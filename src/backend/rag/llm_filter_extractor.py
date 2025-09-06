
import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMFilterExtractor:
    
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1.0  # seconds
        self.max_delay = 10.0  # seconds
        
        # Circuit breaker configuration
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_breaker_timeout = 60  # seconds
        self.max_failures = 5
        
        # System prompt for filter extraction
        self.filter_extraction_prompt = """
You are a specialized filter extraction system for a beauty and wellness product database.

Your task is to analyze user queries and extract structured filters in JSON format.

Available filter categories:

**Tier 1 - Product Level:**
- format: Powder, Capsule, Gummy, Beverage, Cream, Serum, Liquid, Tablet
- primary_benefit: Skin Health, Joint Support, Hair/Nails, General Wellness, Anti-Aging, Hydration, Energy
- price_range: Under $20, $20-$40, $40-$60, Over $60
- brand: Any brand name mentioned
- sales_channel: Amazon, Walmart, DTC, In-Store
- pack_size: Number + unit (e.g., "30 ct", "60 capsules")

**Tier 2 - Ingredient Level:**
- ingredient_name: Specific ingredients (retinol, collagen, biotin, etc.)
- ingredient_form: Marine Collagen, Bovine Collagen, Type I/II/III, Hydrolyzed
- usage_context: Rinse-off, Leave-On, Ingestible, Topical
- jurisdiction: USA, Canada, EU, California, UK
- max_amount: Maximum concentration if mentioned

**Tier 3 - Claim/Positioning Level:**
- claim_category: Beauty, Anti-aging, Joint Flexibility, Gut Health, Energy, Immune
- claim_format: "Supports...", "Clinically Tested", "Made with...", "Natural"
- target_demographic: Women, Men, Athletes, 40+, Pregnant, Seniors, Teens
- lifestyle: Vegan, Vegetarian, Keto, Paleo, Organic

**Examples:**

Query: "What are the most affordable collagen powders for skin health?"
Output: {"format": "Powder", "primary_benefit": "Skin Health", "price_range": "Under $20", "ingredient_name": ["collagen"]}

Query: "Is retinol allowed in skincare in Canada?"
Output: {"ingredient_name": ["retinol"], "usage_context": "Leave-On", "jurisdiction": "Canada"}

Query: "Best marine collagen gummies for women over 40"
Output: {"format": "Gummy", "ingredient_form": "Marine Collagen", "target_demographic": ["Women", "40+"], "ingredient_name": ["collagen"]}

Query: "Compare prices for collagen powders under $40"
Output: {"format": "Powder", "price_range": "Under $40", "ingredient_name": ["collagen"]}

**Instructions:**
1. Extract only filters that are explicitly mentioned or clearly implied
2. Use exact values from the available options above
3. Return valid JSON only
4. If no filters are found, return {}
5. For lists (like ingredient_name, target_demographic), use arrays
6. Be conservative - don't over-extract filters that aren't clearly indicated

Analyze this query and extract filters:
"""
        
        # Validation schema for extracted filters
        self.valid_filters = {
            "tier_1": {
                "format": ["Powder", "Capsule", "Gummy", "Beverage", "Cream", "Serum", "Liquid", "Tablet"],
                "primary_benefit": ["Skin Health", "Joint Support", "Hair/Nails", "General Wellness", "Anti-Aging", "Hydration", "Energy"],
                "price_range": ["Under $20", "$20-$40", "$40-$60", "Over $60"],
                "sales_channel": ["Amazon", "Walmart", "DTC", "In-Store"]
            },
            "tier_2": {
                "ingredient_form": ["Marine Collagen", "Bovine Collagen", "Type I", "Type II", "Type III", "Hydrolyzed"],
                "usage_context": ["Rinse-off", "Leave-On", "Ingestible", "Topical"],
                "jurisdiction": ["USA", "Canada", "EU", "California", "UK"]
            },
            "tier_3": {
                "claim_category": ["Beauty", "Anti-aging", "Joint Flexibility", "Gut Health", "Energy", "Immune"],
                "claim_format": ["Supports", "Clinically Tested", "Made with", "Natural"],
                "target_demographic": ["Women", "Men", "Athletes", "40+", "Pregnant", "Seniors", "Teens"],
                "lifestyle": ["Vegan", "Vegetarian", "Keto", "Paleo", "Organic"]
            }
        }
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.failure_count >= self.max_failures:
            if self.last_failure_time and (time.time() - self.last_failure_time) < self.circuit_breaker_timeout:
                return True
            else:
                # Reset circuit breaker after timeout
                self.failure_count = 0
                self.last_failure_time = None
        return False
    
    def _record_failure(self):
        """Record a failure for circuit breaker"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.warning(f"⚠️ LLM extraction failure recorded. Count: {self.failure_count}/{self.max_failures}")
    
    def _record_success(self):
        """Record a success for circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
    
    async def extract_filters_with_llm(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract filters using LLM preprocessing as specified in RAG Filters.md
        
        Args:
            query: User query string
            context: Optional context information
            
        Returns:
            Dict containing extracted filters and metadata
        """
        logger.info(f"🤖 Extracting filters with LLM for: '{query[:50]}...'")
        
        # Check circuit breaker first
        if self._is_circuit_breaker_open():
            logger.warning("🚫 Circuit breaker is OPEN, using fallback extraction")
            return await self._fallback_extraction(query, context)
        
        if not self.llm_service:
            logger.warning("⚠️ LLM service not available, falling back to rule-based extraction")
            return await self._fallback_extraction(query, context)
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 LLM extraction attempt {attempt + 1}/{self.max_retries}")
                
                # Prepare context for LLM
                context_str = ""
                if context:
                    context_items = []
                    if context.get('role'):
                        context_items.append(f"User role: {context['role']}")
                    if context.get('objective'):
                        context_items.append(f"Objective: {context['objective']}")
                    if context_items:
                        context_str = f"\nContext: {', '.join(context_items)}"
                
                # Construct full prompt
                full_prompt = f"{self.filter_extraction_prompt}\n\nQuery: \"{query}\"{context_str}"
                
                # Call LLM service
                response = await self.llm_service.generate_structured_response(
                    prompt=full_prompt,
                    max_tokens=500,
                    temperature=0.1  # Low temperature for consistent extraction
                )
                
                # Parse JSON response with multiple strategies
                extracted_filters = self._robust_parse_llm_response(response)
                
                if extracted_filters:
                    # Validate and clean filters
                    validated_filters = self._validate_extracted_filters(extracted_filters)
                    
                    # Add metadata
                    result = {
                        "extracted_filters": validated_filters,
                        "extraction_method": "llm",
                        "confidence": self._calculate_extraction_confidence(validated_filters, query),
                        "timestamp": datetime.utcnow().isoformat(),
                        "raw_llm_response": response,
                        "validation_notes": [],
                        "attempts": attempt + 1
                    }
                    
                    # Record success
                    self._record_success()
                    logger.info(f"✅ LLM extracted {len(validated_filters)} filters on attempt {attempt + 1}")
                    return result
                else:
                    raise ValueError("Failed to parse LLM response")
                    
            except Exception as e:
                logger.warning(f"⚠️ LLM extraction attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    # Last attempt failed
                    self._record_failure()
                    logger.error(f"❌ All LLM extraction attempts failed, falling back to rule-based")
                    return await self._fallback_extraction(query, context)
                
                # Calculate delay with exponential backoff
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                await asyncio.sleep(delay)
        
        # Should never reach here, but just in case
        return await self._fallback_extraction(query, context)
    
    def _robust_parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Robust parsing of LLM response with multiple fallback strategies"""
        if not response or not isinstance(response, str):
            logger.warning("⚠️ Empty or invalid LLM response")
            return {}
        
        # Strategy 1: Try to extract JSON with markdown code blocks
        try:
            cleaned = self._extract_json_from_markdown(response)
            if cleaned:
                return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Try to find JSON in the response
        try:
            json_match = self._find_json_in_text(response)
            if json_match:
                return json.loads(json_match)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Try to clean and parse the entire response
        try:
            cleaned_response = self._clean_response_for_json(response)
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            pass
        
        # Strategy 4: Try to extract key-value pairs and construct JSON
        try:
            extracted_pairs = self._extract_key_value_pairs(response)
            if extracted_pairs:
                return extracted_pairs
        except Exception:
            pass
        
        logger.warning("⚠️ All JSON parsing strategies failed")
        return {}
    
    def _extract_json_from_markdown(self, response: str) -> Optional[str]:
        """Extract JSON from markdown code blocks"""
        import re
        
        # Look for ```json ... ``` blocks
        json_block_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_block_match:
            return json_block_match.group(1).strip()
        
        # Look for ``` ... ``` blocks (any language)
        code_block_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()
        
        return None
    
    def _find_json_in_text(self, response: str) -> Optional[str]:
        """Find JSON object in text using regex"""
        import re
        
        # Look for JSON object pattern
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        json_match = re.search(json_pattern, response, re.DOTALL)
        
        if json_match:
            return json_match.group()
        
        return None
    
    def _clean_response_for_json(self, response: str) -> str:
        """Clean response text to make it JSON-parseable"""
        import re
        
        # Remove common prefixes/suffixes
        cleaned = response.strip()
        
        # Remove "Answer:" or similar prefixes
        cleaned = re.sub(r'^(Answer|Response|Output):\s*', '', cleaned, flags=re.IGNORECASE)
        
        # Remove trailing explanations
        cleaned = re.sub(r'\n\s*(Rationale|Explanation|Note):.*$', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Ensure it starts and ends with braces
        if not cleaned.startswith('{'):
            # Try to find the start of JSON
            brace_start = cleaned.find('{')
            if brace_start != -1:
                cleaned = cleaned[brace_start:]
        
        if not cleaned.endswith('}'):
            # Try to find the end of JSON
            brace_end = cleaned.rfind('}')
            if brace_end != -1:
                cleaned = cleaned[:brace_end + 1]
        
        return cleaned
    
    def _extract_key_value_pairs(self, response: str) -> Dict[str, Any]:
        """Extract key-value pairs from text and construct JSON"""
        import re
        
        pairs = {}
        
        # Look for patterns like "key: value" or "key = value"
        patterns = [
            r'(\w+):\s*([^,\n]+)',
            r'(\w+)\s*=\s*([^,\n]+)',
            r'"(\w+)":\s*"([^"]+)"'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for key, value in matches:
                key = key.strip().lower()
                value = value.strip()
                
                # Clean up the value
                if value.endswith(','):
                    value = value[:-1]
                
                # Try to convert to appropriate type
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.startswith('$') and value[1:].replace('.', '').isdigit():
                    # Keep price as string
                    pass
                else:
                    # Check if it's a list
                    if ',' in value:
                        value = [v.strip() for v in value.split(',')]
                
                pairs[key] = value
        
        return pairs
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and extract JSON"""
        try:
            # Clean response - remove any markdown formatting
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Try parsing the whole response
                return json.loads(cleaned)
                
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Failed to parse LLM JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            return {}
    
    def _validate_extracted_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted filters against known valid values"""
        validated = {}
        validation_notes = []
        
        for filter_name, filter_value in filters.items():
            # Find which tier this filter belongs to
            tier = None
            valid_values = None
            
            for tier_name, tier_filters in self.valid_filters.items():
                if filter_name in tier_filters:
                    tier = tier_name
                    valid_values = tier_filters[filter_name]
                    break
            
            if tier is None:
                # Allow unknown filters but note them
                validated[filter_name] = filter_value
                validation_notes.append(f"Unknown filter: {filter_name}")
                continue
            
            # Validate filter values
            if isinstance(filter_value, list):
                valid_items = []
                for item in filter_value:
                    if item in valid_values:
                        valid_items.append(item)
                    else:
                        validation_notes.append(f"Invalid value '{item}' for {filter_name}")
                if valid_items:
                    validated[filter_name] = valid_items
            else:
                if filter_value in valid_values:
                    validated[filter_name] = filter_value
                else:
                    validation_notes.append(f"Invalid value '{filter_value}' for {filter_name}")
        
        return validated
    
    def _calculate_extraction_confidence(self, filters: Dict[str, Any], query: str) -> float:
        """Calculate confidence score for extraction quality"""
        if not filters:
            return 0.0
        
        # Base confidence from number of filters
        base_confidence = min(0.5 + (len(filters) * 0.1), 0.9)
        
        # Boost confidence if filters make sense for query
        query_lower = query.lower()
        
        # Check if extracted formats match query
        if "format" in filters:
            format_val = filters["format"].lower()
            if format_val in query_lower:
                base_confidence += 0.1
        
        # Check if price filters match query
        if "price_range" in filters:
            price_keywords = ["price", "cost", "affordable", "cheap", "expensive"]
            if any(keyword in query_lower for keyword in price_keywords):
                base_confidence += 0.1
        
        # Check if ingredients match query
        if "ingredient_name" in filters:
            ingredients = filters["ingredient_name"]
            if isinstance(ingredients, list):
                for ingredient in ingredients:
                    if ingredient.lower() in query_lower:
                        base_confidence += 0.05
            elif ingredients.lower() in query_lower:
                base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    async def _fallback_extraction(self, query: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Fallback to rule-based extraction when LLM is unavailable"""
        from .three_tier_filters import three_tier_filter_extractor
        
        logger.info("🔧 Using fallback rule-based filter extraction")
        
        rule_based_filters = three_tier_filter_extractor.extract_all_filters(query, context)
        
        # Convert to LLM-style format
        flattened_filters = {}
        for tier_name, tier_filters in rule_based_filters.items():
            if tier_name.startswith("tier_"):
                flattened_filters.update(tier_filters)
        
        return {
            "extracted_filters": flattened_filters,
            "extraction_method": "rule_based_fallback",
            "confidence": 0.6,  # Lower confidence for rule-based
            "timestamp": datetime.utcnow().isoformat(),
            "validation_notes": ["Fallback method used - LLM unavailable"]
        }
    
    def format_filters_for_vector_search(self, extracted_filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format extracted filters for use in vector search
        
        Returns filters in format expected by vector search system
        """
        formatted = {
            "product_filters": {},
            "metadata_filters": {},
            "search_constraints": {}
        }
        
        # Map filters to search categories
        for filter_name, filter_value in extracted_filters.items():
            if filter_name in ["format", "primary_benefit", "brand"]:
                formatted["product_filters"][filter_name] = filter_value
            elif filter_name in ["price_range", "pack_size"]:
                formatted["search_constraints"][filter_name] = filter_value
            elif filter_name in ["ingredient_name", "usage_context", "jurisdiction"]:
                formatted["metadata_filters"][filter_name] = filter_value
            else:
                # Default to metadata filters
                formatted["metadata_filters"][filter_name] = filter_value
        
        return formatted
    
    def get_filter_summary(self, extracted_result: Dict[str, Any]) -> str:
        """Generate human-readable summary of extracted filters"""
        filters = extracted_result.get("extracted_filters", {})
        if not filters:
            return "No specific filters extracted from query"
        
        summary_parts = []
        
        # Product-level filters
        if "format" in filters:
            summary_parts.append(f"Format: {filters['format']}")
        if "primary_benefit" in filters:
            summary_parts.append(f"Benefit: {filters['primary_benefit']}")
        if "price_range" in filters:
            summary_parts.append(f"Price: {filters['price_range']}")
        
        # Ingredient filters
        if "ingredient_name" in filters:
            ingredients = filters["ingredient_name"]
            if isinstance(ingredients, list):
                summary_parts.append(f"Ingredients: {', '.join(ingredients)}")
            else:
                summary_parts.append(f"Ingredient: {ingredients}")
        
        # Target demographic
        if "target_demographic" in filters:
            demo = filters["target_demographic"]
            if isinstance(demo, list):
                summary_parts.append(f"Target: {', '.join(demo)}")
            else:
                summary_parts.append(f"Target: {demo}")
        
        confidence = extracted_result.get("confidence", 0)
        method = extracted_result.get("extraction_method", "unknown")
        
        summary = " | ".join(summary_parts)
        return f"{summary} (confidence: {confidence:.1f}, method: {method})"

# Global instance
llm_filter_extractor = LLMFilterExtractor()
