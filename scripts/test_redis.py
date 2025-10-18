#!/usr/bin/env python3
"""
Test Redis Connection - Upstash or Local
"""

import sys
sys.path.insert(0, ".")

from backend.core.config import settings
import redis
import traceback

print("=" * 70)
print("Redis Connection Test")
print("=" * 70)
print()

redis_url = settings.REDIS_URL
print(f"🔗 Redis URL: {redis_url[:50]}...")
print()

try:
    # Connect to Redis
    print("📡 Connecting to Redis...")
    r = redis.from_url(redis_url, decode_responses=True)

    # Test ping
    print("🏓 Testing PING...")
    response = r.ping()
    if response:
        print("✅ PING successful!")

    # Test set/get
    print("\n💾 Testing SET/GET...")
    test_key = "wealth_coach_test"
    test_value = "Hello from Wealth Warriors!"

    r.set(test_key, test_value, ex=60)  # Expire in 60 seconds
    retrieved = r.get(test_key)

    if retrieved == test_value:
        print(f"✅ SET/GET successful!")
        print(f"   Stored: {test_value}")
        print(f"   Retrieved: {retrieved}")

    # Clean up
    r.delete(test_key)

    # Get info
    print("\n📊 Redis Info:")
    info = r.info()
    print(f"   Version: {info.get('redis_version', 'N/A')}")
    print(f"   Uptime: {info.get('uptime_in_seconds', 0)} seconds")
    print(f"   Connected clients: {info.get('connected_clients', 0)}")
    print(f"   Used memory: {info.get('used_memory_human', 'N/A')}")

    print()
    print("=" * 70)
    print("✅ Redis is fully configured and working!")
    print("=" * 70)

except redis.ConnectionError as e:
    print("❌ Connection Error!")
    print(f"   Could not connect to Redis")
    print(f"   Error: {str(e)}")
    print()
    print("💡 Tips:")
    print("   - Check your REDIS_URL in .env file")
    print("   - Verify Upstash database is active")
    print("   - Check if using correct protocol (redis:// or rediss://)")
    sys.exit(1)

except Exception as e:
    print("❌ Unexpected Error!")
    print(f"   Error: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
