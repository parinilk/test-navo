"""
Clarification Node for RAG Pipeline
Positioned correctly in pipeline as per RAG Filters.md diagram:
User Query → Clarification Node → Intent Router → Filter Extractor → Retriever(s) → Answer Composer
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ClarificationNode:
    """
    Handles query clarification as the first step after user input
    Position: Right after User Query, before Intent Router
    """
    
    def __init__(self):
        # Patterns that typically need clarification
        self.ambiguous_patterns = [
            # Vague quantity words
            r"\b(some|many|few|several|best|good|better)\b",
            # Missing context
            r"\b(products?|ingredients?|brands?)\b(?!\s+\w+)",
            # Unclear comparisons  
            r"\b(compare|vs|versus)\b(?!\s+\w+.*\w+)",
            # Price without range
            r"\b(cheap|expensive|affordable)\b(?!\s+under|\s+over|\s+\$)",
            # Benefits without specifics
            r"\b(good for|helps with|benefits)\b(?!\s+\w+)",
        ]
        
        # Intent-specific clarification triggers
        self.intent_clarifications = {
            "product_search": {
                "missing_format": "What product format are you interested in? (powder, capsule, gummy, etc.)",
                "missing_benefit": "What specific health benefit are you looking for?",
                "missing_price": "What's your budget range?",
                "missing_brand": "Do you have any brand preferences?"
            },
            "regulatory_compliance": {
                "missing_jurisdiction": "Which region/country's regulations? (USA, Canada, EU, etc.)",
                "missing_usage": "How will this ingredient be used? (skincare, supplement, etc.)",
                "missing_ingredient": "Which specific ingredient are you asking about?",
                "missing_context": "Is this for leave-on or rinse-off products?"
            },
            "competitive_analysis": {
                "missing_scope": "What aspect would you like to compare? (price, ingredients, claims, etc.)",
                "missing_category": "What product category should I focus on?",
                "missing_timeframe": "Are you looking for current market data or trends over time?"
            }
        }
        
        # Quality thresholds
        self.clarity_threshold = 0.7  # Below this, suggest clarification
        self.confidence_threshold = 0.6  # Below this, require clarification
        
    def assess_query_clarity(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess if query needs clarification before routing
        
        Returns:
            Dict with clarification assessment and suggestions
        """
        logger.info(f"🤔 Assessing query clarity: '{query[:50]}...'")
        
        assessment = {
            "needs_clarification": False,
            "clarity_score": 1.0,
            "issues": [],
            "suggested_clarifications": [],
            "clarification_type": None,
            "confidence": 1.0
        }
        
        query_lower = query.lower()
        context = context or {}
        
        # Calculate clarity score based on multiple factors
        clarity_factors = self._analyze_clarity_factors(query, context)
        assessment["clarity_score"] = clarity_factors["overall_score"]
        assessment["issues"] = clarity_factors["issues"]
        
        # Determine if clarification is needed
        if clarity_factors["overall_score"] < self.confidence_threshold:
            assessment["needs_clarification"] = True
            assessment["clarification_type"] = "required"
        elif clarity_factors["overall_score"] < self.clarity_threshold:
            assessment["needs_clarification"] = True  
            assessment["clarification_type"] = "suggested"
        
        # Generate specific clarification suggestions
        if assessment["needs_clarification"]:
            assessment["suggested_clarifications"] = self._generate_clarification_suggestions(
                query, context, clarity_factors
            )
        
        assessment["confidence"] = min(clarity_factors["overall_score"], 1.0)
        
        logger.info(f"📊 Clarity assessment: score={assessment['clarity_score']:.2f}, needs_clarification={assessment['needs_clarification']}")
        return assessment
    
    def _analyze_clarity_factors(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze various factors that affect query clarity"""
        factors = {
            "length_score": 0.0,
            "specificity_score": 0.0,
            "context_score": 0.0,
            "intent_clarity_score": 0.0,
            "overall_score": 0.0,
            "issues": []
        }
        
        query_lower = query.lower()
        words = query.split()
        
        # Length factor (too short or too long can be unclear)
        word_count = len(words)
        if word_count < 3:
            factors["length_score"] = 0.3
            factors["issues"].append("Query is very short")
        elif word_count < 6:
            factors["length_score"] = 0.6
            factors["issues"].append("Query could be more specific")
        elif word_count > 20:
            factors["length_score"] = 0.7
            factors["issues"].append("Query is quite long")
        else:
            factors["length_score"] = 1.0
        
        # Specificity factor (presence of specific terms)
        specificity_indicators = [
            "product names", "specific ingredients", "exact prices",
            "brand names", "specific benefits", "jurisdictions"
        ]
        
        specificity_count = 0
        if any(word in query_lower for word in ["retinol", "collagen", "biotin", "vitamin"]):
            specificity_count += 1
        if any(word in query_lower for word in ["powder", "capsule", "gummy", "serum"]):
            specificity_count += 1
        if "$" in query or any(word in query_lower for word in ["under", "over", "between"]):
            specificity_count += 1
        if any(word in query_lower for word in ["canada", "usa", "eu", "california"]):
            specificity_count += 1
        
        factors["specificity_score"] = min(specificity_count / 3.0, 1.0)
        if factors["specificity_score"] < 0.5:
            factors["issues"].append("Query lacks specific details")
        
        # Context factor (user-provided context improves clarity)
        if context:
            context_indicators = ["role", "objective", "category", "target_audience"]
            context_count = sum(1 for key in context_indicators if context.get(key))
            factors["context_score"] = min(context_count / 2.0, 1.0)
        else:
            factors["context_score"] = 0.5
            factors["issues"].append("No additional context provided")
        
        # Intent clarity (how clear the intent is)
        intent_keywords = {
            "product_search": ["product", "brand", "compare", "best", "recommend"],
            "regulatory": ["allowed", "legal", "regulation", "compliance", "banned"],
            "pricing": ["price", "cost", "expensive", "cheap", "budget"],
            "formulation": ["formulate", "develop", "create", "ingredient"]
        }
        
        intent_scores = []
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            intent_scores.append(score)
        
        max_intent_score = max(intent_scores) if intent_scores else 0
        factors["intent_clarity_score"] = min(max_intent_score / 3.0, 1.0)
        
        if factors["intent_clarity_score"] < 0.5:
            factors["issues"].append("Query intent is unclear")
        
        # Calculate overall score
        factors["overall_score"] = (
            factors["length_score"] * 0.2 +
            factors["specificity_score"] * 0.4 +
            factors["context_score"] * 0.2 +
            factors["intent_clarity_score"] * 0.2
        )
        
        return factors
    
    def _generate_clarification_suggestions(
        self, 
        query: str, 
        context: Dict[str, Any],
        clarity_factors: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate specific clarification suggestions based on issues"""
        suggestions = []
        issues = clarity_factors["issues"]
        query_lower = query.lower()
        
        # Beauty/Wellness industry-specific clarifications
        if "Query is very short" in issues:
            suggestions.append({
                "question": "Could you provide more details about what you're looking for?",
                "example": "Instead of 'collagen', try 'best collagen powder for skin health under $30'",
                "domain_context": "This helps me find the most relevant products and regulatory information for your needs."
            })
        
        if "Query lacks specific details" in issues:
            # Product format clarifications
            if any(word in query_lower for word in ["product", "supplement", "skincare", "beauty"]):
                suggestions.append({
                    "question": "What product format are you interested in?",
                    "options": ["Powder", "Capsule", "Gummy", "Liquid", "Cream", "Serum", "Tablet"],
                    "domain_context": "Different formats have different absorption rates and regulatory considerations."
                })
            
            # Price range clarifications
            if any(word in query_lower for word in ["price", "cost", "affordable", "cheap", "expensive"]):
                suggestions.append({
                    "question": "What's your budget range?",
                    "options": ["Under $20", "$20-$40", "$40-$60", "Over $60"],
                    "domain_context": "This helps me find products within your budget and identify price positioning opportunities."
                })
            
            # Ingredient-specific clarifications
            if any(word in query_lower for word in ["collagen", "retinol", "vitamin", "peptide"]):
                suggestions.append({
                    "question": "What specific ingredient form are you looking for?",
                    "options": ["Marine Collagen", "Bovine Collagen", "Type I/II/III", "Hydrolyzed", "Natural", "Synthetic"],
                    "domain_context": "Different forms have different efficacy and regulatory status."
                })
            
            # Benefit clarifications
            if any(word in query_lower for word in ["benefit", "help", "good for", "treat"]):
                suggestions.append({
                    "question": "What specific health benefit are you targeting?",
                    "options": ["Skin Health", "Joint Support", "Hair/Nails", "Anti-Aging", "Hydration", "Energy"],
                    "domain_context": "This helps me match you with the most effective ingredients and products."
                })
        
        if "Query intent is unclear" in issues:
            suggestions.append({
                "question": "What would you like to know?",
                "options": [
                    "Find products", 
                    "Check regulations", 
                    "Compare options",
                    "Get formulation advice",
                    "Market analysis",
                    "Competitive research"
                ],
                "domain_context": "Understanding your goal helps me provide the most relevant information and analysis."
            })
        
        # Regulatory-specific clarifications
        if any(word in query_lower for word in ["allowed", "legal", "regulation", "compliance"]):
            if not any(region in query_lower for region in ["canada", "usa", "eu", "california", "uk"]):
                suggestions.append({
                    "question": "Which region's regulations are you asking about?",
                    "options": ["Canada", "USA", "EU", "California", "UK"],
                    "domain_context": "Regulatory requirements vary significantly between regions, especially for ingredients like retinol."
                })
            
            if not any(word in query_lower for word in ["skincare", "supplement", "cosmetic", "topical"]):
                suggestions.append({
                    "question": "How will this ingredient be used?",
                    "options": ["Skincare (Leave-on)", "Skincare (Rinse-off)", "Oral Supplement", "Topical Treatment"],
                    "domain_context": "Usage context dramatically affects regulatory status - leave-on products have stricter requirements."
                })
        
        # Market research clarifications
        if any(word in query_lower for word in ["market", "competitive", "trend", "analysis"]):
            if not any(word in query_lower for word in ["price", "ingredient", "brand", "format"]):
                suggestions.append({
                    "question": "What aspect of the market would you like to analyze?",
                    "options": ["Pricing Strategy", "Ingredient Trends", "Brand Positioning", "Format Innovation", "Regulatory Changes"],
                    "domain_context": "Different market analysis approaches require different data sources and methodologies."
                })
            
            if not any(word in query_lower for word in ["current", "trend", "forecast", "historical"]):
                suggestions.append({
                    "question": "What timeframe are you interested in?",
                    "options": ["Current Market", "Recent Trends", "Historical Data", "Future Forecast"],
                    "domain_context": "Market analysis can focus on current conditions, emerging trends, or predictive insights."
                })
        
        # Formulation clarifications
        if any(word in query_lower for word in ["formulate", "develop", "create", "ingredient"]):
            if not any(word in query_lower for word in ["safe", "compliant", "regulatory"]):
                suggestions.append({
                    "question": "Do you need regulatory compliance information?",
                    "options": ["Yes - Safety First", "No - Just Formulation", "Maybe - Depends on Market"],
                    "domain_context": "Regulatory compliance is crucial for product development, especially in beauty and wellness."
                })
            
            if not any(word in query_lower for word in ["target", "audience", "demographic"]):
                suggestions.append({
                    "question": "Who is your target audience?",
                    "options": ["Women 25-45", "Men 30-60", "Athletes", "Seniors", "Pregnant Women", "Teens"],
                    "domain_context": "Target demographics affect ingredient safety, efficacy, and regulatory requirements."
                })
        
        return suggestions[:3]  # Limit to 3 suggestions max
    
    def format_clarification_response(
        self, 
        assessment: Dict[str, Any], 
        query: str
    ) -> Dict[str, Any]:
        """Format clarification response for API"""
        if not assessment["needs_clarification"]:
            return {"proceed": True}
        
        clarification_type = assessment["clarification_type"]
        
        response = {
            "proceed": False,
            "clarification_required": clarification_type == "required",
            "clarification_suggested": clarification_type == "suggested",
            "original_query": query,
            "clarity_score": assessment["clarity_score"],
            "issues": assessment["issues"],
            "suggestions": assessment["suggested_clarifications"],
            "fallback_available": clarification_type == "suggested"  # Can proceed if just suggested
        }
        
        # Add appropriate message
        if clarification_type == "required":
            response["message"] = "I need more information to provide accurate results. Could you help clarify?"
        else:
            response["message"] = "I can help with this, but more details would improve the results. Would you like to clarify?"
        
        return response
    
    def should_bypass_clarification(self, context: Dict[str, Any]) -> bool:
        """Check if clarification should be bypassed based on context"""
        # Bypass for follow-up queries in same session
        if context.get("session_context", {}).get("previous_queries"):
            return True
        
        # Bypass for specific user roles that prefer direct answers
        if context.get("role") in ["researcher", "analyst"]:
            return True
        
        # Bypass if explicitly requested
        if context.get("skip_clarification"):
            return True
        
        return False

# Global instance
clarification_node = ClarificationNode()
