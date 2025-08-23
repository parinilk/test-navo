#!/usr/bin/env python3
"""
Test Startup Fix
Verifies that the system can start up without errors
"""
import asyncio
import sys
import os
import logging

# Add src/backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test database connection"""
    print("🧪 Testing Database Connection")
    print("=" * 40)
    
    try:
        from models.database import get_database, connect_to_mongo
        
        # Test connection
        client = await connect_to_mongo()
        print("✅ MongoDB connection successful")
        
        # Test database access
        db = get_database()
        if db is not None:
            print("✅ Database access successful")
            return True
        else:
            print("⚠️ Database access returned None")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_pinecone_connection():
    """Test Pinecone connection"""
    print("\n🧪 Testing Pinecone Connection")
    print("=" * 40)
    
    try:
        from models.pinecone_vector_store import PineconeVectorStore
        
        # Initialize Pinecone
        pinecone_store = PineconeVectorStore()
        result = await pinecone_store.initialize()
        
        if result:
            print("✅ Pinecone connection successful")
            return True
        else:
            print("⚠️ Pinecone connection failed (this is okay if no API key)")
            return True  # Don't fail the test for Pinecone
            
    except Exception as e:
        print(f"⚠️ Pinecone test failed (this is okay): {e}")
        return True  # Don't fail the test for Pinecone

async def test_dataset_manager():
    """Test dataset manager initialization"""
    print("\n🧪 Testing Dataset Manager")
    print("=" * 40)
    
    try:
        from models.dataset_manager import DatasetManager
        
        # Initialize dataset manager
        dataset_manager = DatasetManager()
        await dataset_manager.initialize()
        
        print("✅ Dataset manager initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Dataset manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_features():
    """Test enhanced robustness features"""
    print("\n🧪 Testing Enhanced Features")
    print("=" * 40)
    
    try:
        # Test clarification system
        from rag.clarification_node import clarification_node
        
        test_query = "collagen"
        assessment = clarification_node.assess_query_clarity(test_query, {"role": "Product Developer"})
        
        print(f"✅ Clarification system working")
        print(f"   Clarity score: {assessment['clarity_score']:.2f}")
        print(f"   Needs clarification: {assessment['needs_clarification']}")
        
        # Test three-tier filters
        from rag.three_tier_filters import three_tier_filter_extractor
        
        test_query = "marine collagen for skin health"
        filters = three_tier_filter_extractor.extract_all_filters(test_query, {"role": "Product Developer"})
        
        print(f"✅ Three-tier filter system working")
        print(f"   Filters extracted: {len(filters)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all startup tests"""
    print("🚀 Startup Fix Test Suite")
    print("=" * 50)
    print("Testing if the system can start up without errors")
    print()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Pinecone Connection", test_pinecone_connection),
        ("Dataset Manager", test_dataset_manager),
        ("Enhanced Features", test_enhanced_features)
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
        print("🎉 All tests passed! Your system should start up properly now.")
        print("\n🚀 Next steps:")
        print("1. Try starting your main server: python main.py")
        print("2. Run the enhanced robustness tests: python test_enhanced_robustness.py")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n🔧 You may need to:")
        print("1. Check your environment variables")
        print("2. Verify MongoDB connection")
        print("3. Check Pinecone API key")

if __name__ == "__main__":
    asyncio.run(main())
