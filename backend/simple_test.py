#!/usr/bin/env python3
"""
Simple Sales API Test without Authentication
"""

import subprocess
import json

BASE_URL = "http://localhost:8001/api/v1"

def run_curl(method, endpoint, data=None):
    """Execute curl command and return response"""
    cmd = ["curl", "-s", "-X", method]
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json"])
        cmd.extend(["-d", json.dumps(data)])
    
    cmd.append(f"{BASE_URL}{endpoint}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"\n{'='*50}")
        print(f"Request: {method} {endpoint}")
        print(f"Status: {result.returncode}")
        print(f"Response: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.stdout, result.returncode
    except Exception as e:
        print(f"Error executing curl: {e}")
        return None, -1

def test_simple_endpoints():
    """Test simple endpoints without authentication"""
    print("Testing simple endpoints...")
    
    # Test root endpoint
    print("1. Testing GET /")
    run_curl("GET", "/")
    
    # Test sales companies endpoint (should fail without auth)
    print("2. Testing GET /sales/companies (should fail without auth)")
    run_curl("GET", "/sales/companies")
    
    # Test sales contacts endpoint (should fail without auth)
    print("3. Testing GET /sales/contacts (should fail without auth)")
    run_curl("GET", "/sales/contacts")

if __name__ == "__main__":
    print("Starting Simple API Tests...")
    print(f"Base URL: {BASE_URL}")
    test_simple_endpoints()
    print("\nSimple API testing completed!")