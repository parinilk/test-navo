"""
Query Clarification System for Navo Research Assistant
Detects ambiguous/vague queries and generates clarifying questions
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ClarificationOption:
    """Represents a clarification option to present to the user"""
    text: str
    description: str
    suggested_query: str
    category: str

@dataclass
class ClarificationResult:
    """Result of query clarification analysis"""
    needs_clarification: bool
    confidence: float
    issues: List[str]
    clarification_question: str
    options: List[ClarificationOption]
    fallback_interpretation: Optional[str] = None

class QueryClarificationService:
    """Service to detect ambiguous queries and generate clarifications"""
    
    def __init__(self):
        # Ambiguous terms that often need clarification
        self.ambiguous_terms = {
            "best": ["highest rated", "most affordable", "most popular", "best for specific skin type"],
            "good": ["high quality", "well-reviewed", "affordable", "suitable for beginners"],
            "stuff": ["products", "ingredients", "supplements", "skincare items"],
            "things": ["products", "ingredients", "supplements", "items"],
            "something": ["products", "treatments", "supplements", "routines"],
            "effective": ["clinically proven", "fast-acting", "long-lasting", "highly rated"],
            "natural": ["organic certified", "plant-based", "chemical-free", "minimally processed"],
            "strong": ["high concentration", "potent formula", "fast-acting", "professional strength"],
            "gentle": ["sensitive skin friendly", "hypoallergenic", "fragrance-free", "low concentration"],
            "cheap": ["budget-friendly", "under $20", "drugstore brands", "value for money"],
            "expensive": ["luxury brands", "premium ingredients", "professional grade", "high-end"],
        }
        
        # Vague categories that need specification
        self.vague_categories = {
            "skincare": ["cleansers", "moisturizers", "serums", "treatments", "sunscreen"],
            "supplements": ["vitamins", "collagen", "protein", "probiotics", "omega-3"],
            "beauty": ["makeup", "skincare", "hair care", "nail care", "tools"],
            "wellness": ["nutrition", "fitness", "mental health", "sleep", "stress management"],
            "products": ["specify category like skincare, supplements, makeup"],
        }
        
        # Incomplete context patterns
        self.incomplete_patterns = [
            (r"\bfor\s+(my|me)\b", "What's your specific skin type, concern, or goal?"),
            (r"\bhelp\s+(with|me)\b", "What specific issue or goal do you have?"),
            (r"\bwhat\s+should\s+i\b", "What are you trying to achieve or address?"),
            (r"\bbest\s+for\b", "Best for what specific purpose, skin type, or concern?"),
            (r"\brecommend\b", "What criteria matter most to you (price, brand, ingredients)?"),
        ]
        
        # Technical jargon that might confuse general users
        self.technical_jargon = {
            "peptides": "anti-aging protein fragments",
            "ceramides": "skin barrier lipids", 
            "niacinamide": "vitamin B3 for skin",
            "hyaluronic acid": "moisture-binding ingredient",
            "retinoids": "vitamin A derivatives",
            "aha/bha": "chemical exfoliants",
            "antioxidants": "protective ingredients",
            "emollients": "softening ingredients",
            "humectants": "moisture-attracting ingredients",
            "occlusives": "moisture-sealing ingredients",
        }
        
        # Common misspellings and variations
        self.common_variations = {
            "colegen": "collagen",
            "hylauronic": "hyaluronic", 
            "retinal": "retinol",
            "vitamic": "vitamin",
            "cermamides": "ceramides",
        }

    def analyze_query(self, query: str, context: Optional[Dict] = None) -> ClarificationResult:
        """
        Analyze query for ambiguity and generate clarifications if needed
        
        Args:
            query: User's original query
            context: Optional context (role, objective, etc.)
            
        Returns:
            ClarificationResult with clarification needs and options
        """
        logger.info(f"🔍 Analyzing query for clarification needs: '{query[:50]}...'")
        
        query_lower = query.lower().strip()
        issues = []
        clarification_options = []
        
        # Check for various ambiguity issues
        ambiguity_score = 0
        
        # 1. Check for overly vague terms
        vague_terms_found = self._detect_vague_terms(query_lower)
        if vague_terms_found:
            issues.append("Contains vague terms that could mean different things")
            ambiguity_score += len(vague_terms_found) * 2
            
        # 2. Check for incomplete context
        missing_context = self._detect_missing_context(query_lower)
        if missing_context:
            issues.append("Missing important context for personalized recommendations")
            ambiguity_score += len(missing_context) * 1.5
            
        # 3. Check for too short/minimal queries
        if len(query.split()) <= 2:
            issues.append("Query is very brief and may lack specificity")
            ambiguity_score += 2
            
        # 4. Check for contradictory requirements
        contradictions = self._detect_contradictions(query_lower)
        if contradictions:
            issues.append("Contains potentially contradictory requirements")
            ambiguity_score += len(contradictions) * 1
            
        # 5. Check for technical jargon without context
        jargon_issues = self._check_jargon_clarity(query_lower)
        if jargon_issues:
            issues.append("Contains technical terms that may need clarification")
            ambiguity_score += len(jargon_issues) * 0.5
            
        # Determine if clarification is needed
        needs_clarification = ambiguity_score >= 3.0
        confidence = min(ambiguity_score / 10.0, 1.0)
        
        if needs_clarification:
            # Generate clarification question and options
            clarification_question, options = self._generate_clarification(
                query, query_lower, issues, vague_terms_found, missing_context, context
            )
        else:
            clarification_question = ""
            options = []
            
        # Generate fallback interpretation
        fallback_interpretation = self._generate_fallback_interpretation(query, context)
        
        result = ClarificationResult(
            needs_clarification=needs_clarification,
            confidence=confidence,
            issues=issues,
            clarification_question=clarification_question,
            options=options,
            fallback_interpretation=fallback_interpretation
        )
        
        logger.info(f"✅ Clarification analysis: needs_clarification={needs_clarification}, confidence={confidence:.2f}")
        return result
    
    def _detect_vague_terms(self, query: str) -> List[str]:
        """Detect vague terms that need clarification"""
        found_terms = []
        for term in self.ambiguous_terms.keys():
            if re.search(rf'\b{re.escape(term)}\b', query):
                found_terms.append(term)
        return found_terms
    
    def _detect_missing_context(self, query: str) -> List[str]:
        """Detect patterns that suggest missing context"""
        missing_context = []
        for pattern, description in self.incomplete_patterns:
            if re.search(pattern, query):
                missing_context.append(description)
        return missing_context
    
    def _detect_contradictions(self, query: str) -> List[str]:
        """Detect contradictory requirements"""
        contradictions = []
        
        # Price contradictions
        if re.search(r'\b(cheap|budget|affordable)\b', query) and re.search(r'\b(premium|luxury|expensive|high.end)\b', query):
            contradictions.append("Both budget-friendly and premium requirements mentioned")
            
        # Strength contradictions  
        if re.search(r'\b(gentle|mild|sensitive)\b', query) and re.search(r'\b(strong|potent|powerful)\b', query):
            contradictions.append("Both gentle and strong product requirements mentioned")
            
        return contradictions
    
    def _check_jargon_clarity(self, query: str) -> List[str]:
        """Check for technical jargon that might need explanation"""
        jargon_found = []
        for term in self.technical_jargon.keys():
            if term.lower() in query:
                jargon_found.append(term)
        return jargon_found
    
    def _generate_clarification(
        self, 
        original_query: str, 
        query_lower: str, 
        issues: List[str], 
        vague_terms: List[str], 
        missing_context: List[str],
        context: Optional[Dict]
    ) -> Tuple[str, List[ClarificationOption]]:
        """Generate clarification question and options"""
        
        # Determine the primary clarification need
        primary_issue = self._identify_primary_issue(issues, vague_terms, missing_context)
        
        # Generate question based on primary issue
        if "vague terms" in primary_issue:
            question = f"I want to help you find the perfect solution! Your query '{original_query}' could mean several things. Could you clarify what you're looking for?"
            options = self._generate_vague_term_options(original_query, vague_terms)
            
        elif "missing context" in primary_issue:
            question = f"To give you the most relevant recommendations for '{original_query}', I'd like to understand more about your specific needs:"
            options = self._generate_context_options(original_query, context)
            
        elif "brief" in primary_issue:
            question = f"Your query '{original_query}' is quite brief. Could you help me understand what specifically you're looking for?"
            options = self._generate_expansion_options(original_query)
            
        else:
            question = f"I want to make sure I understand exactly what you're looking for with '{original_query}'. Which of these best describes what you need?"
            options = self._generate_general_options(original_query)
        
        return question, options
    
    def _identify_primary_issue(self, issues: List[str], vague_terms: List[str], missing_context: List[str]) -> str:
        """Identify the most important clarification need"""
        if vague_terms and len(vague_terms) >= 2:
            return "vague terms"
        elif missing_context:
            return "missing context"
        elif "very brief" in str(issues):
            return "brief"
        else:
            return "general"
    
    def _generate_vague_term_options(self, query: str, vague_terms: List[str]) -> List[ClarificationOption]:
        """Generate options for clarifying vague terms"""
        options = []
        
        # Focus on the most impactful vague term
        primary_vague = vague_terms[0] if vague_terms else ""
        
        if primary_vague in self.ambiguous_terms:
            clarifications = self.ambiguous_terms[primary_vague]
            for i, clarification in enumerate(clarifications[:4]):  # Max 4 options
                option = ClarificationOption(
                    text=clarification,
                    description=f"Focus on {clarification.lower()}",
                    suggested_query=query.replace(primary_vague, clarification),
                    category="specification"
                )
                options.append(option)
        
        return options
    
    def _generate_context_options(self, query: str, context: Optional[Dict]) -> List[ClarificationOption]:
        """Generate options for adding missing context"""
        options = []
        
        # Skin type options for skincare queries
        if any(term in query.lower() for term in ["skin", "face", "acne", "dry", "oily"]):
            skin_types = ["oily skin", "dry skin", "sensitive skin", "combination skin", "mature skin"]
            for skin_type in skin_types:
                options.append(ClarificationOption(
                    text=f"For {skin_type}",
                    description=f"Products specifically suited for {skin_type}",
                    suggested_query=f"{query} for {skin_type}",
                    category="skin_type"
                ))
        
        # Budget options
        budget_ranges = ["under $25", "under $50", "under $100", "premium/luxury"]
        for budget in budget_ranges:
            options.append(ClarificationOption(
                text=budget,
                description=f"Products in the {budget} range",
                suggested_query=f"{query} {budget}",
                category="budget"
            ))
        
        return options[:4]  # Limit to 4 options
    
    def _generate_expansion_options(self, query: str) -> List[ClarificationOption]:
        """Generate options for expanding brief queries"""
        options = []
        
        # Common expansion categories
        expansions = [
            ("for anti-aging", "Anti-aging and wrinkle reduction"),
            ("for acne-prone skin", "Acne treatment and prevention"), 
            ("for hydration", "Moisturizing and hydration"),
            ("for daily routine", "Daily skincare routine products"),
        ]
        
        for expansion, description in expansions:
            options.append(ClarificationOption(
                text=expansion,
                description=description,
                suggested_query=f"{query} {expansion}",
                category="purpose"
            ))
        
        return options
    
    def _generate_general_options(self, query: str) -> List[ClarificationOption]:
        """Generate general clarification options"""
        options = []
        
        # Product vs information distinction
        options.extend([
            ClarificationOption(
                text="I want to buy specific products",
                description="Find and compare actual products to purchase",
                suggested_query=f"best {query} products to buy",
                category="intent"
            ),
            ClarificationOption(
                text="I want to learn about ingredients/science",
                description="Understand how ingredients work and their benefits",
                suggested_query=f"how does {query} work and what are the benefits",
                category="intent"
            ),
            ClarificationOption(
                text="I want product recommendations", 
                description="Get personalized product suggestions",
                suggested_query=f"recommend {query} products for me",
                category="intent"
            ),
        ])
        
        return options[:3]
    
    def _generate_fallback_interpretation(self, query: str, context: Optional[Dict]) -> str:
        """Generate a reasonable fallback interpretation of the query"""
        
        # Use context if available
        if context:
            role = context.get('role', '')
            objective = context.get('objective', '')
            
            if role and objective:
                return f"As a {role} with the objective to {objective}, I interpret this as: {query}"
        
        # General fallback based on query content
        if any(term in query.lower() for term in ["best", "top", "recommend"]):
            return f"I'll search for highly-rated products related to: {query}"
        elif any(term in query.lower() for term in ["what", "how", "why", "explain"]):
            return f"I'll provide educational information about: {query}"
        else:
            return f"I'll search for relevant products and information about: {query}"


# Global instance
clarification_service = QueryClarificationService()

def analyze_query_clarity(query: str, context: Optional[Dict] = None) -> ClarificationResult:
    """Convenience function for query clarification analysis"""
    return clarification_service.analyze_query(query, context)
