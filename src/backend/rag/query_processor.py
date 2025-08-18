"""
Query processing for extracting intent and filters from user queries
"""
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Process user queries to extract intent, filters, and keywords"""
    
    def __init__(self):
        # Common product categories in beauty/wellness
        self.categories = {
            "skincare": ["skincare", "skin care", "serum", "moisturizer", "cleanser", "toner", "face"],
            "collagen": ["collagen", "peptide", "marine collagen", "bovine collagen"],
            "vitamins": ["vitamin", "supplement", "nutrients", "multivitamin"],
            "beauty": ["beauty", "cosmetic", "makeup", "foundation", "lipstick"],
            "wellness": ["wellness", "health", "organic", "natural"]
        }
        
        # Common product formats
        self.formats = {
            "powder": ["powder", "powdered"],
            "capsule": ["capsule", "caps", "tablet", "pill"],
            "liquid": ["liquid", "serum", "oil", "drink"],
            "gummy": ["gummy", "gummies", "chewable"],
            "cream": ["cream", "lotion", "moisturizer"]
        }
        
        # Functional ingredients mapping (System Prompt compliance)
        self.functional_ingredients = {
            "hydration": ["hyaluronic acid", "ha", "sodium hyaluronate", "glycerin", "ceramides"],
            "anti_aging": ["retinol", "vitamin a", "peptides", "vitamin c", "ascorbic acid"],
            "brightening": ["vitamin c", "niacinamide", "kojic acid", "arbutin", "licorice"],
            "acne_treatment": ["salicylic acid", "benzoyl peroxide", "tea tree", "zinc"],
            "barrier_repair": ["ceramides", "cholesterol", "fatty acids", "niacinamide"],
            "exfoliation": ["aha", "bha", "glycolic acid", "lactic acid", "salicylic acid"],
            "antioxidant": ["vitamin c", "vitamin e", "green tea", "resveratrol", "coq10"]
        }
        
        # Regulatory-sensitive ingredients
        self.regulated_ingredients = [
            "retinol", "tretinoin", "hydroquinone", "salicylic acid", 
            "glycolic acid", "kojic acid", "vitamin a"
        ]
        
        # Price ranges
        self.price_patterns = {
            "under": r"under\s*\$?(\d+)",
            "below": r"below\s*\$?(\d+)", 
            "less_than": r"less\s+than\s*\$?(\d+)",
            "above": r"above\s*\$?(\d+)",
            "over": r"over\s*\$?(\d+)",
            "between": r"between\s*\$?(\d+)\s*(?:and|to)\s*\$?(\d+)"
        }
        
        # Common brands (you can expand this based on your data)
        self.brands = [
            "vital proteins", "ancient nutrition", "sports research", 
            "great lakes", "neocell", "youtheory", "bulletproof"
        ]
    
    def process_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process user query and extract structured information"""
        
        query_lower = query.lower()
        
        result = {
            "original_query": query,
            "intent": self._classify_intent(query_lower),
            "filters": filters or {},
            "keywords": [],
            "categories": [],
            "formats": [],
            "brands": [],
            "context": context or {}
        }
        
        # Extract categories
        result["categories"] = self._extract_categories(query_lower)
        
        # Extract formats
        result["formats"] = self._extract_formats(query_lower)
        
        # Extract brands
        result["brands"] = self._extract_brands(query_lower)
        
        # Extract price filters
        price_filter = self._extract_price_range(query_lower)
        if price_filter:
            result["filters"]["price_range"] = price_filter
        
        # Extract keywords (removing common stop words)
        result["keywords"] = self._extract_keywords(query_lower)
        
        # Enhanced analysis for System Prompt compliance
        result["functional_benefits"] = self._extract_functional_benefits(query)
        result["ingredient_focus"] = self._extract_ingredient_focus(query)
        result["regulatory_sensitive"] = self._check_regulatory_sensitivity(query)
        result["data_requirements"] = self._identify_data_requirements(query, result["intent"])
        result["analysis_complexity"] = self._assess_complexity(query, result["functional_benefits"], result["ingredient_focus"])
        
        # Add context-based filters
        if context:
            if "category" in context:
                result["filters"]["category"] = context["category"]
            if "objective" in context:
                result["context"]["objective"] = context["objective"]
            if "role" in context:
                result["context"]["role"] = context["role"]
        
        logger.info(f"Processed query: {result['intent']} intent, complexity: {result['analysis_complexity']}, {len(result['keywords'])} keywords")
        return result
    
    def _classify_intent(self, query: str) -> str:
        """Classify the intent of the query"""
        
        # Regulatory/compliance intent
        if any(word in query for word in ["allowed", "permitted", "legal", "regulation", "compliance", "banned", "restricted"]):
            return "regulatory_compliance"
        
        # Competitive analysis intent  
        if any(word in query for word in ["compare", "comparison", "vs", "versus", "competitive", "competitor"]):
            return "competitive_analysis"
        
        # Pricing strategy intent
        if any(word in query for word in ["price", "pricing", "cost", "expensive", "cheap", "affordable"]):
            return "pricing_strategy"
        
        # Product positioning intent
        if any(word in query for word in ["claims", "benefits", "positioning", "marketing", "target"]):
            return "product_positioning"
        
        # Market trends intent
        if any(word in query for word in ["trends", "trending", "popular", "market", "growth"]):
            return "market_trends"
        
        # Ingredient analysis intent
        if any(word in query for word in ["ingredient", "formula", "formulation", "contains"]):
            return "ingredient_analysis"
        
        # General product search
        return "product_search"
    
    def _extract_categories(self, query: str) -> List[str]:
        """Extract product categories from query"""
        found_categories = []
        
        for category, keywords in self.categories.items():
            if any(keyword in query for keyword in keywords):
                found_categories.append(category)
        
        return found_categories
    
    def _extract_formats(self, query: str) -> List[str]:
        """Extract product formats from query"""
        found_formats = []
        
        for format_type, keywords in self.formats.items():
            if any(keyword in query for keyword in keywords):
                found_formats.append(format_type)
        
        return found_formats
    
    def _extract_brands(self, query: str) -> List[str]:
        """Extract brand names from query"""
        found_brands = []
        
        for brand in self.brands:
            if brand in query:
                found_brands.append(brand)
        
        return found_brands
    
    def _extract_price_range(self, query: str) -> Optional[Dict[str, float]]:
        """Extract price range filters from query"""
        
        for pattern_name, pattern in self.price_patterns.items():
            matches = re.findall(pattern, query)
            
            if matches:
                if pattern_name in ["under", "below", "less_than"]:
                    return {"max": float(matches[0])}
                elif pattern_name in ["above", "over"]:
                    return {"min": float(matches[0])}
                elif pattern_name == "between" and len(matches[0]) == 2:
                    return {"min": float(matches[0][0]), "max": float(matches[0][1])}
        
        return None
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from query"""
        
        # Common stop words to remove
        stop_words = {
            "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", 
            "by", "from", "up", "about", "into", "through", "during", "before", 
            "after", "above", "below", "between", "among", "is", "are", "was", 
            "were", "be", "been", "being", "have", "has", "had", "do", "does", 
            "did", "will", "would", "could", "should", "may", "might", "must",
            "what", "where", "when", "why", "how", "which", "who", "whom"
        }
        
        # Split query into words and clean
        words = re.findall(r'\b[a-zA-Z]{2,}\b', query)
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _extract_functional_benefits(self, query: str) -> List[str]:
        """Extract functional benefits mentioned in query (System Prompt compliance)"""
        found_benefits = []
        query_lower = query.lower()
        
        for benefit, ingredients in self.functional_ingredients.items():
            # Check if benefit is mentioned directly
            if benefit.replace("_", " ") in query_lower:
                found_benefits.append(benefit)
            # Check if related ingredients are mentioned
            elif any(ingredient in query_lower for ingredient in ingredients):
                found_benefits.append(benefit)
        
        return found_benefits
    
    def _extract_ingredient_focus(self, query: str) -> List[str]:
        """Extract specific ingredients mentioned in query"""
        found_ingredients = []
        query_lower = query.lower()
        
        # Collect all ingredients from functional mapping
        all_ingredients = set()
        for ingredients_list in self.functional_ingredients.values():
            all_ingredients.update(ingredients_list)
        
        for ingredient in all_ingredients:
            if ingredient in query_lower:
                found_ingredients.append(ingredient)
        
        return found_ingredients
    
    def _check_regulatory_sensitivity(self, query: str) -> bool:
        """Check if query involves regulatory-sensitive ingredients"""
        query_lower = query.lower()
        return any(ingredient in query_lower for ingredient in self.regulated_ingredients)
    
    def _identify_data_requirements(self, query: str, intent: str) -> List[str]:
        """Identify what data is needed for comprehensive analysis"""
        requirements = []
        
        if intent == "ingredient_analysis":
            requirements.extend(["ingredient_concentrations", "product_type_classification"])
        
        if "compare" in query.lower() or "vs" in query.lower():
            requirements.extend(["detailed_pricing", "ingredient_profiles", "claims_analysis"])
        
        if any(price_word in query.lower() for price_word in ["price", "cost", "cheap", "expensive", "budget"]):
            requirements.append("pricing_per_serving")
        
        if self._check_regulatory_sensitivity(query):
            requirements.extend(["regulatory_compliance", "jurisdiction_specific_data"])
        
        return list(set(requirements))  # Remove duplicates
    
    def _assess_complexity(self, query: str, functional_benefits: List[str], ingredient_focus: List[str]) -> str:
        """Assess the complexity of the query for appropriate response depth"""
        complexity_score = 0
        
        # Base complexity
        if len(query.split()) > 10:
            complexity_score += 1
        
        # Functional analysis complexity
        if len(functional_benefits) > 2:
            complexity_score += 2
        elif len(functional_benefits) > 0:
            complexity_score += 1
        
        # Ingredient complexity
        if len(ingredient_focus) > 3:
            complexity_score += 2
        elif len(ingredient_focus) > 0:
            complexity_score += 1
        
        # Comparative analysis
        if any(word in query.lower() for word in ["compare", "vs", "versus", "difference", "better"]):
            complexity_score += 2
        
        # Regulatory complexity
        if self._check_regulatory_sensitivity(query):
            complexity_score += 1
        
        if complexity_score >= 5:
            return "high"
        elif complexity_score >= 3:
            return "medium"
        else:
            return "low"
