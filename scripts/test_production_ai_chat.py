#!/usr/bin/env python3
"""
Test Production AI Chat via WebSocket
Tests wss://api.wealthwarriorshub.in/ws/chat with real questions
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

# Production WebSocket URL
WSS_URL = "wss://api.wealthwarriorshub.in/ws/chat"

# Test token - fresh token from production
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjE1NWRjMzUtYTMxNy00YTljLWJlNzQtYTNiZWM3ZTYzMmNiIiwibW9iaWxlX251bWJlciI6IjYyOTczNjk4MzIiLCJlbWFpbCI6InNvdXJhdjEyM0BnbWFpbC5jb20iLCJleHAiOjE3NjA4MDc5MTEsImlhdCI6MTc2MDgwNjExMSwidHlwZSI6ImFjY2VzcyJ9.C5fqXfbnuIy6F2x9_GVaG5qD4LXpPrB6iWU4_xDAJwE"

# Test questions to ask the AI
TEST_QUESTIONS = [
    "What is compound interest?",
    "How should I start saving money?",
    "What is the difference between stocks and bonds?",
]

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'


async def test_ai_question(websocket, question, question_num):
    """Send a question and receive streaming AI response"""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.CYAN}Question {question_num}: {question}{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}")

    # Send question
    start_time = time.time()
    await websocket.send(json.dumps({
        "type": "message",
        "content": question
    }))

    ttfb = None
    chunk_count = 0
    response_text = ""

    print(f"\n{Colors.YELLOW}AI Response:{Colors.END}")
    print(f"{Colors.WHITE}", end="", flush=True)

    try:
        while True:
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            data = json.loads(response)

            if data.get("type") == "response":
                chunk_count += 1

                # Record time to first byte
                if ttfb is None:
                    ttfb = (time.time() - start_time) * 1000

                # Update response text
                new_content = data.get("content", "")

                # Print only the new part (streaming effect)
                if new_content != response_text:
                    new_chars = new_content[len(response_text):]
                    print(new_chars, end="", flush=True)
                    response_text = new_content

                # Check if done
                if data.get("done"):
                    total_time = (time.time() - start_time) * 1000
                    print(f"{Colors.END}\n")

                    # Print stats
                    print(f"{Colors.GREEN}✅ Response Stats:{Colors.END}")
                    print(f"   TTFB: {ttfb:.0f}ms")
                    print(f"   Total Time: {total_time:.0f}ms")
                    print(f"   Chunks: {chunk_count}")
                    print(f"   Response Length: {len(response_text)} chars")

                    return True

            elif data.get("type") == "error":
                print(f"{Colors.END}")
                print(f"{Colors.RED}❌ AI Error: {data.get('message')}{Colors.END}")
                return False

    except asyncio.TimeoutError:
        print(f"{Colors.END}")
        print(f"{Colors.RED}❌ Response timeout (30s){Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.END}")
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        return False


async def test_production_ai_chat():
    """Main test function"""
    print(f"\n{Colors.BLUE}{'='*80}")
    print("🤖 PRODUCTION AI CHAT TEST")
    print(f"{'='*80}{Colors.END}\n")

    print(f"{Colors.CYAN}Production URL:{Colors.END} {WSS_URL}")
    print(f"{Colors.CYAN}Test Time:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.CYAN}Questions:{Colors.END} {len(TEST_QUESTIONS)}")

    uri = f"{WSS_URL}?token={TEST_TOKEN}"

    try:
        print(f"\n{Colors.YELLOW}🔌 Connecting to WebSocket...{Colors.END}")

        async with websockets.connect(uri, ping_timeout=10) as websocket:
            print(f"{Colors.GREEN}✅ WebSocket connected!{Colors.END}")

            # Receive welcome message
            welcome = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(welcome)

            if data.get("type") == "connected":
                print(f"{Colors.GREEN}✅ Connection confirmed: {data.get('message')}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Unexpected welcome: {data}{Colors.END}")

            # Ask each test question
            results = []
            for i, question in enumerate(TEST_QUESTIONS, 1):
                success = await test_ai_question(websocket, question, i)
                results.append(success)

                # Wait between questions
                if i < len(TEST_QUESTIONS):
                    print(f"\n{Colors.CYAN}⏳ Waiting 2 seconds before next question...{Colors.END}")
                    await asyncio.sleep(2)

            # Print summary
            print(f"\n{Colors.BLUE}{'='*80}")
            print("📊 TEST SUMMARY")
            print(f"{'='*80}{Colors.END}\n")

            passed = sum(results)
            total = len(results)

            print(f"{Colors.CYAN}Questions Asked:{Colors.END} {total}")
            print(f"{Colors.GREEN}Successful Responses:{Colors.END} {passed}")
            print(f"{Colors.RED}Failed Responses:{Colors.END} {total - passed}")

            if passed == total:
                print(f"\n{Colors.GREEN}✅ ALL TESTS PASSED - AI is responding correctly!{Colors.END}")
                return True
            else:
                print(f"\n{Colors.YELLOW}⚠️  SOME TESTS FAILED - Check responses above{Colors.END}")
                return False

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"{Colors.RED}❌ Connection failed with status code: {e.status_code}{Colors.END}")
        print(f"{Colors.YELLOW}Headers: {e.headers}{Colors.END}")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"{Colors.RED}❌ WebSocket error: {e}{Colors.END}")
        return False
    except ConnectionRefusedError:
        print(f"{Colors.RED}❌ Connection refused - server may be down{Colors.END}")
        return False
    except asyncio.TimeoutError:
        print(f"{Colors.RED}❌ Connection timeout{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Unexpected error: {type(e).__name__}: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys

    try:
        result = asyncio.run(test_production_ai_chat())

        print(f"\n{Colors.BLUE}{'='*80}{Colors.END}\n")

        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        sys.exit(1)
