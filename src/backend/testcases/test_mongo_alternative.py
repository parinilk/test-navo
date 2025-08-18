#!/usr/bin/env python3
"""
Alternative MongoDB connection test with different SSL settings
"""
import os
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import ssl

# Load environment variables
load_dotenv()

async def test_mongo_alternatives():
    """Test different MongoDB connection methods"""
    mongodb_url = os.getenv("MONGODB_URL", "")
    
    if not mongodb_url:
        print("❌ No MONGODB_URL found in .env file")
        return
    
    print("🧪 Testing Alternative MongoDB Connections...")
    print("=" * 50)
    
    # Method 1: Completely disable SSL verification
    print("\n🔧 Method 1: Disable SSL verification")
    try:
        client1 = AsyncIOMotorClient(
            mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsInsecure=True,
            serverSelectionTimeoutMS=5000
        )
        await client1.admin.command('ping')
        print("✅ Method 1 SUCCESS: SSL verification disabled")
        
        # Test database access
        db = client1['Navo_data']
        count = await db['main_data'].count_documents({})
        print(f"📊 Found {count} documents")
        client1.close()
        return True
        
    except Exception as e:
        print(f"❌ Method 1 failed: {str(e)[:100]}...")
    
    # Method 2: Use different SSL context
    print("\n🔧 Method 2: Custom SSL context")
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        client2 = AsyncIOMotorClient(
            mongodb_url,
            ssl_context=ssl_context,
            serverSelectionTimeoutMS=5000
        )
        await client2.admin.command('ping')
        print("✅ Method 2 SUCCESS: Custom SSL context")
        
        db = client2['Navo_data']
        count = await db['main_data'].count_documents({})
        print(f"📊 Found {count} documents")
        client2.close()
        return True
        
    except Exception as e:
        print(f"❌ Method 2 failed: {str(e)[:100]}...")
    
    # Method 3: Pymongo standard connection
    print("\n🔧 Method 3: Standard pymongo connection")
    try:
        import pymongo
        client3 = pymongo.MongoClient(
            mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000
        )
        client3.admin.command('ping')
        print("✅ Method 3 SUCCESS: Standard pymongo")
        
        db = client3['Navo_data']
        count = db['main_data'].count_documents({})
        print(f"📊 Found {count} documents")
        client3.close()
        return True
        
    except Exception as e:
        print(f"❌ Method 3 failed: {str(e)[:100]}...")
    
    print("\n❌ All connection methods failed")
    print("\n💡 Troubleshooting tips:")
    print("   1. Check if your IP is whitelisted in MongoDB Atlas")
    print("   2. Verify your username/password in the connection string")
    print("   3. Try connecting from MongoDB Compass first")
    print("   4. Check if Windows Firewall is blocking the connection")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_mongo_alternatives())

