#!/usr/bin/env python3
"""
Quick LLM Fix Test
Tests if the LLM can now provide specific examples without getting confused
"""
import asyncio
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_llm_specific_examples():
    """Test if LLM can provide specific examples without context confusion"""
    print("🧪 Testing LLM Specific Examples Request")
    print("=" * 60)
    
    try:
        from rag.llm_integration import LLMService
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Test the exact follow-up question the user asked
        follow_up_query = "Yes please do that."
        original_context = "User asked about stress relief, energy, and sleep support product descriptions"
        
        print(f"🔍 Testing follow-up: '{follow_up_query}'")
        print(f"📝 Context: {original_context}")
        print()
        
        # Generate response with proper context
        response = await llm_service.generate_research_response(
            query=follow_up_query,
            context={
                "role": "Product Developer",
                "previous_query": "What are some distinct or unique ways brands describe stress relief, energy, or sleep support in their product descriptions?",
                "user_wants": "Specific examples with ingredient mentions and targeted claims from leading brands"
            },
            product_data=[],  # No products to confuse the LLM
            processed_query={"intent": "clarification", "analysis_complexity": "high"}
        )
        
        print("✅ LLM response generated successfully!")
        print()
        
        # Display the response
        answer = response.get('answer', '')
        rationale = response.get('rationale', '')
        
        print("📄 LLM Response:")
        print("-" * 50)
        print(f"Answer: {answer}")
        print(f"Rationale: {rationale}")
        print("-" * 50)
        
        # Check if response is helpful
        if len(answer) > 100 and "ingredient" in answer.lower():
            print("✅ Response appears to provide specific examples as requested")
            return True
        else:
            print("⚠️ Response may not be providing specific examples")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the quick test"""
    print("🚀 Quick LLM Fix Test")
    print("Testing if LLM can handle follow-up questions without confusion")
    print()
    
    result = await test_llm_specific_examples()
    
    if result:
        print("\n🎉 Test passed! The LLM should now handle follow-up questions properly.")
        print("\n🚀 Next steps:")
        print("1. Try your question again in the frontend")
        print("2. Ask for specific examples: 'Yes please do that.'")
        print("3. The LLM should now provide ingredient examples without confusion")
    else:
        print("\n⚠️ Test failed. The LLM may still have context issues.")
        print("\n🔧 You may need to:")
        print("1. Check if the fixes were applied correctly")
        print("2. Verify the LLM service is working")
        print("3. Check the context preparation logic")

if __name__ == "__main__":
    asyncio.run(main())
