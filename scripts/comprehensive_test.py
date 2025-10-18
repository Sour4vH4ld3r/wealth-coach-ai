#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Wealth Coach AI
Tests all functionality from database to chat endpoints
"""

import requests
import sys
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(message):
    print(f"{Colors.BLUE}[TEST]{Colors.END} {message}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_section(message):
    print(f"\n{Colors.YELLOW}{'='*70}\n{message}\n{'='*70}{Colors.END}")

# Global variables for test data
access_token = None
user_email = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
user_password = "TestPass@123"
user_name = "Test User"

def test_health_check():
    """Test 1: Health Check Endpoint"""
    print_section("TEST 1: Health Check")
    print_test("Checking if server is running...")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is running: {data}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Is it running on port 8000?")
        return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False

def test_database_check():
    """Test 2: Database Initialization"""
    print_section("TEST 2: Database Check")
    print_test("Checking database...")

    try:
        import sys
        sys.path.insert(0, ".")
        from backend.db.database import SessionLocal
        from backend.db.models import User

        db = SessionLocal()
        count = db.query(User).count()
        db.close()

        print_success(f"Database is accessible. Current users: {count}")
        return True
    except Exception as e:
        print_error(f"Database check failed: {str(e)}")
        return False

def test_user_registration():
    """Test 3: User Registration"""
    global access_token
    print_section("TEST 3: User Registration")
    print_test(f"Registering new user: {user_email}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": user_email,
                "password": user_password,
                "full_name": user_name
            },
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            access_token = data.get("access_token")
            print_success(f"Registration successful!")
            print_success(f"Access token received: {access_token[:20]}...")
            return True
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return False

def test_duplicate_registration():
    """Test 4: Duplicate Registration Prevention"""
    print_section("TEST 4: Duplicate Registration Prevention")
    print_test("Attempting to register with same email...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": user_email,
                "password": user_password,
                "full_name": user_name
            },
            timeout=10
        )

        if response.status_code == 400:
            print_success("Duplicate registration correctly prevented")
            return True
        else:
            print_error(f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def test_user_login():
    """Test 5: User Login"""
    global access_token
    print_section("TEST 5: User Login")
    print_test(f"Logging in as {user_email}...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": user_email,
                "password": user_password
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print_success("Login successful!")
            print_success(f"New access token: {access_token[:20]}...")
            return True
        else:
            print_error(f"Login failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return False

def test_wrong_password():
    """Test 6: Wrong Password"""
    print_section("TEST 6: Wrong Password Rejection")
    print_test("Attempting login with wrong password...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": user_email,
                "password": "WrongPassword123!"
            },
            timeout=10
        )

        if response.status_code == 401:
            print_success("Wrong password correctly rejected")
            return True
        else:
            print_error(f"Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def test_chat_without_auth():
    """Test 7: Chat Without Authentication"""
    print_section("TEST 7: Unauthorized Chat Access")
    print_test("Attempting chat without authentication...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/message",
            json={
                "message": "What is a 401k?"
            },
            timeout=10
        )

        if response.status_code == 401:
            print_success("Unauthorized access correctly rejected")
            return True
        else:
            print_error(f"Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def test_chat_with_auth():
    """Test 8: Chat With Authentication"""
    print_section("TEST 8: Authenticated Chat")
    print_test("Sending chat message with authentication...")

    if not access_token:
        print_error("No access token available. Skipping test.")
        return False

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/message",
            json={
                "message": "What is a 401k retirement plan?",
                "use_rag": True
            },
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Chat response received!")
            print_success(f"Response length: {len(data.get('response', ''))} characters")
            print_success(f"Sources used: {len(data.get('sources', []))}")
            print_success(f"Tokens used: {data.get('tokens_used', 'N/A')}")
            print(f"\n{Colors.BLUE}AI Response Preview:{Colors.END}")
            print(data.get('response', '')[:200] + "...")
            return True
        else:
            print_error(f"Chat failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Chat error: {str(e)}")
        return False

def test_password_strength():
    """Test 9: Password Strength Validation"""
    print_section("TEST 9: Password Strength Validation")

    weak_passwords = [
        ("short", "Short password"),
        ("nouppercaseorspecial123", "No uppercase or special chars"),
        ("NoSpecialChars123", "No special chars"),
    ]

    passed = 0
    for password, description in weak_passwords:
        print_test(f"Testing: {description}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/register",
                json={
                    "email": f"weak_{datetime.now().timestamp()}@test.com",
                    "password": password,
                    "full_name": "Test User"
                },
                timeout=10
            )

            if response.status_code == 400:
                print_success(f"Weak password rejected: {description}")
                passed += 1
            else:
                print_error(f"Weak password accepted: {description}")
        except Exception as e:
            print_error(f"Test error: {str(e)}")

    return passed == len(weak_passwords)

def test_bcrypt_72_byte_fix():
    """Test 10: Bcrypt 72-Byte Password Fix"""
    print_section("TEST 10: Bcrypt 72-Byte Password Handling")
    print_test("Testing password that previously caused bcrypt error...")

    try:
        test_email = f"bcrypt_test_{datetime.now().timestamp()}@test.com"
        # This was the original failing password
        test_password = "Halder@7908"

        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "full_name": "Bcrypt Test User"
            },
            timeout=10
        )

        if response.status_code == 201:
            print_success("Password 'Halder@7908' now works correctly!")

            # Now test login with same password
            login_response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "email": test_email,
                    "password": test_password
                },
                timeout=10
            )

            if login_response.status_code == 200:
                print_success("Login with same password successful!")
                return True
            else:
                print_error(f"Login failed after registration: {login_response.status_code}")
                return False
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print_section("🧪 COMPREHENSIVE TEST SUITE - WEALTH COACH AI")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Health Check", test_health_check),
        ("Database Check", test_database_check),
        ("User Registration", test_user_registration),
        ("Duplicate Registration Prevention", test_duplicate_registration),
        ("User Login", test_user_login),
        ("Wrong Password Rejection", test_wrong_password),
        ("Unauthorized Chat Access", test_chat_without_auth),
        ("Authenticated Chat", test_chat_with_auth),
        ("Password Strength Validation", test_password_strength),
        ("Bcrypt 72-Byte Fix", test_bcrypt_72_byte_fix),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {str(e)}")
            results.append((name, False))

    # Summary
    print_section("📊 TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} - {name}")

    print(f"\n{Colors.YELLOW}Results: {passed}/{total} tests passed{Colors.END}")

    if passed == total:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! System is working correctly.{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}⚠️  Some tests failed. Please review the output above.{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
