#!/usr/bin/env python3
"""Test user registration with password"""

import requests
import json

API_URL = "http://localhost:8000"

print("Testing User Registration with 'Halder@7908' password")
print("=" * 70)

# Test registration
register_data = {
    "email": "halder@example.com",
    "password": "Halder@7908",
    "full_name": "Halder User"
}

print(f"\n1. Attempting to register user: {register_data['email']}")
print(f"   Password: {register_data['password']}")
print(f"   Password length: {len(register_data['password'])} characters")
print(f"   Password bytes: {len(register_data['password'].encode('utf-8'))} bytes")
print()

try:
    response = requests.post(
        f"{API_URL}/api/v1/auth/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"Response Status: {response.status_code}")
    print()

    if response.status_code == 201:
        result = response.json()
        print("✅ SUCCESS! User registered successfully!")
        print()
        print(f"Access Token: {result['access_token'][:50]}...")
        print(f"Refresh Token: {result['refresh_token'][:50]}...")
        print(f"Token Type: {result['token_type']}")
        print()

        # Test login
        print("2. Testing login with same credentials...")
        login_response = requests.post(
            f"{API_URL}/api/v1/auth/login",
            json={
                "email": register_data['email'],
                "password": register_data['password']
            }
        )

        if login_response.status_code == 200:
            print("✅ Login successful!")
            login_result = login_response.json()
            print(f"   New Access Token: {login_result['access_token'][:50]}...")
        else:
            print(f"✗ Login failed: {login_response.status_code}")
            print(f"   {login_response.text}")

    else:
        print(f"✗ Registration failed!")
        print()
        try:
            error_detail = response.json()
            print("Error Details:")
            print(json.dumps(error_detail, indent=2))
        except:
            print(response.text)

except Exception as e:
    print(f"✗ Request failed: {e}")

print()
print("=" * 70)
