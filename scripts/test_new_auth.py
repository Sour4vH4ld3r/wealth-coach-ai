#!/usr/bin/env python3
"""
Test NEW WebSocket Authentication Flow
Uses message-based authentication (not URL token)
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

# Local development server
WSS_URL = "ws://localhost:8000/ws/chat"

# Fresh localhost token (from logs)
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOGZhMjFlOTMtN2ZmNy00YjRiLWE5YjktY2Y0ZDQ3Y2I4ZmJkIiwiZW1haWwiOiJzb3VyYXYxMjNAZ21haWwuY29tIiwiZXhwIjoxNzYwNzY0NDgyLCJpYXQiOjE3NjA3NjI2ODIsInR5cGUiOiJhY2Nlc3MifQ.RTqz7u82ZVxIrcs56czvuzxZBy0pAMk7vXHCafeOOd0"

# Test questions for conversation history
TEST_QUESTIONS = [
    "What is SIP?",
    "How much should I invest in SIP monthly?",
    "What did you just tell me about SIP?",  # Tests conversation memory
]

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'
    END = '\033[0m'


async def test_question(websocket, question, question_num):
    """Send a question and receive streaming AI response."""
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
    is_cached = False

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

                # Check if cached
                if data.get("cached"):
                    is_cached = True

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
                    cache_indicator = f"{Colors.MAGENTA}💾 CACHED{Colors.END}" if is_cached else f"{Colors.GREEN}🤖 FRESH{Colors.END}"
                    print(f"{Colors.GREEN}✅ Response Stats:{Colors.END}")
                    print(f"   Source: {cache_indicator}")
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


async def test_new_auth_flow():
    """Test the NEW message-based authentication flow."""
    print(f"\n{Colors.BLUE}{'='*80}")
    print("🚀 NEW WEBSOCKET AUTHENTICATION TEST")
    print(f"{'='*80}{Colors.END}\n")

    print(f"{Colors.CYAN}Server:{Colors.END} {WSS_URL}")
    print(f"{Colors.CYAN}Auth Method:{Colors.END} Message-based (NEW)")
    print(f"{Colors.CYAN}Test Time:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.CYAN}Questions:{Colors.END} {len(TEST_QUESTIONS)}")

    try:
        print(f"\n{Colors.YELLOW}🔌 Step 1: Connecting WITHOUT token in URL...{Colors.END}")

        # Step 1: Connect WITHOUT token in URL (NEW METHOD)
        async with websockets.connect(WSS_URL, ping_timeout=10) as websocket:
            print(f"{Colors.GREEN}✅ WebSocket connected!{Colors.END}")

            print(f"\n{Colors.YELLOW}🔐 Step 2: Sending authentication message...{Colors.END}")

            # Step 2: Authenticate via message (NEW METHOD)
            await websocket.send(json.dumps({
                "type": "authenticate",
                "token": TEST_TOKEN
            }))

            # Wait for connection confirmation
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)

            if data.get("type") == "connected":
                print(f"{Colors.GREEN}✅ Authenticated: {data.get('message')}{Colors.END}")
                if data.get("deprecated"):
                    print(f"{Colors.YELLOW}⚠️  Using deprecated auth method{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Unexpected response: {data}{Colors.END}")

            print(f"\n{Colors.YELLOW}💬 Step 3: Testing conversation with history...{Colors.END}")

            # Ask test questions
            results = []
            for i, question in enumerate(TEST_QUESTIONS, 1):
                success = await test_question(websocket, question, i)
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

            print(f"{Colors.CYAN}Authentication Method:{Colors.END} Message-based (NEW)")
            print(f"{Colors.CYAN}Questions Asked:{Colors.END} {total}")
            print(f"{Colors.GREEN}Successful Responses:{Colors.END} {passed}")
            print(f"{Colors.RED}Failed Responses:{Colors.END} {total - passed}")

            if passed == total:
                print(f"\n{Colors.GREEN}✅ ALL TESTS PASSED!{Colors.END}")
                print(f"\n{Colors.MAGENTA}🧠 Conversation History Test:{Colors.END}")
                print(f"   Question 3 asked 'What did you just tell me about SIP?'")
                print(f"   If AI referenced previous answers, conversation history is working!")
                return True
            else:
                print(f"\n{Colors.YELLOW}⚠️  SOME TESTS FAILED{Colors.END}")
                return False

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"{Colors.RED}❌ Connection failed with status code: {e.status_code}{Colors.END}")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"{Colors.RED}❌ WebSocket error: {e}{Colors.END}")
        return False
    except ConnectionRefusedError:
        print(f"{Colors.RED}❌ Connection refused - is the server running?{Colors.END}")
        print(f"{Colors.YELLOW}Run: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload{Colors.END}")
        return False
    except asyncio.TimeoutError:
        print(f"{Colors.RED}❌ Connection/Authentication timeout{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Unexpected error: {type(e).__name__}: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys

    try:
        result = asyncio.run(test_new_auth_flow())

        print(f"\n{Colors.BLUE}{'='*80}{Colors.END}\n")

        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        sys.exit(1)
