#!/usr/bin/env python3
"""
Quick Test: Pricing Analysis Service Fix
Tests if the service can now handle dictionary format products without crashing
"""
import sys
import os

# Add src/backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_pricing_analysis_fix():
    """Test that pricing analysis works with dictionary products"""
    print("🧪 Testing Pricing Analysis Service Fix")
    print("=" * 50)
    
    try:
        from services.product_analysis_service import ProductAnalysisService
        
        # Initialize service
        analysis_service = ProductAnalysisService()
        
        # Test with mock products in dictionary format (like what comes from database)
        mock_products = [
            {
                "product_name": "Premium Probiotic",
                "brand": "HealthPlus",
                "category": "Digestive Health",
                "price": 29.99,
                "ingredients": [
                    {"name": "Lactobacillus", "concentration": "10B CFU"},
                    {"name": "Bifidobacterium", "concentration": "5B CFU"}
                ]
            },
            {
                "product_name": "Budget Probiotic",
                "brand": "ValueBrand",
                "category": "Digestive Health", 
                "price": 12.99,
                "ingredients": [
                    {"name": "Lactobacillus", "concentration": "5B CFU"}
                ]
            },
            {
                "product_name": "Luxury Probiotic",
                "brand": "PremiumWellness",
                "category": "Digestive Health",
                "price": 49.99,
                "ingredients": [
                    {"name": "Lactobacillus", "concentration": "20B CFU"},
                    {"name": "Bifidobacterium", "concentration": "10B CFU"},
                    {"name": "Saccharomyces", "concentration": "2B CFU"}
                ]
            }
        ]
        
        print(f"🔍 Testing with {len(mock_products)} mock products")
        print("   - Premium Probiotic: $29.99")
        print("   - Budget Probiotic: $12.99") 
        print("   - Luxury Probiotic: $49.99")
        print()
        
        # Run analysis
        result = analysis_service.analyze_products(mock_products, {"query": "pricing analysis"})
        
        print("✅ Pricing analysis completed successfully!")
        print(f"📊 Analysis confidence: {result.get('analysis_confidence', 0):.2f}")
        print(f"🔍 Data gaps: {len(result.get('data_gaps', []))}")
        
        # Check pricing analysis
        pricing = result.get('pricing_analysis', {})
        if 'error' not in pricing:
            print(f"💰 Products with pricing: {pricing.get('products_with_pricing', 0)}")
            if 'base_price_range' in pricing:
                price_range = pricing['base_price_range']
                print(f"   Price range: ${price_range.get('min', 0):.2f} - ${price_range.get('max', 0):.2f}")
                print(f"   Average price: ${price_range.get('average', 0):.2f}")
        else:
            print(f"⚠️ Pricing analysis error: {pricing.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pricing analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_pricing_analysis_fix()
    
    if result:
        print("\n🎉 Test passed! The pricing analysis service should now work properly.")
        print("\n🚀 Next steps:")
        print("1. Try your pricing question again")
        print("2. The LLM should now respond to the correct question")
        print("3. No more 'pricing' attribute errors")
    else:
        print("\n⚠️ Test failed. Check the error details above.")
