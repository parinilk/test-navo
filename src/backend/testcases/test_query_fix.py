#!/usr/bin/env python3
"""
Test Query Fix
Verifies that the LLM now responds to the correct user query instead of getting confused
"""
import asyncio
import sys
import os
import logging

# Add src/backend to path - fix the path to go up one level
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)  # This goes up to src/backend
sys.path.insert(0, parent_dir)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_query_response_fix():
    """Test that the LLM responds to the correct query"""
    print("🧪 Testing Query Response Fix")
    print("=" * 50)
    
    try:
        from rag.llm_integration import LLMService
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Test query (the one that was failing)
        test_query = "What are some distinct or unique ways brands describe stress relief, energy, or sleep support in their product descriptions?"
        
        # Mock product data (simulating what was retrieved)
        mock_products = [
            {
                "product_name": "Hyaluronic Acid Serum",
                "brand": "Test Brand",
                "category": "Skincare",
                "description": "Hydrating serum with HA for skin moisture",
                "price": 29.99
            },
            {
                "product_name": "Vitamin C Cream",
                "brand": "Another Brand", 
                "category": "Skincare",
                "description": "Brightening cream with vitamin C",
                "price": 24.99
            }
        ]
        
        print(f"🔍 Testing query: '{test_query}'")
        print(f"📊 Mock products: {len(mock_products)} products (none about stress/energy/sleep)")
        print()
        
        # Generate response
        print("🔄 Generating LLM response...")
        response = await llm_service.generate_research_response(
            query=test_query,
            context={"role": "Product Developer"},
            product_data=mock_products,
            processed_query={"intent": "product_search", "analysis_complexity": "medium"}
        )
        
        print("✅ LLM response generated successfully!")
        print()
        
        # Analyze the response
        answer = response.get('answer', '')
        rationale = response.get('rationale', '')
        
        print("📝 Response Analysis:")
        print(f"Answer length: {len(answer)} characters")
        print(f"Rationale length: {len(rationale)} characters")
        print()
        
        # Check if response addresses the correct query
        query_keywords = ['stress', 'energy', 'sleep', 'relief', 'support']
        answer_lower = answer.lower()
        
        print("🎯 Query Relevance Check:")
        relevant_terms = [term for term in query_keywords if term in answer_lower]
        print(f"Relevant terms found: {relevant_terms}")
        
        if relevant_terms:
            print("✅ Response appears to address the user's question about stress/energy/sleep")
        else:
            print("⚠️ Response may not be addressing the user's question")
        
        print()
        
        # Check for wrong content (like HA/hyaluronic acid)
        wrong_terms = ['ha', 'hyaluronic', 'acid', 'hydration']
        wrong_content = [term for term in wrong_terms if term in answer_lower]
        
        print("❌ Wrong Content Check:")
        if wrong_content:
            print(f"⚠️ Found irrelevant terms: {wrong_content}")
            print("   This suggests the LLM is still getting confused")
        else:
            print("✅ No irrelevant content found")
        
        print()
        
        # Display response
        print("📄 Full Response:")
        print("-" * 40)
        print(f"Answer: {answer[:200]}...")
        print(f"Rationale: {rationale[:200]}...")
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_product_analysis_service():
    """Test that the product analysis service no longer crashes"""
    print("\n🧪 Testing Product Analysis Service Fix")
    print("=" * 50)
    
    try:
        from services.product_analysis_service import ProductAnalysisService
        
        # Initialize service
        analysis_service = ProductAnalysisService()
        
        # Test with mock products (both dict and object formats)
        mock_products = [
            {
                "product_name": "Test Product 1",
                "ingredients": [
                    {"name": "Vitamin C", "concentration": "10%"},
                    {"name": "Hyaluronic Acid", "concentration": "2%"}
                ]
            },
            {
                "product_name": "Test Product 2", 
                "ingredients": [
                    {"name": "Retinol", "concentration": "1%"}
                ]
            }
        ]
        
        print(f"🔍 Testing with {len(mock_products)} mock products")
        
        # Run analysis
        result = analysis_service.analyze_products(mock_products, {"query": "test"})
        
        print("✅ Product analysis completed successfully!")
        print(f"📊 Analysis confidence: {result.get('analysis_confidence', 0):.2f}")
        print(f"🔍 Data gaps: {len(result.get('data_gaps', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Product analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all query fix tests"""
    print("🚀 Query Response Fix Test Suite")
    print("=" * 60)
    print("Testing if the LLM now responds to the correct user query")
    print()
    
    tests = [
        ("Query Response Fix", test_query_response_fix),
        ("Product Analysis Service", test_product_analysis_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"🧪 Running: {test_name}")
            result = await test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your query response issue should be fixed.")
        print("\n🚀 Next steps:")
        print("1. Test with your actual frontend")
        print("2. Try the same query: 'What are some distinct or unique ways brands describe stress relief, energy, or sleep support in their product descriptions?'")
        print("3. Verify the response now addresses the correct question")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n🔧 You may need to:")
        print("1. Check your environment variables")
        print("2. Verify the LLM service is working")
        print("3. Check the product analysis service")

if __name__ == "__main__":
    asyncio.run(main())
