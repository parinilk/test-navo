#!/usr/bin/env python3
"""
Test MongoDB connection for Navo
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mongo_connection():
    """Test MongoDB connection and basic queries"""
    print("🧪 Testing MongoDB Connection...")
    print("=" * 40)
    
    try:
        from models.database import connect_to_mongo
        
        # Test connection
        client = await connect_to_mongo()
        print("✅ MongoDB connected successfully!")
        
        # Test database access
        db = client['Navo_data']
        print(f"📊 Connected to database: {db.name}")
        
        # Test collection access
        collection = db['main_data']
        count = await collection.count_documents({})
        print(f"📈 Found {count} documents in main_data collection")
        
        # Test a sample query
        if count > 0:
            sample = await collection.find_one({})
            if sample:
                print("📋 Sample document structure:")
                for key in list(sample.keys())[:5]:  # Show first 5 keys
                    print(f"   - {key}: {type(sample[key]).__name__}")
        
        print("\n✅ MongoDB test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n💡 Make sure to:")
        print("   1. Update MONGODB_URL in your .env file")
        print("   2. Check your MongoDB Atlas cluster is running")
        print("   3. Verify network access (IP whitelist)")
        return False

if __name__ == "__main__":
    asyncio.run(test_mongo_connection())

