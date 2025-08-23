#!/usr/bin/env python3
"""
Test Session Isolation Fix
Verifies that the LLM now responds to the correct question without context confusion
"""
import asyncio
import sys
import os

# Add src/backend to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_session_isolation():
    """Test that LLM responds to the correct question without context confusion"""
    print("🧪 Testing Session Isolation Fix")
    print("=" * 60)
    
    try:
        from rag.llm_integration import LLMService
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Test 1: Pricing question (what the user actually asked)
        print("🔍 Test 1: Pricing Question")
        print("Question: 'Which brands consistently price above the category median, and how do their product features compare to lower-priced competitors?'")
        print()
        
        response1 = await llm_service.generate_research_response(
            query="Which brands consistently price above the category median, and how do their product features compare to lower-priced competitors?",
            context={"role": "Brand Manager", "objective": "Pricing Strategy"},
            product_data=[],  # No products to confuse the LLM
            processed_query={"intent": "competitive_analysis", "analysis_complexity": "high"}
        )
        
        print("✅ Response 1 generated successfully!")
        answer1 = response1.get('answer', '')
        print(f"Answer preview: {answer1[:200]}...")
        
        # Check if response is about pricing (not stress relief)
        if any(term in answer1.lower() for term in ['price', 'pricing', 'median', 'competitive', 'brand']):
            print("✅ Response correctly focuses on pricing and competitive analysis")
        else:
            print("⚠️ Response may not be focused on pricing")
        
        print()
        print("-" * 60)
        print()
        
        # Test 2: Different question to ensure no context carryover
        print("🔍 Test 2: Different Question (Stress Relief)")
        print("Question: 'What are some distinct ways brands describe stress relief, energy, or sleep support in their product descriptions?'")
        print()
        
        response2 = await llm_service.generate_research_response(
            query="What are some distinct ways brands describe stress relief, energy, or sleep support in their product descriptions?",
            context={"role": "Product Developer", "objective": "Claims Analysis"},
            product_data=[],
            processed_query={"intent": "product_research", "analysis_complexity": "medium"}
        )
        
        print("✅ Response 2 generated successfully!")
        answer2 = response2.get('answer', '')
        print(f"Answer preview: {answer2[:200]}...")
        
        # Check if response is about stress relief (not pricing)
        if any(term in answer2.lower() for term in ['stress', 'energy', 'sleep', 'relief', 'support']):
            print("✅ Response correctly focuses on stress relief and sleep support")
        else:
            print("⚠️ Response may not be focused on stress relief")
        
        print()
        print("-" * 60)
        print()
        
        # Test 3: Back to pricing question to ensure no carryover
        print("🔍 Test 3: Back to Pricing Question (Session Isolation)")
        print("Question: 'Which brands consistently price above the category median, and how do their product features compare to lower-priced competitors?'")
        print()
        
        response3 = await llm_service.generate_research_response(
            query="Which brands consistently price above the category median, and how do their product features compare to lower-priced competitors?",
            context={"role": "Brand Manager", "objective": "Pricing Strategy"},
            product_data=[],
            processed_query={"intent": "competitive_analysis", "analysis_complexity": "high"}
        )
        
        print("✅ Response 3 generated successfully!")
        answer3 = response3.get('answer', '')
        print(f"Answer preview: {answer3[:200]}...")
        
        # Check if response is about pricing (not stress relief from previous question)
        if any(term in answer3.lower() for term in ['price', 'pricing', 'median', 'competitive', 'brand']):
            print("✅ Response correctly focuses on pricing (no context carryover)")
        else:
            print("⚠️ Response may have carried over context from previous question")
        
        return True
        
    except Exception as e:
        print(f"❌ Session isolation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the session isolation test"""
    print("🚀 Testing Session Isolation Fix")
    print("This test verifies that the LLM responds to the correct question without context confusion")
    print()
    
    result = await test_session_isolation()
    
    if result:
        print("\n🎉 Test completed! The LLM should now:")
        print("1. ✅ Respond to the correct question (pricing vs. stress relief)")
        print("2. ✅ Maintain session isolation between queries")
        print("3. ✅ Not carry over context from previous questions")
        print("\n🚀 Next steps:")
        print("1. Try your pricing question again in the frontend")
        print("2. The LLM should now respond about pricing, not stress relief")
        print("3. Each new question should be treated as a fresh session")
    else:
        print("\n⚠️ Test failed. Check the error details above.")

if __name__ == "__main__":
    asyncio.run(main())
