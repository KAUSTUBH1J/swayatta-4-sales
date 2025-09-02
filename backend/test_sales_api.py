#!/usr/bin/env python3
"""
Sales API Testing Script
Tests the Sales module endpoints with curl commands
"""

import subprocess
import json
import sys

# Base URL for the API
BASE_URL = "http://localhost:8001/api/v1"

def run_curl(method, endpoint, data=None, headers=None, token=None):
    """Execute curl command and return response"""
    cmd = ["curl", "-s", "-X", method]
    
    if headers:
        for header in headers:
            cmd.extend(["-H", header])
    
    if token:
        cmd.extend(["-H", f"Authorization: Bearer {token}"])
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json"])
        cmd.extend(["-d", json.dumps(data)])
    
    cmd.append(f"{BASE_URL}{endpoint}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"\n{'='*50}")
        print(f"Request: {method} {endpoint}")
        print(f"Command: {' '.join(cmd)}")
        print(f"Status: {result.returncode}")
        print(f"Response: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.stdout, result.returncode
    except Exception as e:
        print(f"Error executing curl: {e}")
        return None, -1

def test_auth():
    """Test authentication and get token"""
    print("Testing Authentication...")
    
    # Test login
    login_data = {
        "username": "admin",  # Default admin user
        "password": "admin123"  # Default password
    }
    
    response, code = run_curl(
        "POST", 
        "/auth/token",
        data=login_data,
        headers=["Content-Type: application/x-www-form-urlencoded"]
    )
    
    if code == 0 and response:
        try:
            data = json.loads(response)
            if 'data' in data and 'access_token' in data['data']:
                return data['data']['access_token']
        except json.JSONDecodeError:
            pass
    
    print("Failed to get authentication token")
    return None

def test_verify_token(token):
    """Test token verification to see Sales menus"""
    print("Testing Token Verification (should show Sales menus)...")
    
    response, code = run_curl("GET", "/auth/verify-token/", token=token)
    return response, code

def test_companies_api(token):
    """Test Companies CRUD operations"""
    print("Testing Companies API...")
    
    # Test GET companies list
    print("1. Testing GET /sales/companies")
    run_curl("GET", "/sales/companies", token=token)
    
    # Test POST create company
    print("2. Testing POST /sales/companies")
    company_data = {
        "company_name": "Test Company Ltd",
        "gst_no": "27AAAAA0000A1Z5",
        "pan_no": "AAAAA0000A",
        "website": "https://testcompany.com",
        "is_child": False,
        "company_profile": "A test company for API testing",
        "addresses": [
            {
                "address": "123 Test Street",
                "zip_code": "12345"
            }
        ],
        "turnover_records": [
            {
                "year": 2024,
                "revenue": 1000000.00
            }
        ]
    }
    
    response, code = run_curl("POST", "/sales/companies", data=company_data, token=token)
    
    # Extract company ID from response for further tests
    company_id = None
    if code == 0 and response:
        try:
            data = json.loads(response)
            if 'data' in data and 'id' in data['data']:
                company_id = data['data']['id']
        except json.JSONDecodeError:
            pass
    
    if company_id:
        # Test GET single company
        print(f"3. Testing GET /sales/companies/{company_id}")
        run_curl("GET", f"/sales/companies/{company_id}", token=token)
        
        # Test PUT update company
        print(f"4. Testing PUT /sales/companies/{company_id}")
        update_data = {
            "company_name": "Updated Test Company Ltd",
            "website": "https://updated-testcompany.com"
        }
        run_curl("PUT", f"/sales/companies/{company_id}", data=update_data, token=token)
    
    # Test parent companies dropdown
    print("5. Testing GET /sales/companies/parent-companies")
    run_curl("GET", "/sales/companies/parent-companies", token=token)

def test_contacts_api(token):
    """Test Contacts CRUD operations"""
    print("Testing Contacts API...")
    
    # Test GET contacts list
    print("1. Testing GET /sales/contacts")
    run_curl("GET", "/sales/contacts", token=token)
    
    # Test POST create contact (assuming company ID 1 exists)
    print("2. Testing POST /sales/contacts")
    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@testcompany.com",
        "primary_no": "+1234567890",
        "company_id": 1,  # Assuming company with ID 1 exists
        "addresses": [
            {
                "address": "456 Contact Street",
                "zip_code": "67890"
            }
        ]
    }
    
    response, code = run_curl("POST", "/sales/contacts", data=contact_data, token=token)
    
    # Extract contact ID from response
    contact_id = None
    if code == 0 and response:
        try:
            data = json.loads(response)
            if 'data' in data and 'id' in data['data']:
                contact_id = data['data']['id']
        except json.JSONDecodeError:
            pass
    
    if contact_id:
        # Test GET single contact
        print(f"3. Testing GET /sales/contacts/{contact_id}")
        run_curl("GET", f"/sales/contacts/{contact_id}", token=token)
        
        # Test PUT update contact
        print(f"4. Testing PUT /sales/contacts/{contact_id}")
        update_data = {
            "first_name": "Jane",
            "email": "jane.doe@testcompany.com"
        }
        run_curl("PUT", f"/sales/contacts/{contact_id}", data=update_data, token=token)
    
    # Test contacts by company
    print("5. Testing GET /sales/contacts/by-company/1")
    run_curl("GET", "/sales/contacts/by-company/1", token=token)

def main():
    """Main test function"""
    print("Starting Sales API Tests...")
    print(f"Base URL: {BASE_URL}")
    
    # Test authentication
    token = test_auth()
    if not token:
        print("Cannot proceed without authentication token")
        sys.exit(1)
    
    print(f"Authentication successful! Token: {token[:20]}...")
    
    # Test token verification (should show Sales menus)
    test_verify_token(token)
    
    # Test Companies API
    test_companies_api(token)
    
    # Test Contacts API
    test_contacts_api(token)
    
    print("\n" + "="*50)
    print("Sales API testing completed!")
    print("Check the responses above for any errors.")
    print("="*50)

if __name__ == "__main__":
    main()