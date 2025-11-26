#!/usr/bin/env python3
"""
Authentication tests for Lexikon API endpoints.
Tests JWT token generation, validation, and endpoint protection.
"""

import subprocess
import time
import json
import sys
import uuid
import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8001"

# Test user credentials
TEST_USER = {
    "email": "test@example.com",
    "password": "test-password-123",
    "name": "Test User"
}

class TestAuthenticator:
    """Helper class for authentication testing"""

    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.user_id = None

    def register_user(self):
        """Register a test user"""
        print("  Registering test user...")
        resp = requests.post(
            f"{self.base_url}/api/auth/register",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "first_name": "Test",
                "last_name": "User",
                "language": "fr"
            }
        )

        if resp.status_code in [200, 201]:
            data = resp.json()
            self.user_id = data.get('data', {}).get('user_id') or data.get('user_id')
            print(f"    [OK] User registered: {self.user_id}")
            return True
        else:
            print(f"    [SKIP] Registration failed: {resp.status_code}")
            return False

    def login(self):
        """Login and get JWT tokens"""
        print("  Logging in...")
        resp = requests.post(
            f"{self.base_url}/api/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )

        if resp.status_code in [200, 201]:
            data = resp.json()
            token_data = data.get('data', {}) or data
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            self.user_id = token_data.get('user_id')
            print(f"    [OK] Logged in, token: {self.access_token[:20]}...")
            return True
        else:
            print(f"    [FAIL] Login failed: {resp.status_code}")
            print(f"    Response: {resp.text[:200]}")
            return False

    def get_headers(self):
        """Get authorization headers"""
        if not self.access_token:
            return {}
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def test_token_validation(self):
        """Test JWT token validation"""
        print("\n  Testing token validation...")

        if not self.access_token:
            print("    [SKIP] No token available")
            return False

        # Valid token
        headers = self.get_headers()
        resp = requests.get(f"{self.base_url}/api/users/me", headers=headers)
        if resp.status_code == 200:
            print("    [OK] Valid token accepted")
        else:
            print(f"    [FAIL] Valid token rejected: {resp.status_code}")
            return False

        # Invalid token
        bad_headers = {"Authorization": "Bearer invalid-token-xyz"}
        resp = requests.get(f"{self.base_url}/api/users/me", headers=bad_headers)
        if resp.status_code == 401:
            print("    [OK] Invalid token rejected")
        else:
            print(f"    [FAIL] Invalid token should be 401, got {resp.status_code}")

        # Missing token
        resp = requests.get(f"{self.base_url}/api/users/me")
        if resp.status_code == 401:
            print("    [OK] Missing token rejected")
        else:
            print(f"    [FAIL] Missing token should be 401, got {resp.status_code}")

        return True


def start_server():
    """Start FastAPI server"""
    print("Starting FastAPI server...")
    proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8001'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    return proc


def test_endpoint_protection(auth, method, endpoint, data=None):
    """Test that endpoint requires authentication"""
    url = f"{BASE_URL}{endpoint}"

    # Test without authentication
    try:
        if method == "GET":
            resp = requests.get(url)
        elif method == "POST":
            resp = requests.post(url, json=data or {})
        elif method == "DELETE":
            resp = requests.delete(url)
        else:
            return None

        unauth_status = resp.status_code
    except:
        unauth_status = None

    # Test with authentication
    headers = auth.get_headers()
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers)
        elif method == "POST":
            resp = requests.post(url, json=data or {}, headers=headers)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers)
        else:
            return None

        auth_status = resp.status_code
    except:
        auth_status = None

    return {
        "endpoint": endpoint,
        "method": method,
        "without_auth": unauth_status,
        "with_auth": auth_status,
        "protected": unauth_status == 401 or unauth_status == 403
    }


def main():
    """Run authentication tests"""
    print("=" * 70)
    print("LEXIKON AUTHENTICATION TESTS")
    print("=" * 70)

    server = start_server()

    try:
        # Initialize authenticator
        auth = TestAuthenticator()

        # Test 1: User Registration & Login
        print("\n[1] User Registration & Authentication")
        print("-" * 70)
        if not auth.register_user():
            print("  [SKIP] User registration skipped, attempting login with existing user")

        if not auth.login():
            print("  [ERROR] Cannot proceed without authentication")
            return

        # Test 2: Token Validation
        print("\n[2] JWT Token Validation")
        print("-" * 70)
        auth.test_token_validation()

        # Test 3: Endpoint Protection - SPRINT 2 Features
        print("\n[3] SPRINT 2 Feature Endpoints Protection (Features 1-2)")
        print("-" * 70)

        sprint2_endpoints = [
            ("POST", "/api/terms/search", {"query": "test"}),
            ("POST", "/api/ontology/relations", {
                "source_term_id": "term-1",
                "target_term_id": "term-2",
                "relation_type": "broader"
            }),
            ("GET", "/api/ontology/relations/term-1", None),
            ("POST", "/api/ontology/infer", {
                "source_term_id": "term-1",
                "rules": ["transitive"]
            }),
        ]

        sprint2_results = []
        for method, endpoint, data in sprint2_endpoints:
            result = test_endpoint_protection(auth, method, endpoint, data)
            if result:
                sprint2_results.append(result)
                status = "[PROTECTED]" if result["protected"] else "[UNPROTECTED]"
                print(f"  {status} {method:6} {endpoint}")

        # Test 4: Endpoint Protection - SPRINT 3 Features
        print("\n[4] SPRINT 3 Feature Endpoints Protection (Features 3-4)")
        print("-" * 70)

        sprint3_endpoints = [
            ("POST", "/api/vocabularies/extract", {
                "content": "Test content here"
            }),
            ("POST", "/api/vocabularies/bulk-import", {
                "content": "[]",
                "format": "json"
            }),
        ]

        sprint3_results = []
        for method, endpoint, data in sprint3_endpoints:
            result = test_endpoint_protection(auth, method, endpoint, data)
            if result:
                sprint3_results.append(result)
                status = "[PROTECTED]" if result["protected"] else "[UNPROTECTED]"
                print(f"  {status} {method:6} {endpoint}")

        # Test 5: Endpoint Protection - SPRINT 4 Features
        print("\n[5] SPRINT 4 Feature Endpoints Protection (Features 5-6)")
        print("-" * 70)

        sprint4_endpoints = [
            ("GET", "/api/hitl/queue", None),
            ("POST", "/api/hitl/reviews", {"term_id": "term-1", "review_type": "term_clarity"}),
            ("GET", "/api/metrics/usage", None),
            ("GET", "/api/metrics/ontology-health", None),
            ("GET", "/api/metrics/growth", None),
            ("GET", "/api/metrics/drift-detection", None),
        ]

        sprint4_results = []
        for method, endpoint, data in sprint4_endpoints:
            result = test_endpoint_protection(auth, method, endpoint, data)
            if result:
                sprint4_results.append(result)
                status = "[PROTECTED]" if result["protected"] else "[UNPROTECTED]"
                print(f"  {status} {method:6} {endpoint}")

        # Summary
        print("\n" + "=" * 70)
        print("AUTHENTICATION TEST SUMMARY")
        print("=" * 70)

        all_results = sprint2_results + sprint3_results + sprint4_results
        protected_count = sum(1 for r in all_results if r["protected"])
        total_count = len(all_results)

        print(f"\nEndpoint Protection: {protected_count}/{total_count} endpoints properly secured")

        if protected_count == total_count:
            print("\n[SUCCESS] All endpoints are properly protected with JWT authentication")
        else:
            print("\n[WARNING] Some endpoints may not be properly protected")
            unprotected = [r for r in all_results if not r["protected"]]
            for endpoint in unprotected:
                print(f"  - {endpoint['method']:6} {endpoint['endpoint']}: status without auth = {endpoint['without_auth']}")

        print("\nAuthentication Flow:")
        print("  1. User registers and gets confirmation")
        print("  2. User logs in with email/password")
        print("  3. Backend returns access_token + refresh_token")
        print("  4. Client includes 'Authorization: Bearer <token>' header")
        print("  5. Backend validates JWT and returns user context")
        print("  6. Protected endpoints enforce authentication dependency")

        print("\n" + "=" * 70)

    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    main()
