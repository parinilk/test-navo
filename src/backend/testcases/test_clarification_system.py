"""
Test the Query Clarification System
Run this to see how the clarification system handles ambiguous queries
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.query_clarification import analyze_query_clarity

async def test_clarification_examples():
    """Test the clarification system with various query types"""
    
    print("🧪 Testing Query Clarification System")
    print("=" * 60)
    
    # Test cases that should trigger clarification
    ambiguous_queries = [
        # Vague terms
        "best skincare products",
        "good supplements for me", 
        "cheap stuff for acne",
        "strong retinol",
        "natural beauty things",
        
        # Missing context
        "help with my skin",
        "what should I buy",
        "recommend something",
        "best for dry skin",
        
        # Too brief
        "collagen",
        "vitamin C",
        "moisturizer",
        
        # Technical jargon without context
        "peptides vs ceramides",
        "niacinamide concentration",
        
        # From your test prompts
        "st marine collagen supplements under $50",
        "Which marine collagen supplements are the top sellers in the U.S. and Canadian beauty & wellness markets",
    ]
    
    # Test cases that should NOT trigger clarification  
    clear_queries = [
        "What is the difference between marine and bovine collagen supplements?",
        "Best collagen supplements under $50 for anti-aging with high protein content",
        "How does vitamin C work in skincare and what concentration is effective?",
        "Compare marine collagen powder vs capsules for daily supplementation"
    ]
    
    print("🔍 TESTING AMBIGUOUS QUERIES (should trigger clarification):")
    print("-" * 60)
    
    for query in ambiguous_queries:
        print(f"\nQuery: '{query}'")
        result = analyze_query_clarity(query)
        
        if result.needs_clarification:
            print(f"✅ CLARIFICATION NEEDED (confidence: {result.confidence:.2f})")
            print(f"   Issues: {', '.join(result.issues)}")
            print(f"   Question: {result.clarification_question}")
            print(f"   Options:")
            for i, option in enumerate(result.options, 1):
                print(f"      {i}. {option.text} - {option.description}")
                print(f"         Suggested: '{option.suggested_query}'")
        else:
            print(f"❌ NO CLARIFICATION (confidence: {result.confidence:.2f}) - Should have triggered!")
        
        print("-" * 40)
    
    print("\n\n🎯 TESTING CLEAR QUERIES (should NOT trigger clarification):")
    print("-" * 60)
    
    for query in clear_queries:
        print(f"\nQuery: '{query}'")
        result = analyze_query_clarity(query)
        
        if not result.needs_clarification:
            print(f"✅ NO CLARIFICATION NEEDED (confidence: {result.confidence:.2f})")
            print(f"   Fallback: {result.fallback_interpretation}")
        else:
            print(f"❌ CLARIFICATION TRIGGERED (confidence: {result.confidence:.2f}) - Should be clear!")
            print(f"   Issues: {', '.join(result.issues)}")
        
        print("-" * 40)

async def test_with_context():
    """Test how context affects clarification"""
    
    print("\n\n🎭 TESTING WITH CONTEXT:")
    print("-" * 60)
    
    query = "best products for my needs"
    
    contexts = [
        {
            "role": "Product Manager",
            "objective": "identify competitive marine collagen products for market analysis",
            "topic": "marine collagen supplements in the beauty and wellness market"
        },
        {
            "role": "Skincare Enthusiast", 
            "objective": "find effective anti-aging routine",
            "topic": "skincare products for mature skin"
        },
        None  # No context
    ]
    
    for i, context in enumerate(contexts, 1):
        print(f"\nTest {i} - Query: '{query}'")
        if context:
            print(f"Context: {context}")
        else:
            print("Context: None")
            
        result = analyze_query_clarity(query, context)
        
        print(f"Needs clarification: {result.needs_clarification}")
        print(f"Confidence: {result.confidence:.2f}")
        if result.needs_clarification:
            print(f"Question: {result.clarification_question}")
        print(f"Fallback: {result.fallback_interpretation}")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_clarification_examples())
    asyncio.run(test_with_context())
    
    print("\n🎉 Clarification system testing complete!")
    print("\nTo use in your application:")
    print("1. Vague queries will return ClarificationResponse with options")
    print("2. Users can select an option or provide more specific queries") 
    print("3. Clear queries proceed directly to research")
    print("4. Use /query/clarified endpoint for pre-clarified queries")
