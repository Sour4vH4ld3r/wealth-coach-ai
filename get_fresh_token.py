"""Get fresh authentication token."""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

# Register a new test user
print("📝 Registering new user...")
register_data = {
    "mobile_number": "9999999999",
    "full_name": "Test User Allocations",
    "password": "Test@12345"
}

response = requests.post(
    f"{API_BASE}/auth/register",
    json=register_data
)

print(f"Status: {response.status_code}")

if response.status_code == 201:
    data = response.json()
    token = data.get("access_token")
    user_info = data

    print(f"✅ Registration successful!")
    print(f"\n🔑 ACCESS TOKEN:")
    print(token)

    # Test the token immediately
    print(f"\n🔍 Testing token with /api/v1/allocations...")
    headers = {"Authorization": f"Bearer {token}"}
    test_response = requests.get(f"{API_BASE}/allocations", headers=headers)

    print(f"Status: {test_response.status_code}")
    if test_response.status_code == 200:
        print("✅ Token works! Allocations endpoint is accessible.")
        data = test_response.json()
        print(f"Categories returned: {len(data.get('categories', []))}")
    else:
        print(f"❌ Error: {test_response.json()}")

elif response.status_code == 400:
    print("User already exists, trying login instead...")
    login_data = {
        "mobile_number": "9999999999",
        "password": "Test@12345"
    }
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful!")
        print(f"\n🔑 ACCESS TOKEN:")
        print(token)

        # Test token
        print(f"\n🔍 Testing token...")
        headers = {"Authorization": f"Bearer {token}"}
        test_response = requests.get(f"{API_BASE}/allocations", headers=headers)
        print(f"Status: {test_response.status_code}")
        if test_response.status_code == 200:
            print("✅ Token works!")
else:
    print(f"❌ Registration failed: {response.json()}")
