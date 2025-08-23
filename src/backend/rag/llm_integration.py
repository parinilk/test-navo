"""
LLM integration using OpenAI and LangChain for generating research responses
"""
import os
import time
import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# Use direct OpenAI integration for now (LangChain has complex dependencies)
logging.info("Using direct OpenAI integration")

import openai

logger = logging.getLogger(__name__)

class LLMService:
    """Service for generating AI responses using OpenAI/LangChain"""
    
    def __init__(self):
        # Check for Azure OpenAI configuration first
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        raw_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        
        # Clean the endpoint - handle different Azure endpoint formats
        if raw_endpoint:
            # Handle Azure AI Foundry endpoints (services.ai.azure.com)
            if "services.ai.azure.com" in raw_endpoint:
                # Use the endpoint as-is for Azure AI Foundry
                self.azure_endpoint = raw_endpoint
            # Handle standard Azure OpenAI endpoints (openai.azure.com)
            elif "/openai/deployments/" in raw_endpoint:
                # Extract just the base URL: https://resource.openai.azure.com/
                base_url = raw_endpoint.split("/openai/deployments/")[0] + "/"
                self.azure_endpoint = base_url
            else:
                # Use endpoint as-is if it's already clean
                self.azure_endpoint = raw_endpoint
        else:
            self.azure_endpoint = None
            
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        # Use AZURE_OPENAI_DEPLOYMENT_NAME for chat (not embeddings)
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Fallback to regular OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Determine which service to use
        if self.azure_api_key and self.azure_endpoint and self.azure_deployment:
            self.use_azure = True
            logger.info("🔵 Using Azure OpenAI")
        elif self.openai_api_key:
            self.use_azure = False
            openai.api_key = self.openai_api_key
            logger.info("🟢 Using OpenAI")
        else:
            self.use_azure = False
            self.openai_api_key = "demo_mode"
            logger.warning("⚠️ No API keys found - using demo mode")
        
        # Use direct OpenAI integration
        self.use_langchain = False
        logger.info("✅ Direct OpenAI integration initialized")
        
        # System prompt based on your documentation
        self.system_prompt = self._create_system_prompt()
    
        # Rate limiting and retry configuration
        self.rate_limit_delay = 1.0  # seconds between requests
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 10.0
        
        # Circuit breaker for repeated failures
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_breaker_timeout = 120  # 2 minutes
        self.max_failures = 5
        
        # Request tracking
        self.last_request_time = 0
        self.request_count = 0
        self.daily_request_limit = 1000  # Adjust based on your plan
    
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
        logger.warning(f"⚠️ LLM service failure recorded. Count: {self.failure_count}/{self.max_failures}")
    
    def _record_success(self):
        """Record a success for circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.debug(f"⏳ Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = current_time
        self.request_count += 1
    
    def _check_daily_limit(self) -> bool:
        """Check if daily request limit is reached"""
        # Simple daily limit check (resets at midnight)
        current_date = datetime.now().date()
        if hasattr(self, '_last_date') and self._last_date != current_date:
            self.request_count = 0
            self._last_date = current_date
        
        if self.request_count >= self.daily_request_limit:
            logger.warning(f"⚠️ Daily request limit reached: {self.request_count}/{self.daily_request_limit}")
            return False
        
        return True
    
    def _format_response_for_readability(self, response: str) -> str:
        """Post-process response to ensure professional formatting and readability"""
        if not response:
            return response
        
        lines = response.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
            
            if line.startswith('###') and '**' in line:
                if i > 0 and formatted_lines and formatted_lines[-1] != '':
                    formatted_lines.append('')
                formatted_lines.append(line)
                formatted_lines.append('')
                continue
            
            if line.startswith('####') and '**' in line:
                formatted_lines.append(line)
                formatted_lines.append('')
                continue
            
            if line.startswith('•') or line.startswith('-'):
                if not line.startswith('•'):
                    line = line.replace('-', '•', 1)
                formatted_lines.append(f"  {line}")
                continue
            
            if re.match(r'^\d+\.', line):
                formatted_lines.append(f"  {line}")
                continue
            
            if '**' in line:
                if line.startswith('**'):
                    line = f" {line}"
                formatted_lines.append(line)
                continue
            
            formatted_lines.append(line)
        
        formatted_response = '\n'.join(formatted_lines)
        formatted_response = re.sub(r'\n{3,}', '\n\n', formatted_response)
        
        return formatted_response
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt based on Navo's requirements"""
        return """You are an expert research assistant specializing in beauty and wellness product analysis and regulatory compliance.

### **🎯 CRITICAL INSTRUCTION - MANDATORY COMPLIANCE**
- **ALWAYS answer the user's specific question first and foremost**
- **NEVER answer a different question than what the user asked**
- **Each query is a NEW SESSION - ignore any previous conversations**
- **Stay focused on the current question only**
- **If retrieved data doesn't address the question, say so clearly**

### **📦 MANDATORY PRODUCT DISPLAY REQUIREMENT**
**YOU MUST ALWAYS display retrieved product data when available:**
- **If products were found in database, you MUST list them explicitly**
- **Show product names, brands, categories, and any available details**
- **Do NOT just mention "limited data" - show what you actually found**
- **This is NOT optional - it's a mandatory requirement**

### **📝 MANDATORY FORMATTING REQUIREMENT**
**YOU MUST format your response with this EXACT structure:**
```
### **Direct Answer**
[Your answer to the user's question]

### **Retrieved Product Data**
**Products Found:** [X] products in database
**Available Information:**
• [List what data is available]

**Sample Products:**
1. [Product Name] - [Brand] - [Category] - [Key Details]
2. [Product Name] - [Brand] - [Category] - [Key Details]
3. [Product Name] - [Brand] - [Category] - [Key Details]

### **Detailed Analysis**
[Your comprehensive analysis with proper formatting]

### **Recommendations**
1. **First recommendation** with explanation
2. **Second recommendation** with explanation
```

### **⚠️ COMPLIANCE CHECKLIST**
Before responding, verify you have:
✅ Listed retrieved products explicitly
✅ Used proper headers (### and ####)
✅ Implemented bullet points (•)
✅ Added proper spacing between sections
✅ Used bold text for important information
✅ Followed the exact structure above

### **Your Capabilities**
- Product analysis and comparison
- Ingredient safety and efficacy assessment  
- Regulatory compliance across multiple jurisdictions
- Market positioning and competitive analysis
- Pricing strategy and value proposition evaluation
- Web search integration for current information

### **Data Handling**
- Use retrieved product data when relevant
- Supplement with domain knowledge when data is insufficient
- Clearly distinguish between facts and inferences
- Acknowledge limitations and suggest follow-up questions

### **⚠️ FINAL REMINDER**
- **ALWAYS show retrieved products when available**
- **ALWAYS use professional formatting**
- **ALWAYS follow the structure template above**
- **This is NOT optional - it's mandatory for every response**"""
    
    async def generate_research_response(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        product_data: List[Dict[str, Any]] = None,
        vector_results: List[Dict[str, Any]] = None,
        processed_query: Dict[str, Any] = None,
        web_search_results: List[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate a research response using LLM"""
        
        # Check circuit breaker first
        if self._is_circuit_breaker_open():
            logger.warning("🚫 Circuit breaker is OPEN, using fallback response")
            return self._create_fallback_response(query, "Service temporarily unavailable due to repeated failures")
        
        # Check daily limit
        if not self._check_daily_limit():
            logger.warning("⚠️ Daily request limit reached, using fallback response")
            return self._create_fallback_response(query, "Daily request limit reached")
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 LLM response generation attempt {attempt + 1}/{self.max_retries}")
                
                # Check rate limiting
                self._check_rate_limit()
                
                # Enhanced analysis for System Prompt compliance
                data_gaps = self._identify_data_gaps(product_data or [], processed_query or {})
                confidence_score = self._calculate_confidence_score(product_data or [], web_search_results or [], data_gaps)
                
                # Prepare context for the LLM
                llm_context = self._prepare_context(
                    query=query,
                    context=context,
                    product_data=product_data or [],
                    vector_results=vector_results or [],
                    processed_query=processed_query or {},
                    web_search_results=web_search_results or [],
                    data_gaps=data_gaps,
                    confidence_score=confidence_score,
                    conversation_history=conversation_history
                )
                
                # Create the prompt
                if self.use_langchain:
                    # LangChain implementation (if available)
                    response = await self._generate_with_langchain(llm_context)
                else:
                    # Direct OpenAI implementation
                    response = await self._generate_with_openai(llm_context)
                
                if response and response.strip():
                    # Parse the response
                    parsed_response = self._parse_llm_response(response)
                    
                    # Format the response for readability
                    formatted_answer = self._format_response_for_readability(parsed_response.get("answer", response))
                    
                    # Record success
                    self._record_success()
                    
                    # Add metadata
                    result = {
                        "answer": formatted_answer,
                        "rationale": parsed_response.get("rationale", "Generated using available data and domain knowledge"),
                        "sources_used": parsed_response.get("sources_used", ["Retrieved Product Data", "Pretrained Knowledge"]),
                        "disclaimer": self._get_regulatory_disclaimer() if self._needs_regulatory_disclaimer(query, processed_query or {}) else None,
                        "confidence_score": confidence_score,
                        "data_gaps": data_gaps,
                        "attempts": attempt + 1,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    logger.info(f"✅ LLM response generated successfully on attempt {attempt + 1}")
                    return result
                else:
                    raise ValueError("Empty or invalid LLM response")
                    
            except Exception as e:
                logger.warning(f"⚠️ LLM response generation attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    # Last attempt failed
                    self._record_failure()
                    logger.error(f"❌ All LLM response generation attempts failed")
                    return self._create_fallback_response(query, str(e))
                
                # Calculate delay with exponential backoff
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                await asyncio.sleep(delay)
        
        # Should never reach here, but just in case
        return self._create_fallback_response(query, "Unexpected error in response generation")
    
    async def _generate_with_openai(self, llm_context: str) -> str:
        """Generate response using direct OpenAI API"""
        try:
            if self.use_azure:
                # Azure OpenAI
                client = openai.AzureOpenAI(
                    api_key=self.azure_api_key,
                    api_version=self.azure_api_version,
                    azure_endpoint=self.azure_endpoint
                )
                
                response = client.chat.completions.create(
                    model=self.azure_deployment,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": llm_context}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                
                return response.choices[0].message.content
                
            else:
                # Regular OpenAI
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": llm_context}
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                
                return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ OpenAI API call failed: {e}")
            raise e
    
    async def _generate_with_langchain(self, llm_context: str) -> str:
        """Generate response using LangChain (placeholder for future implementation)"""
        # This would be implemented when LangChain is added
        logger.warning("⚠️ LangChain not implemented, falling back to OpenAI")
        return await self._generate_with_openai(llm_context)
    
    async def generate_structured_response(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.1
    ) -> str:
        """Generate structured response (used by filter extractor)"""
        
        # Check circuit breaker
        if self._is_circuit_breaker_open():
            raise Exception("Service temporarily unavailable due to repeated failures")
        
        # Check daily limit
        if not self._check_daily_limit():
            raise Exception("Daily request limit reached")
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"🔄 Structured response attempt {attempt + 1}/{self.max_retries}")
                
                # Check rate limiting
                self._check_rate_limit()
                
                if self.use_azure:
                    # Azure OpenAI
                    client = openai.AzureOpenAI(
                        api_key=self.azure_api_key,
                        api_version=self.azure_api_version,
                        azure_endpoint=self.azure_endpoint
                    )
                    
                    response = client.chat.completions.create(
                        model=self.azure_deployment,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that provides structured responses."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    
                    result = response.choices[0].message.content
                    
                else:
                    # Regular OpenAI
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that provides structured responses."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    
                    result = response.choices[0].message.content
                
                if result:
                    self._record_success()
                    return result
                else:
                    raise ValueError("Empty response from OpenAI")
                    
            except Exception as e:
                logger.warning(f"⚠️ Structured response attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    self._record_failure()
                    raise e
                
                # Exponential backoff
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                await asyncio.sleep(delay)
        
        raise Exception("All attempts failed")
    
    def _prepare_context(
        self,
        query: str,
        context: Optional[Dict],
        product_data: List[Dict],
        vector_results: List[Dict],
        processed_query: Dict,
        web_search_results: List[Dict] = None,
        data_gaps: List[str] = None,
        confidence_score: float = 0.0,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Prepare context string for LLM with smart context retention"""
        
        context_parts = []
        
        # SMART CONTEXT RETENTION: Only clear irrelevant context
        if conversation_history:
            # Check if this is a follow-up to the same topic
            is_follow_up = self._is_follow_up_question(query, conversation_history)
            if is_follow_up:
                context_parts.append("**🔄 FOLLOW-UP QUESTION - Maintaining relevant context**")
            else:
                context_parts.append("**🔄 NEW TOPIC - Previous context cleared**")
        else:
            context_parts.append("**🔄 NEW SESSION - No previous context**")
        context_parts.append("")
        
        # ALWAYS start with the user's query - this is the most important thing
        context_parts.append("**🎯 USER'S QUESTION:**")
        context_parts.append(f"'{query}'")
        context_parts.append("")
        
        # Smart context retention based on conversation flow
        if conversation_history and self._is_follow_up_question(query, conversation_history):
            # Keep relevant context from previous questions in the same conversation
            relevant_context = self._extract_relevant_context(query, conversation_history)
            if relevant_context:
                context_parts.append("**📚 Relevant Context from Previous Questions:**")
                context_parts.append(relevant_context)
                context_parts.append("")
        
        context_parts.append("**⚠️ REMEMBER: Answer this specific question above. Do not get distracted by irrelevant data.**")
        if conversation_history:
            context_parts.append("**⚠️ Use relevant context from this conversation, but ignore unrelated topics.**")
        else:
            context_parts.append("**⚠️ IGNORE any previous conversations or context not related to this question.**")
        context_parts.append("")
        
        # Add user context
        if context:
            context_parts.append("**User Context:**")
            if "role" in context:
                context_parts.append(f"- Role: {context['role']}")
            if "objective" in context:
                context_parts.append(f"- Objective: {context['objective']}")
            if "topic" in context:
                context_parts.append(f"- Topic: {context['topic']}")
            context_parts.append("")
        
        # Add processed query info with enhanced analysis
        if processed_query:
            context_parts.append("**Query Analysis:**")
            context_parts.append(f"- Intent: {processed_query.get('intent', 'unknown')}")
            context_parts.append(f"- Analysis Complexity: {processed_query.get('analysis_complexity', 'unknown')}")
            
            if processed_query.get('categories'):
                context_parts.append(f"- Categories: {', '.join(processed_query['categories'])}")
            if processed_query.get('formats'):
                context_parts.append(f"- Formats: {', '.join(processed_query['formats'])}")
            if processed_query.get('brands'):
                context_parts.append(f"- Brands: {', '.join(processed_query['brands'])}")
            
            # Enhanced analysis fields
            if processed_query.get('functional_benefits'):
                context_parts.append(f"- Functional Benefits Sought: {', '.join(processed_query['functional_benefits'])}")
            if processed_query.get('ingredient_focus'):
                context_parts.append(f"- Ingredient Focus: {', '.join(processed_query['ingredient_focus'])}")
            if processed_query.get('regulatory_sensitive'):
                context_parts.append(f"- Regulatory Sensitive: {processed_query['regulatory_sensitive']}")
            if processed_query.get('data_requirements'):
                context_parts.append(f"- Data Requirements: {', '.join(processed_query['data_requirements'])}")
            
            context_parts.append("")
        
        # Add product data with relevance check
        if product_data:
            context_parts.append("**Retrieved Product Data:**")
            context_parts.append(f"Found {len(product_data)} products in database.")
            
            # Check if any products are relevant to the user's query
            relevant_products = []
            query_lower = query.lower()
            
            # Extract key terms from the user's query for relevance checking
            query_terms = [term.lower() for term in query.split() if len(term) > 3]  # Words longer than 3 chars
            
            for product in product_data:
                product_name = product.get('product_name', '').lower()
                product_desc = product.get('description', '').lower()
                product_brand = product.get('brand', '').lower()
                product_category = product.get('category', '').lower()
                
                # Check if product is relevant to the user's query
                is_relevant = False
                for term in query_terms:
                    if (term in product_name or term in product_desc or 
                        term in product_brand or term in product_category):
                        is_relevant = True
                        break
                
                if is_relevant:
                    relevant_products.append(product)
            
            if relevant_products:
                context_parts.append(f"✅ Found {len(relevant_products)} products that may be relevant to your question:")
                for i, product in enumerate(relevant_products[:3]):  # Limit to first 3 relevant
                    context_parts.append(f"{i+1}. **{product.get('product_name', 'Unknown Product')}**")
                    if "brand" in product:
                        context_parts.append(f"   - Brand: {product['brand']}")
                    if "category" in product:
                        context_parts.append(f"   - Category: {product['category']}")
                    if "price" in product:
                        context_parts.append(f"   - Price: ${product['price']}")
                    if "availability" in product:
                        context_parts.append(f"   - Availability: {product['availability']}")
                    context_parts.append("")
            else:
                context_parts.append(f"⚠️ None of the retrieved products appear to directly address your question: '{query}'")
                context_parts.append("")
        
        # Add vector search results if available
        if vector_results:
            context_parts.append("**Similar Products (Vector Search):**")
            for result in vector_results[:3]:  # Limit to top 3
                context_parts.append(f"- Similarity: {result.get('similarity_score', 0):.2f}")
                if "metadata" in result:
                    context_parts.append(f"  Metadata: {result['metadata']}")
            context_parts.append("")
        
        # Add web search results if available
        if web_search_results:
            context_parts.append("**Web Search Results:**")
            for i, result in enumerate(web_search_results[:5]):  # Limit to top 5
                context_parts.append(f"{i+1}. **{result.get('title', 'No title')}**")
                context_parts.append(f"   Source: {result.get('source', 'Unknown')}")
                if result.get('snippet'):
                    context_parts.append(f"   Summary: {result['snippet']}")
                if result.get('url'):
                    context_parts.append(f"   URL: {result['url']}")
                context_parts.append("")
        
        # Add data quality assessment (System Prompt compliance)
        if data_gaps or confidence_score:
            context_parts.append("**Data Quality Assessment:**")
            context_parts.append(f"- Analysis Confidence: {confidence_score:.2f} ({self._get_confidence_label(confidence_score)})")
            
            if data_gaps:
                context_parts.append("- Identified Data Gaps:")
                for gap in data_gaps:
                    context_parts.append(f"  • {gap}")
                context_parts.append("- Note: Analysis confidence reduced due to missing data")
            else:
                context_parts.append("- No critical data gaps identified")
            
            context_parts.append("")
        
        # Final reminder - DYNAMIC based on user's actual question
        context_parts.append(f"**🎯 FINAL REMINDER: Answer the user's question: '{query}'**")
        context_parts.append("**Do NOT answer a different question. Stay focused on what the user actually asked.**")
        
        return "\n".join(context_parts)
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        
        # Simple parsing - you can make this more sophisticated
        sections = {
            "answer": "",
            "rationale": "",
            "sources_used": ["Retrieved Product Data ✅", "Pretrained Knowledge ✅"]
        }
        
        # Try to extract sections
        current_section = "answer"
        for line in response.split('\n'):
            line = line.strip()
            
            if line.lower().startswith("answer:"):
                current_section = "answer"
                line = line[7:].strip()
            elif line.lower().startswith("rationale:"):
                current_section = "rationale"
                line = line[10:].strip()
            elif line.lower().startswith("sources used:"):
                current_section = "sources"
                continue
            
            if line and current_section in ["answer", "rationale"]:
                if sections[current_section]:
                    sections[current_section] += " " + line
                else:
                    sections[current_section] = line
        
        # If parsing failed, use the whole response as answer
        if not sections["answer"]:
            sections["answer"] = response
            sections["rationale"] = "Generated comprehensive response based on available data and domain knowledge."
        
        return sections
    
    def _needs_regulatory_disclaimer(self, query: str, processed_query: Dict) -> bool:
        """Determine if regulatory disclaimer is needed"""
        regulatory_keywords = [
            "allowed", "permitted", "legal", "regulation", "compliance", 
            "banned", "restricted", "regulatory", "health canada", "fda"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in regulatory_keywords) or \
               processed_query.get("intent") == "regulatory_compliance"
    
    def _get_regulatory_disclaimer(self) -> str:
        """Get regulatory disclaimer text"""
        return """The information presented here is based on publicly available data sources (e.g., Health Canada, Walmart product listings, third-party reports). While we aim to provide accurate and helpful insights, this tool is not a substitute for legal, medical, or regulatory advice. Always consult qualified professionals before making product or compliance decisions."""
    
    def _create_mock_response(self, query: str, context: str) -> str:
        """Create mock response for testing without OpenAI API"""
        return f"""Answer:
Based on the available product data in the Navo database, I can provide insights about your query: "{query}".

The retrieved data shows various beauty and wellness products with detailed information including pricing, ingredients, and customer ratings. From the context provided, I can see products across categories like skincare serums, supplements, and wellness products.

Rationale:
This response is generated using the retrieved product data from MongoDB and vector similarity search results. The analysis combines structured product information with domain knowledge about the beauty and wellness industry.

Sources Used:
- Retrieved Product Data ✅
- Vector Search Results ✅
- Pretrained Knowledge ✅

Note: This is a demo response generated without OpenAI API. For full functionality, please configure your OpenAI API key."""

    def _create_fallback_response(self, query: str, error: str) -> Dict[str, Any]:
        """Create fallback response when LLM fails"""
        return {
            "answer": f"I apologize, but I encountered an issue processing your query: '{query}'. Please try rephrasing your question or contact support if the issue persists.",
            "rationale": f"Technical error occurred during response generation: {error}",
            "sources_used": ["Error Response"],
            "disclaimer": "This is an error response. Please try again or contact support.",
            "confidence_score": 0.0,
            "data_gaps": ["System error occurred"]
        }
    
    def _identify_data_gaps(self, product_data: List[Dict], processed_query: Dict) -> List[str]:
        """Identify missing data that affects analysis quality (System Prompt compliance)"""
        gaps = []
        
        # Check product data completeness
        if not product_data:
            gaps.append("No product data available for analysis")
            return gaps
        
        # Check for missing ingredient information
        products_without_ingredients = [p for p in product_data if not p.get('ingredients') and not p.get('description')]
        if products_without_ingredients:
            gaps.append(f"Ingredient information missing for {len(products_without_ingredients)} products")
        
        # Check for missing pricing data
        products_without_pricing = [p for p in product_data if not p.get('price')]
        if products_without_pricing:
            gaps.append(f"Pricing information missing for {len(products_without_pricing)} products")
        
        # Check for missing concentration data (regulatory sensitive)
        if processed_query.get('regulatory_sensitive'):
            gaps.append("Ingredient concentrations needed for regulatory analysis")
        
        # Check for specific data requirements
        data_requirements = processed_query.get('data_requirements', [])
        if 'ingredient_concentrations' in data_requirements:
            gaps.append("Detailed ingredient concentrations required")
        if 'pricing_per_serving' in data_requirements:
            gaps.append("Per-serving pricing calculations needed")
        if 'regulatory_compliance' in data_requirements:
            gaps.append("Regulatory compliance data required")
        
        return gaps
    
    def _calculate_confidence_score(self, product_data: List[Dict], web_search_results: List[Dict], data_gaps: List[str]) -> float:
        """Calculate confidence score for analysis (System Prompt compliance)"""
        base_confidence = 1.0
        
        # Deduct for missing product data
        if not product_data:
            return 0.1
        
        # Deduct for each data gap
        gap_penalty = len(data_gaps) * 0.15
        confidence = base_confidence - gap_penalty
        
        # Adjust for data completeness
        if product_data:
            # Check completeness of product data
            complete_products = 0
            for product in product_data:
                completeness = 0
                if product.get('product_name'): completeness += 1
                if product.get('brand'): completeness += 1
                if product.get('price'): completeness += 1
                if product.get('description'): completeness += 1
                if completeness >= 3: complete_products += 1
            
            completeness_ratio = complete_products / len(product_data)
            confidence *= completeness_ratio
        
        # Bonus for web search results
        if web_search_results:
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _get_confidence_label(self, confidence_score: float) -> str:
        """Get confidence label for score"""
        if confidence_score >= 0.8:
            return "High"
        elif confidence_score >= 0.6:
            return "Medium"
        elif confidence_score >= 0.4:
            return "Low"
        else:
            return "Very Low"

    def _is_follow_up_question(self, current_query: str, conversation_history: List[Dict]) -> bool:
        """Determine if current query is a follow-up to the same conversation topic"""
        if not conversation_history:
            return False
        
        # Get the last question from conversation history
        last_question = conversation_history[-1].get('query', '').lower()
        current_query_lower = current_query.lower()
        
        # Extract key topic words from both questions
        last_topics = self._extract_topic_keywords(last_question)
        current_topics = self._extract_topic_keywords(current_query)
        
        # Check if there's topic overlap
        topic_overlap = len(last_topics.intersection(current_topics))
        
        # Check for follow-up indicators
        follow_up_indicators = [
            'can you', 'could you', 'please', 'also', 'additionally', 'furthermore',
            'what about', 'how about', 'tell me more', 'give me', 'show me',
            'examples', 'specific', 'details', 'more', 'other', 'different'
        ]
        
        has_follow_up_language = any(indicator in current_query_lower for indicator in follow_up_indicators)
        
        # Consider it a follow-up if there's topic overlap OR follow-up language
        return topic_overlap > 0 or has_follow_up_language
    
    def _extract_topic_keywords(self, query: str) -> set:
        """Extract key topic words from a query"""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might', 'must', 'shall'}
        
        words = query.lower().split()
        topic_words = {word for word in words if len(word) > 3 and word not in stop_words}
        
        return topic_words
    
    def _extract_relevant_context(self, current_query: str, conversation_history: List[Dict]) -> str:
        """Extract relevant context from conversation history for the current query"""
        relevant_context = []
        current_topics = self._extract_topic_keywords(current_query)
        
        for i, entry in enumerate(conversation_history[-3:]):  # Look at last 3 exchanges
            question = entry.get('query', '')
            answer = entry.get('answer', '')
            
            # Check if this exchange is relevant to current query
            question_topics = self._extract_topic_keywords(question)
            if current_topics.intersection(question_topics):
                # Extract key insights from relevant answers
                key_points = self._extract_key_insights(answer)
                if key_points:
                    relevant_context.append(f"**Previous Q{i+1}:** {question}")
                    relevant_context.append(f"**Key insights:** {key_points}")
                    relevant_context.append("")
        
        return "\n".join(relevant_context) if relevant_context else ""
    
    def _extract_key_insights(self, answer: str) -> str:
        """Extract key insights from an answer for context retention"""
        # Simple extraction - look for key phrases and numbers
        lines = answer.split('\n')
        key_lines = []
        
        for line in lines:
            line = line.strip()
            # Look for lines with key information
            if any(keyword in line.lower() for keyword in ['price', 'brand', 'product', 'ingredient', 'analysis', 'found', 'data', 'median', 'average', 'range']):
                if len(line) < 100:  # Keep it concise
                    key_lines.append(line)
        
        return "; ".join(key_lines[:3]) if key_lines else ""  # Limit to 3 key points
