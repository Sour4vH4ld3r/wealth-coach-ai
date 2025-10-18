#!/usr/bin/env python3
"""
Test Production WebSocket Connection
Tests wss:// connection to api.wealthwarriorshub.in
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

# Production WebSocket URL
WSS_URL = "wss://api.wealthwarriorshub.in/ws/chat"

# Test token (you need to provide a valid one)
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYzc5MGZlMmMtZjRiZS00Zjk0LWI3NmYtNWZhNmRmNzVhNjkzIiwibW9iaWxlX251bWJlciI6Ijk5OTk5OTk5OTkiLCJlbWFpbCI6bnVsbCwiZXhwIjoxNzYwNzY0MzQ3LCJpYXQiOjE3NjA3NjI1NDcsInR5cGUiOiJhY2Nlc3MifQ.CkDKFJzvGMa9r_tQyjTDdxc1fjS_GxRJ0epB7YR5Bf0"

async def test_websocket_connection():
    """Test WebSocket connection to production server"""
    print(f"Testing Production WebSocket Connection")
    print(f"=" * 80)
    print(f"URL: {WSS_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    uri = f"{WSS_URL}?token={TEST_TOKEN}"

    try:
        print("🔌 Connecting to WebSocket...")
        async with websockets.connect(uri, ping_timeout=10) as websocket:
            print("✅ WebSocket connected successfully!")
            print()

            # Receive welcome message
            print("📨 Waiting for welcome message...")
            welcome = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(welcome)

            print(f"✅ Received: {json.dumps(data, indent=2)}")
            print()

            if data.get("type") == "connected":
                print("✅ Connection type is correct (connected)")
                print()

                # Send a test message
                test_message = "Hello from production test"
                print(f"📤 Sending test message: '{test_message}'")
                await websocket.send(json.dumps({
                    "type": "message",
                    "content": test_message
                }))

                print("📥 Waiting for AI response...")

                # Receive response chunks
                response_text = ""
                chunk_count = 0

                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        data = json.loads(response)

                        if data.get("type") == "response":
                            chunk_count += 1
                            response_text = data.get("content", "")

                            if data.get("done"):
                                print(f"✅ Received complete response ({chunk_count} chunks)")
                                print(f"Response preview: {response_text[:100]}...")
                                print()
                                print("✅ WebSocket test PASSED!")
                                return True

                    except asyncio.TimeoutError:
                        print("❌ Timeout waiting for response")
                        return False

            else:
                print(f"❌ Unexpected welcome message type: {data.get('type')}")
                return False

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection failed with status code: {e.status_code}")
        print(f"   Headers: {e.headers}")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        return False
    except ConnectionRefusedError:
        print("❌ Connection refused - server may be down")
        return False
    except asyncio.TimeoutError:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_http_endpoints():
    """Test HTTP API endpoints"""
    import aiohttp

    print(f"\nTesting HTTP API Endpoints")
    print(f"=" * 80)

    base_url = "https://api.wealthwarriorshub.in"

    endpoints = [
        ("/", "Root"),
        ("/api/v1/health", "Health"),
        ("/docs", "API Documentation"),
    ]

    async with aiohttp.ClientSession() as session:
        for path, name in endpoints:
            url = f"{base_url}{path}"
            try:
                async with session.get(url, timeout=10) as response:
                    status = response.status
                    if status == 200:
                        print(f"✅ {name:20} - Status {status} - {url}")
                    else:
                        print(f"⚠️  {name:20} - Status {status} - {url}")
            except Exception as e:
                print(f"❌ {name:20} - Error: {e}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("PRODUCTION SERVER CONNECTIVITY TEST")
    print("=" * 80 + "\n")

    # Test HTTP endpoints
    await test_http_endpoints()

    print()

    # Test WebSocket
    success = await test_websocket_connection()

    print()
    print("=" * 80)
    if success:
        print("✅ ALL TESTS PASSED - Production server is working correctly!")
    else:
        print("❌ WEBSOCKET TEST FAILED - Check server configuration")
    print("=" * 80)

    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
