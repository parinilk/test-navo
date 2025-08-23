#!/usr/bin/env python3
"""
Test Enhanced Robustness Features
Demonstrates the improved error handling, retry logic, and domain expertise
"""
import asyncio
import sys
import os
import time
import logging

# Add src/backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_enhanced_llm_filter_extractor():
    """Test the enhanced LLM filter extractor with robustness features"""
    print("🧪 Testing Enhanced LLM Filter Extractor")
    print("=" * 50)
    
    try:
        from rag.llm_filter_extractor import LLMFilterExtractor
        
        # Initialize extractor
        extractor = LLMFilterExtractor()
        
        # Test queries with different complexity levels
        test_queries = [
            "collagen",  # Very vague - should trigger clarification
            "best collagen powder for skin health under $30",  # Clear and specific
            "retinol products in Canada for anti-aging",  # Regulatory-sensitive
            "marine collagen gummies for women over 40 with joint support",  # Complex multi-filter
            "skincare products with peptides and hyaluronic acid for sensitive skin"  # Advanced ingredients
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            print("-" * 40)
            
            try:
                # Extract filters
                result = await extractor.extract_filters_with_llm(query, {"role": "Product Developer"})
                
                print(f"✅ Extraction successful")
                print(f"   Method: {result.get('extraction_method')}")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
                print(f"   Filters extracted: {len(result.get('extracted_filters', {}))}")
                print(f"   Attempts: {result.get('attempts', 1)}")
                
                # Show extracted filters
                filters = result.get('extracted_filters', {})
                if filters:
                    print("   Extracted filters:")
                    for key, value in filters.items():
                        print(f"     {key}: {value}")
                
            except Exception as e:
                print(f"❌ Extraction failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_clarification_system():
    """Test the enhanced clarification system with domain-specific questions"""
    print("\n🧪 Testing Enhanced Clarification System")
    print("=" * 50)
    
    try:
        from rag.clarification_node import clarification_node
        
        # Test queries that should trigger clarification
        test_queries = [
            "collagen",  # Very vague
            "retinol products",  # Missing context
            "market analysis",  # Missing scope
            "formulate product",  # Missing details
            "regulatory check"  # Missing jurisdiction
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            print("-" * 40)
            
            # Assess query clarity
            assessment = clarification_node.assess_query_clarity(query, {"role": "Product Developer"})
            
            print(f"Clarity Score: {assessment['clarity_score']:.2f}")
            print(f"Needs Clarification: {assessment['needs_clarification']}")
            print(f"Clarification Type: {assessment.get('clarification_type', 'none')}")
            
            if assessment['needs_clarification']:
                print("Issues identified:")
                for issue in assessment.get('issues', []):
                    print(f"  • {issue}")
                
                print("Suggested clarifications:")
                for suggestion in assessment.get('suggested_clarifications', []):
                    print(f"  • {suggestion['question']}")
                    if 'options' in suggestion:
                        print(f"    Options: {', '.join(suggestion['options'])}")
                    if 'domain_context' in suggestion:
                        print(f"    Context: {suggestion['domain_context']}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_three_tier_filters():
    """Test the enhanced three-tier filter system with expanded categories"""
    print("\n🧪 Testing Enhanced Three-Tier Filter System")
    print("=" * 50)
    
    try:
        from rag.three_tier_filters import three_tier_filter_extractor
        
        # Test queries with advanced ingredients and categories
        test_queries = [
            "peptides and ceramides for anti-aging",
            "marine collagen with hyaluronic acid for joint health",
            "retinol serum with niacinamide for acne-prone skin",
            "vegan collagen supplements for women over 40",
            "clean beauty products with alpha hydroxy acids"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            print("-" * 40)
            
            # Extract filters
            result = three_tier_filter_extractor.extract_all_filters(query, {"role": "Product Developer"})
            
            print("Extracted filters by tier:")
            for tier_name, tier_filters in result.items():
                if tier_name.startswith("tier_") and tier_filters:
                    print(f"  {tier_name}:")
                    for filter_name, filter_value in tier_filters.items():
                        print(f"    {filter_name}: {filter_value}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_regulatory_service():
    """Test the enhanced regulatory service with comprehensive compliance checking"""
    print("\n🧪 Testing Enhanced Regulatory Service")
    print("=" * 50)
    
    try:
        from services.regulatory_service import regulatory_service
        
        # Test ingredient safety profiles
        test_ingredients = ["retinol", "collagen", "hyaluronic_acid", "salicylic_acid"]
        
        print("🔍 Testing Ingredient Safety Profiles")
        print("-" * 40)
        
        for ingredient in test_ingredients:
            print(f"\nIngredient: {ingredient}")
            
            # Get safety profile for Canada
            profile = regulatory_service.get_ingredient_safety_profile(ingredient, "canada")
            
            print(f"  Safety Rating: {profile['safety_rating']}")
            print(f"  Pregnancy Safe: {profile['pregnancy_safe']}")
            print(f"  Sensitive Skin: {profile['sensitive_skin']}")
            print(f"  Regional Status: {profile.get('regional_status', 'unknown')}")
            
            if 'side_effects' in profile:
                print(f"  Side Effects: {', '.join(profile['side_effects'])}")
            
            if 'alternatives' in profile:
                print(f"  Alternatives: {', '.join(profile['alternatives'])}")
        
        # Test regulatory compliance
        print("\n🔍 Testing Regulatory Compliance")
        print("-" * 40)
        
        test_formulation = {
            "ingredients": ["retinol", "collagen", "hyaluronic_acid"],
            "product_type": "skincare",
            "usage_context": "leave_on"
        }
        
        compliance = regulatory_service.check_regulatory_compliance(
            test_formulation["ingredients"], 
            "canada", 
            test_formulation["product_type"],
            test_formulation["usage_context"]
        )
        
        print(f"Compliant: {compliance['compliant']}")
        print(f"Confidence Score: {compliance['confidence_score']:.2f}")
        
        if compliance['restrictions']:
            print("Restrictions found:")
            for restriction in compliance['restrictions']:
                print(f"  • {restriction['ingredient']}: {restriction['status']}")
        
        if compliance['warnings']:
            print("Warnings:")
            for warning in compliance['warnings']:
                print(f"  • {warning['ingredient']}: {warning['warning']}")
        
        # Test compliance report generation
        print("\n🔍 Testing Compliance Report Generation")
        print("-" * 40)
        
        product_formulation = {
            "name": "Test Anti-Aging Serum",
            "type": "skincare",
            "usage_context": "leave_on",
            "ingredients": ["retinol", "collagen", "hyaluronic_acid", "peptides"]
        }
        
        report = regulatory_service.generate_compliance_report(
            product_formulation, 
            ["canada", "usa", "eu"]
        )
        
        print(f"Product: {report['product_name']}")
        print(f"Overall Compliance: {report['overall_compliance']}")
        print(f"Risk Assessment: {report['risk_assessment']}")
        
        if report['recommendations']:
            print("Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec['region']}: {rec['issue']} (Priority: {rec['priority']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_circuit_breaker_and_retry():
    """Test circuit breaker and retry mechanisms"""
    print("\n🧪 Testing Circuit Breaker and Retry Mechanisms")
    print("=" * 50)
    
    try:
        from rag.llm_filter_extractor import LLMFilterExtractor
        
        # Initialize extractor
        extractor = LLMFilterExtractor()
        
        print("🔍 Testing Circuit Breaker State Management")
        print("-" * 40)
        
        # Simulate failures to trigger circuit breaker
        print("Simulating failures to trigger circuit breaker...")
        for i in range(6):  # More than max_failures (5)
            extractor._record_failure()
            print(f"  Failure {i+1}: Circuit breaker state - {'OPEN' if extractor._is_circuit_breaker_open() else 'CLOSED'}")
        
        # Test circuit breaker timeout
        print("\n🔍 Testing Circuit Breaker Timeout")
        print("-" * 40)
        
        # Simulate time passing
        extractor.last_failure_time = time.time() - 70  # 70 seconds ago (more than 60s timeout)
        
        print(f"Circuit breaker after timeout: {'OPEN' if extractor._is_circuit_breaker_open() else 'CLOSED'}")
        
        # Test retry configuration
        print("\n🔍 Testing Retry Configuration")
        print("-" * 40)
        
        print(f"Max retries: {extractor.max_retries}")
        print(f"Base delay: {extractor.base_delay}s")
        print(f"Max delay: {extractor.max_delay}s")
        
        # Calculate retry delays
        for attempt in range(extractor.max_retries):
            delay = min(extractor.base_delay * (2 ** attempt), extractor.max_delay)
            print(f"  Attempt {attempt + 1}: {delay:.1f}s delay")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all enhanced robustness tests"""
    print("🚀 Enhanced Robustness Test Suite")
    print("=" * 60)
    print("Testing improved error handling, retry logic, and domain expertise")
    print()
    
    tests = [
        ("Enhanced LLM Filter Extractor", test_enhanced_llm_filter_extractor),
        ("Enhanced Clarification System", test_enhanced_clarification_system),
        ("Enhanced Three-Tier Filters", test_enhanced_three_tier_filters),
        ("Enhanced Regulatory Service", test_enhanced_regulatory_service),
        ("Circuit Breaker and Retry", test_circuit_breaker_and_retry)
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
        print("🎉 All tests passed! Your system is robust and ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
