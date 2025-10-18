#!/usr/bin/env python3
"""Quick test script to chat with the AI"""

import requests
import json

API_URL = "http://localhost:8000"

def test_chat():
    print("=" * 70)
    print(" Wealth Coach AI - Testing Chat Functionality")
    print("=" * 70)
    print()

    # Step 1: Register a user
    print("1. Registering test user...")
    register_data = {
        "email": "testuser@example.com",
        "password": "Test123!",
        "full_name": "Test User"
    }

    try:
        response = requests.post(f"{API_URL}/api/v1/auth/register", json=register_data)
        if response.status_code == 201:
            auth_data = response.json()
            token = auth_data["access_token"]
            print("✓ User registered successfully")
            print(f"  Token: {token[:30]}...")
        elif "already registered" in response.text.lower():
            # User exists, try to login
            print("  User already exists, logging in...")
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            response = requests.post(f"{API_URL}/api/v1/auth/login", json=login_data)
            if response.status_code == 200:
                auth_data = response.json()
                token = auth_data["access_token"]
                print("✓ Logged in successfully")
                print(f"  Token: {token[:30]}...")
            else:
                print(f"✗ Login failed: {response.text}")
                return
        else:
            print(f"✗ Registration failed: {response.text}")
            return
    except Exception as e:
        print(f"✗ Error during registration: {e}")
        return

    print()

    # Step 2: Ask some questions
    questions = [
        "What is a 401k?",
        "How much should I save for retirement?",
        "What is the difference between a Roth IRA and Traditional IRA?",
        "Should I pay off my credit card debt or invest?",
        "What is compound interest?"
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    for i, question in enumerate(questions, 1):
        print(f"{i}. Question: {question}")
        print("-" * 70)

        chat_request = {
            "message": question,
            "use_rag": True
        }

        try:
            response = requests.post(
                f"{API_URL}/api/v1/chat/message",
                json=chat_request,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(f"Answer: {result['response'][:300]}...")
                print(f"\n  Sources used: {len(result.get('sources', []))}")
                if result.get('cached'):
                    print("  ⚡ From cache")
                if result.get('tokens_used'):
                    print(f"  Tokens: {result['tokens_used']}")
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"  {response.text}")
        except Exception as e:
            print(f"✗ Request failed: {e}")

        print()
        print("=" * 70)
        print()

    print("Testing complete!")

if __name__ == "__main__":
    test_chat()
