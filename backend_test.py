#!/usr/bin/env python3
"""
Backend API Testing Script
Tests the current backend implementation to understand what's available
"""

import requests
import sys
import json
from datetime import datetime

class BackendTester:
    def __init__(self):
        # Use the public endpoint from frontend .env
        self.base_url = "https://erm-sales-portal.preview.emergentagent.com"
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        if not headers:
            headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Expected {expected_status}, got {response.status_code}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, {}
        except json.JSONDecodeError as e:
            print(f"❌ Failed - JSON Decode Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_basic_endpoints(self):
        """Test basic endpoints that should exist"""
        print("="*60)
        print("TESTING BASIC ENDPOINTS")
        print("="*60)
        
        # Test root endpoint
        self.run_test("Root Endpoint", "GET", "/", 200)
        
        # Test API root
        self.run_test("API Root", "GET", "/api", 200)
        
        # Test API v1 root  
        self.run_test("API V1 Root", "GET", "/api/v1", 200)

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("="*60)
        print("TESTING AUTHENTICATION ENDPOINTS")
        print("="*60)
        
        # Test auth endpoints
        self.run_test("Auth Token Endpoint", "POST", "/api/v1/auth/token", 422)  # Should fail without data
        
        # Try with login data
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        success, response = self.run_test("Login with Admin", "POST", "/api/v1/auth/token", 200, data=login_data)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"✅ Got authentication token: {self.token[:20]}...")
        elif success and 'data' in response and 'access_token' in response['data']:
            self.token = response['data']['access_token']
            print(f"✅ Got authentication token: {self.token[:20]}...")

    def test_sales_endpoints(self):
        """Test sales endpoints"""
        print("="*60)
        print("TESTING SALES ENDPOINTS")
        print("="*60)
        
        # Test companies endpoints
        self.run_test("List Companies", "GET", "/api/v1/sales/companies", 200)
        self.run_test("Get Parent Companies", "GET", "/api/v1/sales/companies/parent-companies", 200)
        
        # Test contacts endpoints
        self.run_test("List Contacts", "GET", "/api/v1/sales/contacts", 200)
        
        # Test creating a company
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
        
        success, response = self.run_test("Create Company", "POST", "/api/v1/sales/companies", 201, data=company_data)
        
        if success and 'data' in response and 'id' in response['data']:
            company_id = response['data']['id']
            print(f"✅ Created company with ID: {company_id}")
            
            # Test getting the created company
            self.run_test(f"Get Company {company_id}", "GET", f"/api/v1/sales/companies/{company_id}", 200)

    def test_status_endpoints(self):
        """Test the simple status endpoints from server.py"""
        print("="*60)
        print("TESTING STATUS ENDPOINTS (Simple Server)")
        print("="*60)
        
        # Test status endpoints
        self.run_test("Get Status Checks", "GET", "/api/status", 200)
        
        # Test creating status check
        status_data = {"client_name": "Test Client"}
        self.run_test("Create Status Check", "POST", "/api/status", 200, data=status_data)

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == 0:
            print("\n❌ CRITICAL: No tests passed - Backend may not be running correctly")
        elif self.tests_passed < self.tests_run * 0.5:
            print("\n⚠️  WARNING: Less than 50% tests passed - Major issues detected")
        else:
            print("\n✅ Backend appears to be functioning")

def main():
    """Main test function"""
    print("Starting Backend API Tests...")
    print(f"Testing against: https://erm-sales-portal.preview.emergentagent.com")
    
    tester = BackendTester()
    
    # Test basic endpoints first
    tester.test_basic_endpoints()
    
    # Test simple status endpoints (from server.py)
    tester.test_status_endpoints()
    
    # Test authentication
    tester.test_auth_endpoints()
    
    # Test sales endpoints (if auth works)
    if tester.token:
        tester.test_sales_endpoints()
    else:
        print("\n⚠️  Skipping sales tests - No authentication token available")
    
    # Print summary
    tester.print_summary()
    
    return 0 if tester.tests_passed > 0 else 1

if __name__ == "__main__":
    sys.exit(main())