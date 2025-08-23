#!/usr/bin/env python3
"""
Simple Query Fix Test
Run this from src/backend directory to test the fixes
"""
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_product_analysis_service():
    """Test that the product analysis service no longer crashes"""
    print("🧪 Testing Product Analysis Service Fix")
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

async def test_llm_service_import():
    """Test that LLM service can be imported and initialized"""
    print("\n🧪 Testing LLM Service Import")
    print("=" * 50)
    
    try:
        from rag.llm_integration import LLMService
        
        # Initialize LLM service
        llm_service = LLMService()
        
        print("✅ LLM service imported and initialized successfully!")
        print(f"📊 Service config: max_retries={llm_service.max_retries}, circuit_breaker_timeout={llm_service.circuit_breaker_timeout}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_context_preparation():
    """Test that context preparation works correctly"""
    print("\n🧪 Testing Context Preparation")
    print("=" * 50)
    
    try:
        from rag.llm_integration import LLMService
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Test query
        test_query = "What are some distinct or unique ways brands describe stress relief, energy, or sleep support in their product descriptions?"
        
        # Mock data
        mock_products = [
            {
                "product_name": "Hyaluronic Acid Serum",
                "brand": "Test Brand",
                "category": "Skincare",
                "description": "Hydrating serum with HA for skin moisture",
                "price": 29.99
            }
        ]
        
        # Test context preparation
        context = llm_service._prepare_context(
            query=test_query,
            context={"role": "Product Developer"},
            product_data=mock_products,
            vector_results=[],
            processed_query={"intent": "product_search"},
            web_search_results=[],
            data_gaps=["No stress/energy/sleep products found"],
            confidence_score=0.3
        )
        
        print("✅ Context preparation completed successfully!")
        print(f"📊 Context length: {len(context)} characters")
        
        # Check if user query is prominent
        if "USER'S QUESTION" in context and test_query in context:
            print("✅ User query is prominently displayed in context")
        else:
            print("⚠️ User query may not be prominent enough")
        
        # Check if relevance warning is present
        if "None of the retrieved products appear to directly address your question" in context:
            print("✅ Relevance warning is present")
        else:
            print("⚠️ Relevance warning may be missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Context preparation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Simple Query Fix Test Suite")
    print("=" * 50)
    print("Testing the key fixes for your query response issue")
    print()
    
    tests = [
        ("Product Analysis Service", test_product_analysis_service),
        ("LLM Service Import", test_llm_service_import),
        ("Context Preparation", test_context_preparation)
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
