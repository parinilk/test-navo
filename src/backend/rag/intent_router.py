"""
Intent Router for RAG System
Routes queries to appropriate datasets: product data vs regulatory compliance data
"""
from typing import Dict, List, Any, Optional, Tuple
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class DatasetType(Enum):
    """Available datasets for routing"""
    PRODUCT_DATA = "product_data"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    BOTH = "both"  # For queries needing info from both datasets
    GENERAL_KNOWLEDGE = "general_knowledge"  # For general questions using web search

class IntentRouter:
    """
    Routes user queries to appropriate datasets based on intent analysis
    As specified in RAG Filters.md Q1 & Q2
    """
    
    def __init__(self):
        # Keywords indicating product-focused queries
        self.product_keywords = {
            "primary": [
                "products", "brands", "compare products", "best products",
                "price", "pricing", "cost", "affordable", "expensive",
                "review", "rating", "quality", "effectiveness",
                "where to buy", "availability", "in stock"
            ],
            "formats": [
                "powder", "capsule", "gummy", "liquid", "cream", "serum",
                "tablet", "pill", "drink", "oil", "lotion"
            ],
            "benefits": [
                "skin health", "joint support", "hair growth", "anti-aging",
                "collagen boost", "hydration", "brightening", "acne treatment"
            ]
        }
        
        # Keywords indicating regulatory/compliance queries
        self.regulatory_keywords = {
            "primary": [
                "allowed", "permitted", "legal", "regulation", "compliance",
                "banned", "restricted", "prohibited", "approved", "safe",
                "FDA", "Health Canada", "EU regulation", "jurisdiction"
            ],
            "ingredients": [
                "retinol", "tretinoin", "hydroquinone", "salicylic acid",
                "glycolic acid", "kojic acid", "vitamin a", "mercury",
                "lead", "formaldehyde"
            ],
            "contexts": [
                "skincare", "leave-on", "rinse-off", "ingestible",
                "topical", "oral supplement", "cosmetic", "drug"
            ],
            "regions": [
                "Canada", "USA", "EU", "California", "Prop 65",
                "Health Canada", "FDA approved", "European Union"
            ]
        }
        
        # Keywords indicating need for both datasets
        self.hybrid_keywords = [
            "formulate", "formulation", "develop product", "ingredient selection",
            "safe ingredients for", "compliant products", "regulatory-safe",
            "market analysis with compliance", "competitive landscape",
            "product positioning with regulations"
        ]
        
        # Use case patterns from RAG Filters.md
        self.use_case_patterns = {
            DatasetType.PRODUCT_DATA: [
                r"\b(competitive landscape|pricing strategy|product positioning)\b",
                r"\b(marketing channel|consumer sentiment|review analysis)\b", 
                r"\b(new product ideation|line extension|flavor.*testing)\b",
                r"\b(packaging strategy|white label|ODM.*benchmarking)\b",
                r"\b(best.*products|recommend.*products|product.*comparison)\b"
            ],
            DatasetType.REGULATORY_COMPLIANCE: [
                r"\b(regulatory.safe|ingredient.*claims|compliance.*check)\b",
                r"\b(allowed.*in|permitted.*for|legal.*use)\b",
                r"\b(banned.*in|restricted.*in|prohibited.*for)\b",
                r"\b(FDA.*approval|Health Canada.*list|EU.*regulation)\b"
            ],
            DatasetType.BOTH: [
                r"\b(formulate.*with|develop.*compliant|safe.*ingredients.*for)\b",
                r"\b(market.*analysis.*compliance|competitive.*regulatory)\b",
                r"\b(product.*development.*regulations|compliant.*positioning)\b",
                r"\b(recent.*updates.*products|latest.*regulation.*products)\b"
            ]
        }
        
        # General knowledge patterns (don't need database)
        self.general_knowledge_patterns = [
            r"\b(what is|how does|why does|explain|define)\b.*\b(collagen|vitamin|supplement|ingredient)\b",
            r"\b(benefits of|effects of|science behind)\b",
            r"\b(how.*work|mechanism|process)\b",
            r"\b(general.*information|learn.*about|understand)\b"
        ]
    
    def route_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        processed_query: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route query to appropriate dataset(s)
        
        Args:
            query: User query string
            context: Optional context from user
            processed_query: Optional pre-processed query data
            
        Returns:
            Dict containing routing decision and metadata
        """
        logger.info(f"🧭 Routing query: '{query[:50]}...'")
        
        query_lower = query.lower()
        context = context or {}
        processed_query = processed_query or {}
        
        # Calculate scores for each dataset
        product_score = self._calculate_product_score(query_lower, context, processed_query)
        regulatory_score = self._calculate_regulatory_score(query_lower, context, processed_query)
        hybrid_score = self._calculate_hybrid_score(query_lower, context, processed_query)
        general_knowledge_score = self._calculate_general_knowledge_score(query_lower, context, processed_query)
        
        # Determine primary dataset
        scores = {
            DatasetType.PRODUCT_DATA: product_score,
            DatasetType.REGULATORY_COMPLIANCE: regulatory_score,
            DatasetType.BOTH: hybrid_score,
            DatasetType.GENERAL_KNOWLEDGE: general_knowledge_score
        }
        
        primary_dataset = max(scores, key=scores.get)
        confidence = scores[primary_dataset] / 10.0  # Normalize to 0-1
        
        # Determine if we need secondary dataset
        secondary_datasets = []
        if primary_dataset == DatasetType.BOTH:
            secondary_datasets = [DatasetType.PRODUCT_DATA, DatasetType.REGULATORY_COMPLIANCE]
        elif confidence < 0.8:  # Low confidence, might need both
            if primary_dataset == DatasetType.PRODUCT_DATA and regulatory_score > 3:
                secondary_datasets.append(DatasetType.REGULATORY_COMPLIANCE)
            elif primary_dataset == DatasetType.REGULATORY_COMPLIANCE and product_score > 3:
                secondary_datasets.append(DatasetType.PRODUCT_DATA)
        
        # Special case: Regulatory-sensitive ingredients always need regulatory data
        if processed_query.get('regulatory_sensitive', False):
            if DatasetType.REGULATORY_COMPLIANCE not in [primary_dataset] + secondary_datasets:
                secondary_datasets.append(DatasetType.REGULATORY_COMPLIANCE)
        
        routing_result = {
            "primary_dataset": primary_dataset,
            "secondary_datasets": secondary_datasets,
            "confidence": min(confidence, 1.0),
            "scores": {k.value: v for k, v in scores.items()},
            "reasoning": self._generate_reasoning(primary_dataset, scores, context),
            "collections_needed": self._map_to_collections(primary_dataset, secondary_datasets),
            "query_strategy": self._determine_query_strategy(primary_dataset, secondary_datasets)
        }
        
        logger.info(f"🎯 Routed to {primary_dataset.value} (confidence: {confidence:.2f})")
        if secondary_datasets:
            logger.info(f"📊 Secondary datasets: {[d.value for d in secondary_datasets]}")
        
        return routing_result
    
    def _calculate_product_score(self, query: str, context: Dict, processed_query: Dict) -> int:
        """Calculate score for product dataset routing"""
        score = 0
        
        # Primary keywords
        for keyword in self.product_keywords["primary"]:
            if keyword in query:
                score += 2
        
        # Format keywords
        for keyword in self.product_keywords["formats"]:
            if keyword in query:
                score += 1
        
        # Benefit keywords
        for keyword in self.product_keywords["benefits"]:
            if keyword in query:
                score += 1
        
        # Price-related queries
        if any(word in query for word in ["price", "cost", "cheap", "expensive", "budget", "affordable"]):
            score += 2
        
        # Comparison queries
        if any(word in query for word in ["compare", "vs", "versus", "better", "best"]):
            score += 2
        
        # Context adjustments
        role = context.get('role', '').lower()
        if any(term in role for term in ['brand manager', 'marketing', 'product manager']):
            score += 1
        
        # Processed query adjustments
        if processed_query.get('intent') in ['competitive_analysis', 'pricing_strategy', 'product_positioning']:
            score += 3
        
        if processed_query.get('categories'):
            score += 1
        
        if processed_query.get('brands'):
            score += 1
        
        return score
    
    def _calculate_regulatory_score(self, query: str, context: Dict, processed_query: Dict) -> int:
        """Calculate score for regulatory dataset routing"""
        score = 0
        
        # Primary regulatory keywords
        for keyword in self.regulatory_keywords["primary"]:
            if keyword in query:
                score += 3
        
        # Regulated ingredients
        for keyword in self.regulatory_keywords["ingredients"]:
            if keyword in query:
                score += 2
        
        # Usage contexts
        for keyword in self.regulatory_keywords["contexts"]:
            if keyword in query:
                score += 1
        
        # Regional/jurisdiction keywords
        for keyword in self.regulatory_keywords["regions"]:
            if keyword in query:
                score += 2
        
        # Context adjustments
        role = context.get('role', '').lower()
        if any(term in role for term in ['regulatory', 'compliance', 'legal', 'scientist']):
            score += 2
        
        # Processed query adjustments
        if processed_query.get('intent') == 'regulatory_compliance':
            score += 4
        
        if processed_query.get('regulatory_sensitive'):
            score += 3
        
        if processed_query.get('ingredient_focus'):
            score += 1
        
        return score
    
    def _calculate_hybrid_score(self, query: str, context: Dict, processed_query: Dict) -> int:
        """Calculate score for needing both datasets"""
        score = 0
        
        # Hybrid keywords
        for keyword in self.hybrid_keywords:
            if keyword in query:
                score += 3
        
        # Product development context
        if any(word in query for word in ["formulate", "develop", "create", "design"]):
            score += 2
        
        # Both product and regulatory elements present
        has_product_elements = any(word in query for word in ["product", "brand", "market"])
        has_regulatory_elements = any(word in query for word in ["safe", "compliant", "allowed", "legal"])
        
        if has_product_elements and has_regulatory_elements:
            score += 4
        
        # Context adjustments
        role = context.get('role', '').lower()
        if any(term in role for term in ['product developer', 'formulation', 'R&D']):
            score += 2
        
        objective = context.get('objective', '').lower()
        if any(term in objective for term in ['develop', 'formulate', 'create']):
            score += 2
        
        # High complexity queries often need both datasets
        if processed_query.get('analysis_complexity') == 'high':
            score += 1
        
        return score
    
    def _calculate_general_knowledge_score(self, query: str, context: Dict, processed_query: Dict) -> int:
        """Calculate score for general knowledge routing (web search)"""
        score = 0
        
        # Check for general knowledge patterns
        import re
        for pattern in self.general_knowledge_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score += 4
        
        # General question words
        general_question_words = ["what is", "how does", "why", "explain", "define", "tell me about"]
        for word_phrase in general_question_words:
            if word_phrase in query:
                score += 2
        
        # Educational context
        role = context.get('role', '').lower()
        if any(term in role for term in ['student', 'researcher', 'learner', 'consumer']):
            score += 1
        
        # No specific product or regulatory indicators
        has_specific_indicators = any([
            any(brand in query for brand in ["vital proteins", "ancient nutrition"]),
            any(price in query for price in ["$", "price", "cost", "buy"]),
            any(reg in query for reg in ["FDA", "allowed", "legal", "regulation"])
        ])
        
        if not has_specific_indicators:
            score += 2
        
        # Broad educational queries
        if any(word in query for word in ["science", "research", "study", "benefits", "mechanism"]):
            score += 1
        
        return score
    
    def _generate_reasoning(self, primary_dataset: DatasetType, scores: Dict, context: Dict) -> str:
        """Generate human-readable reasoning for the routing decision"""
        reasons = []
        
        if primary_dataset == DatasetType.PRODUCT_DATA:
            reasons.append("Query focuses on product information, pricing, or comparisons")
        elif primary_dataset == DatasetType.REGULATORY_COMPLIANCE:
            reasons.append("Query involves regulatory compliance, ingredient safety, or jurisdictional requirements")
        elif primary_dataset == DatasetType.GENERAL_KNOWLEDGE:
            reasons.append("Query seeks general knowledge or educational information best answered via web search")
        else:
            reasons.append("Query requires both product data and regulatory compliance information")
        
        # Add context-based reasoning
        if context.get('role'):
            reasons.append(f"User role ({context['role']}) supports this routing")
        
        # Add score-based reasoning
        score_diff = max(scores.values()) - sorted(scores.values())[-2]
        if score_diff < 2:
            reasons.append("Multiple datasets may be relevant (low confidence)")
        
        return "; ".join(reasons)
    
    def _map_to_collections(self, primary: DatasetType, secondary: List[DatasetType]) -> Dict[str, List[str]]:
        """Map dataset types to actual MongoDB collections"""
        collection_mapping = {
            DatasetType.PRODUCT_DATA: ["main_data", "product_embeddings"],
            DatasetType.REGULATORY_COMPLIANCE: ["regulatory_compliance", "ingredient_safety"],
            DatasetType.BOTH: ["main_data", "regulatory_compliance", "product_embeddings"],
            DatasetType.GENERAL_KNOWLEDGE: []  # No database collections needed, uses web search
        }
        
        collections = {"primary": collection_mapping.get(primary, [])}
        
        if secondary:
            secondary_collections = []
            for dataset in secondary:
                secondary_collections.extend(collection_mapping.get(dataset, []))
            collections["secondary"] = list(set(secondary_collections))
        
        return collections
    
    def _determine_query_strategy(self, primary: DatasetType, secondary: List[DatasetType]) -> str:
        """Determine the query execution strategy"""
        if not secondary:
            return "single_dataset"
        elif len(secondary) == 1:
            return "primary_with_fallback"
        else:
            return "multi_dataset_fusion"

# Global instance
intent_router = IntentRouter()
