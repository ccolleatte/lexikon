#!/usr/bin/env python3
"""
Simple authentication test - verify endpoints require JWT.
No registration or login needed - just test that 401 is returned without auth.
"""

import subprocess
import time
import sys
import requests

BASE_URL = "http://127.0.0.1:8001"

def start_server():
    """Start FastAPI server"""
    print("Starting FastAPI server...")
    proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8001'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(4)
    return proc


def test_endpoint(method, endpoint, payload=None):
    """Test endpoint for authentication requirement"""
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        elif method == "POST":
            resp = requests.post(f"{BASE_URL}{endpoint}", json=payload or {}, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(f"{BASE_URL}{endpoint}", timeout=10)
        else:
            return None

        return resp.status_code

    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return "NO_CONN"
    except Exception as e:
        return f"ERROR: {type(e).__name__}"


def main():
    """Run tests"""
    print("=" * 80)
    print("LEXIKON AUTHENTICATION VERIFICATION - Simple Test")
    print("=" * 80)

    server = start_server()

    try:
        print("\nWaiting for server to be ready...")
        time.sleep(2)

        # Test endpoints
        endpoints = [
            # SPRINT 2: Features 1-2
            ("POST", "/api/terms/search", {"query": "test"}),
            ("POST", "/api/ontology/relations", {"source_term_id": "t1", "target_term_id": "t2", "relation_type": "broader"}),
            ("GET", "/api/ontology/relations/term-1", None),
            ("POST", "/api/ontology/infer", {"source_term_id": "t1", "rules": ["transitive"]}),

            # SPRINT 3: Features 3-4
            ("POST", "/api/vocabularies/extract", {"content": "test"}),
            ("POST", "/api/vocabularies/bulk-import", {"content": "[]", "format": "json"}),

            # SPRINT 4: Features 5-6
            ("GET", "/api/hitl/queue", None),
            ("POST", "/api/hitl/reviews", {"term_id": "t1", "review_type": "term_clarity"}),
            ("GET", "/api/metrics/usage", None),
            ("GET", "/api/metrics/ontology-health", None),
            ("GET", "/api/metrics/growth", None),
            ("GET", "/api/metrics/drift-detection", None),
        ]

        print("\n[Authentication Requirements Test]")
        print("-" * 80)

        protected_count = 0
        for method, endpoint, payload in endpoints:
            status = test_endpoint(method, endpoint, payload)

            # 401/403 = requires auth, others = maybe unprotected or error
            is_protected = status in [401, 403]
            marker = "[PROTECTED]" if is_protected else "[WARNING]"

            if is_protected:
                protected_count += 1

            print(f"{marker} {method:6} {endpoint:40} -> {status}")

        print("\n" + "=" * 80)
        print(f"RESULT: {protected_count}/{len(endpoints)} endpoints properly protected")
        print("=" * 80)

        if protected_count == len(endpoints):
            print("[SUCCESS] All SPRINT 2-4 endpoints are authenticated!")
        else:
            print(f"[INFO] {protected_count}/{len(endpoints)} endpoints return 401/403 for missing auth")

    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    main()
