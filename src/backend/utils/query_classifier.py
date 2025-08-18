"""
Query Classification Utility for Navo Research Assistant
Classifies user queries to determine the best response strategy
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Classification keywords and patterns
PRODUCT_KEYWORDS = [
    'product', 'brand', 'price', 'buy', 'purchase', 'compare', 'review', 'rating',
    'supplement', 'cream', 'serum', 'lotion', 'oil', 'mask', 'cleanser',
    'available', 'stock', 'store', 'shop', 'best', 'top', 'recommend',
    'collagen supplement', 'vitamin', 'protein', 'skincare product'
]

GENERAL_KNOWLEDGE_KEYWORDS = [
    'what is', 'how does', 'why does', 'explain', 'define', 'meaning',
    'difference between', 'benefits of', 'side effects', 'how to use',
    'mechanism', 'science', 'research', 'study', 'clinical', 'evidence',
    'safety', 'dosage', 'recommended amount', 'frequency'
]

HYBRID_KEYWORDS = [
    'best products for', 'which products contain', 'products with',
    'compare products', 'alternatives to', 'similar products',
    'market analysis', 'product trends', 'ingredient analysis'
]

def classify_research_query(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Classify a research query to determine the best response strategy
    
    Args:
        query: The user's query string
        context: Optional context information from the user
        
    Returns:
        Dict with classification results including strategy, confidence, and intent
    """
    logger.info(f"🔍 Classifying query: '{query[:50]}...'")
    
    query_lower = query.lower()
    context = context or {}
    
    # Initialize scoring
    product_score = 0
    general_score = 0
    hybrid_score = 0
    
    # Score based on keywords
    for keyword in PRODUCT_KEYWORDS:
        if keyword in query_lower:
            product_score += 1
    
    for keyword in GENERAL_KNOWLEDGE_KEYWORDS:
        if keyword in query_lower:
            general_score += 2  # Higher weight for knowledge indicators
    
    for keyword in HYBRID_KEYWORDS:
        if keyword in query_lower:
            hybrid_score += 3  # Highest weight for hybrid indicators
    
    # Pattern-based scoring
    if re.search(r'\b(what is|how does|why does|explain|define)\b', query_lower):
        general_score += 3
    
    if re.search(r'\b(best|top|compare|review|price|buy)\b', query_lower):
        product_score += 2
    
    if re.search(r'\b(products? (with|containing|for)|brands? (that|with))\b', query_lower):
        hybrid_score += 2
    
    # Context-based adjustments
    if context:
        role = context.get('role', '').lower()
        objective = context.get('objective', '').lower()
        
        # Role-based adjustments
        if any(term in role for term in ['developer', 'brand manager', 'marketing']):
            product_score += 1
            hybrid_score += 1
        
        if any(term in role for term in ['researcher', 'analyst', 'scientist']):
            general_score += 1
        
        # Objective-based adjustments
        if any(term in objective for term in ['competitive', 'market', 'analysis']):
            hybrid_score += 2
        
        if any(term in objective for term in ['understand', 'learn', 'know']):
            general_score += 1
    
    # Determine strategy based on scores
    max_score = max(product_score, general_score, hybrid_score)
    
    if max_score == 0:
        # Default to general knowledge for unclear queries
        strategy = 'general_knowledge'
        confidence = 0.3
        primary_intent = 'unclear'
    elif hybrid_score == max_score:
        strategy = 'hybrid'
        confidence = min(0.95, 0.6 + (hybrid_score * 0.1))
        primary_intent = 'product_research_with_context'
    elif product_score == max_score:
        strategy = 'product_search'
        confidence = min(0.95, 0.5 + (product_score * 0.1))
        primary_intent = 'product_discovery'
    else:
        strategy = 'general_knowledge'
        confidence = min(0.95, 0.5 + (general_score * 0.1))
        primary_intent = 'knowledge_seeking'
    
    # Special cases for obvious patterns
    if re.search(r'\b(difference between|vs|versus|compare)\b.*\b(marine|bovine|types?)\b', query_lower):
        strategy = 'general_knowledge'
        confidence = 0.9
        primary_intent = 'comparison_knowledge'
    
    if re.search(r'\b(what is|how does|explain|define)\b', query_lower) and not any(kw in query_lower for kw in ['product', 'brand', 'buy']):
        strategy = 'general_knowledge'
        confidence = 0.85
        primary_intent = 'educational'
    
    classification_result = {
        'strategy': strategy,
        'confidence': confidence,
        'primary_intent': primary_intent,
        'scores': {
            'product': product_score,
            'general': general_score,
            'hybrid': hybrid_score
        },
        'reasoning': _get_classification_reasoning(strategy, confidence, query)
    }
    
    logger.info(f"✅ Classification: {strategy} (confidence: {confidence:.2f})")
    return classification_result

def _get_classification_reasoning(strategy: str, confidence: float, query: str) -> str:
    """Generate reasoning for the classification decision"""
    
    if strategy == 'product_search':
        return f"Query appears to be seeking specific product information or comparisons. Keywords suggest product discovery intent."
    
    elif strategy == 'general_knowledge':
        return f"Query appears to be seeking educational or explanatory information. Pattern suggests knowledge-seeking intent."
    
    elif strategy == 'hybrid':
        return f"Query requires both product data and general knowledge. Suggests need for comprehensive market analysis."
    
    else:
        return f"Query classification unclear, defaulting to general knowledge approach."

# Example usage and test queries
EXAMPLE_QUERIES = [
    # Product Search
    "Best collagen supplements under $50",
    "Top rated vitamin C serums",
    "Compare marine collagen products",
    "Affordable retinol creams",
    
    # General Knowledge  
    "What is the difference between marine and bovine collagen?",
    "How does vitamin C work in skincare?",
    "Benefits of hyaluronic acid",
    "What are peptides in skincare?",
    
    # Hybrid
    "Which products contain ceramides for dry skin?",
    "Best niacinamide products for beginners",
    "Market trends in clean beauty",
    "Products with bakuchiol as retinol alternative"
]

def test_classification():
    """Test the classification system with example queries"""
    print("🧪 Testing Query Classification")
    print("=" * 50)
    
    for query in EXAMPLE_QUERIES:
        result = classify_research_query(query)
        print(f"Query: {query}")
        print(f"Strategy: {result['strategy']} (confidence: {result['confidence']:.2f})")
        print(f"Intent: {result['primary_intent']}")
        print(f"Reasoning: {result['reasoning']}")
        print()

if __name__ == "__main__":
    test_classification()