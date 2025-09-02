#!/usr/bin/env python3
"""
Backend API Testing Script for Sales Module
Tests the Sales module backend APIs as per review request
"""

import requests
import sys
import json
from datetime import datetime

class BackendTester:
    def __init__(self):
        # Use the public endpoint from frontend .env
        self.base_url = "https://erm-sales-portal.preview.emergentagent.com"
        self.api_base = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_form_data=False):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        if not headers:
            headers = {}
        
        if self.token and not use_form_data:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                if self.token:
                    headers['Authorization'] = f'Bearer {self.token}'
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                if use_form_data:
                    # For form data (login endpoint)
                    response = requests.post(url, data=data, headers=headers, timeout=10)
                else:
                    headers['Content-Type'] = 'application/json'
                    if self.token:
                        headers['Authorization'] = f'Bearer {self.token}'
                    response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"Status Code: {response.status_code}")
            
            # Handle different response types
            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)[:500]}...")
            except:
                print(f"Response: {response.text[:500]}...")
                response_data = {}
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Expected {expected_status}, got {response.status_code}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'url': url
                })

            return success, response_data

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'error': f"Network Error: {str(e)}",
                'url': url
            })
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'error': f"Error: {str(e)}",
                'url': url
            })
            return False, {}

    def test_authentication_endpoints(self):
        """Test authentication endpoints as per review request"""
        print("="*60)
        print("TESTING AUTHENTICATION ENDPOINTS")
        print("="*60)
        
        # 1. Test login endpoint: POST /api/v1/auth/token
        print("\n1. Testing Login Endpoint")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        success, response = self.run_test(
            "Login with admin/admin123", 
            "POST", 
            "/api/v1/auth/token", 
            200, 
            data=login_data,
            use_form_data=True
        )
        
        if success and response:
            # Check if we got access_token and user data with menus
            if 'data' in response and 'access_token' in response['data']:
                self.token = response['data']['access_token']
                print(f"✅ Got authentication token: {self.token[:20]}...")
                
                # Verify user data structure
                user_data = response['data'].get('user', {})
                if 'menus' in user_data:
                    print("✅ User data contains menus")
                    # Check for Sales module (module_id = 2)
                    sales_menu = None
                    for menu in user_data['menus']:
                        if menu.get('module_id') == 2:
                            sales_menu = menu
                            break
                    
                    if sales_menu:
                        print(f"✅ Sales module found: {sales_menu['name']}")
                    else:
                        print("❌ Sales module (module_id = 2) not found in menus")
                else:
                    print("❌ User data missing menus")
            else:
                print("❌ Response missing access_token or data structure")
        
        # 2. Test token verification: GET /api/v1/auth/verify-token/
        if self.token:
            print("\n2. Testing Token Verification")
            success, response = self.run_test(
                "Verify Token", 
                "GET", 
                "/api/v1/auth/verify-token/", 
                200
            )
            
            if success and response:
                # Should return user data with menus containing Sales module
                user_data = response.get('data', {}).get('user', {})
                if 'menus' in user_data:
                    print("✅ Token verification returns user data with menus")
                    # Check for Sales module
                    sales_menu = None
                    for menu in user_data['menus']:
                        if menu.get('module_id') == 2:
                            sales_menu = menu
                            break
                    
                    if sales_menu:
                        print(f"✅ Sales module verified: {sales_menu['name']}")
                    else:
                        print("❌ Sales module (module_id = 2) not found in token verification")
                else:
                    print("❌ Token verification missing menus in user data")

    def test_sales_module_endpoints(self):
        """Test Sales Module API endpoints as per review request"""
        print("="*60)
        print("TESTING SALES MODULE ENDPOINTS")
        print("="*60)
        
        if not self.token:
            print("❌ No authentication token available - skipping sales tests")
            return
        
        # 3. Test Companies list: GET /api/v1/sales/companies/
        print("\n3. Testing Companies List")
        success, response = self.run_test(
            "List Companies", 
            "GET", 
            "/api/v1/sales/companies/", 
            200
        )
        
        if success and response:
            companies_data = response.get('data', {})
            if 'companies' in companies_data:
                companies = companies_data['companies']
                print(f"✅ Found {len(companies)} companies")
                
                # Check data structure - should have addresses, turnover, profit records
                if companies:
                    sample_company = companies[0]
                    required_fields = ['addresses', 'turnover_records', 'profit_records']
                    for field in required_fields:
                        if field in sample_company:
                            print(f"✅ Company data contains {field}")
                        else:
                            print(f"❌ Company data missing {field}")
            else:
                print("❌ Response missing companies data")
        
        # 4. Test Contacts list: GET /api/v1/sales/contacts/
        print("\n4. Testing Contacts List")
        success, response = self.run_test(
            "List Contacts", 
            "GET", 
            "/api/v1/sales/contacts/", 
            200
        )
        
        if success and response:
            contacts_data = response.get('data', {})
            if 'contacts' in contacts_data:
                contacts = contacts_data['contacts']
                print(f"✅ Found {len(contacts)} contacts")
                
                # Check data structure - should have addresses and company associations
                if contacts:
                    sample_contact = contacts[0]
                    if 'addresses' in sample_contact:
                        print("✅ Contact data contains addresses")
                    else:
                        print("❌ Contact data missing addresses")
                    
                    if 'company_id' in sample_contact:
                        print("✅ Contact data contains company association")
                    else:
                        print("❌ Contact data missing company association")
            else:
                print("❌ Response missing contacts data")
        
        # 5. Test Parent Companies dropdown: GET /api/v1/sales/companies/parent-companies
        print("\n5. Testing Parent Companies Dropdown")
        success, response = self.run_test(
            "Get Parent Companies", 
            "GET", 
            "/api/v1/sales/companies/parent-companies", 
            200
        )
        
        if success and response:
            if 'data' in response:
                parent_companies = response['data']
                print(f"✅ Found {len(parent_companies)} parent companies for dropdown")
                
                # Check simplified data structure
                if parent_companies and isinstance(parent_companies, list):
                    sample = parent_companies[0]
                    if 'id' in sample and 'name' in sample:
                        print("✅ Parent companies have correct dropdown format (id, name)")
                    else:
                        print("❌ Parent companies missing id/name fields")
            else:
                print("❌ Response missing data field")

    def test_user_management_endpoints(self):
        """Test User Management API endpoints as per review request"""
        print("="*60)
        print("TESTING USER MANAGEMENT ENDPOINTS")
        print("="*60)
        
        if not self.token:
            print("❌ No authentication token available - skipping user management tests")
            return
        
        # 6. Test Users endpoint: GET /api/v1/users/
        print("\n6. Testing Users Endpoint")
        success, response = self.run_test(
            "List Users", 
            "GET", 
            "/api/v1/users/", 
            200
        )
        
        if success and response:
            users_data = response.get('data', {})
            if 'users' in users_data:
                print(f"✅ Found {len(users_data['users'])} users")
            else:
                print("❌ Response missing users data")
        
        # 7. Test Roles endpoint: GET /api/v1/roles/
        print("\n7. Testing Roles Endpoint")
        success, response = self.run_test(
            "List Roles", 
            "GET", 
            "/api/v1/roles/", 
            200
        )
        
        if success and response:
            roles_data = response.get('data', {})
            if 'roles' in roles_data:
                print(f"✅ Found {len(roles_data['roles'])} roles")
            else:
                print("❌ Response missing roles data")
        
        # 8. Test Departments endpoint: GET /api/v1/departments/
        print("\n8. Testing Departments Endpoint")
        success, response = self.run_test(
            "List Departments", 
            "GET", 
            "/api/v1/departments/", 
            200
        )
        
        if success and response:
            departments_data = response.get('data', {})
            if 'departments' in departments_data:
                print(f"✅ Found {len(departments_data['departments'])} departments")
            else:
                print("❌ Response missing departments data")

    def test_master_data_dropdowns(self):
        """Test Master Data Dropdown endpoints as per review request"""
        print("="*60)
        print("TESTING MASTER DATA DROPDOWNS")
        print("="*60)
        
        if not self.token:
            print("❌ No authentication token available - skipping dropdown tests")
            return
        
        # 9. Test dropdown endpoints
        dropdown_endpoints = [
            ("/api/v1/dropdowns/roles", "Roles Dropdown"),
            ("/api/v1/dropdowns/departments", "Departments Dropdown"),
            ("/api/v1/dropdowns/designations", "Designations Dropdown"),
            ("/api/v1/dropdowns/regions", "Regions Dropdown")
        ]
        
        print("\n9. Testing Dropdown Endpoints")
        for endpoint, name in dropdown_endpoints:
            success, response = self.run_test(
                name, 
                "GET", 
                endpoint, 
                200
            )
            
            if success and response:
                if 'data' in response:
                    dropdown_data = response['data']
                    print(f"✅ {name}: Found {len(dropdown_data)} items")
                else:
                    print(f"❌ {name}: Response missing data field")

    def test_basic_connectivity(self):
        """Test basic connectivity and API structure"""
        print("="*60)
        print("TESTING BASIC CONNECTIVITY")
        print("="*60)
        
        # Test API root
        self.run_test("API Root", "GET", "/api/", 200)
        
        # Test API status
        self.run_test("API Status", "GET", "/api/status", 200)

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                if 'error' in test:
                    print(f"  - {test['name']}: {test['error']}")
                else:
                    print(f"  - {test['name']}: Expected {test['expected']}, got {test['actual']}")
                print(f"    URL: {test['url']}")
        
        print(f"\n📊 FOCUS AREAS FROM REVIEW REQUEST:")
        print("✓ Look for any 404 Not Found responses")
        print("✓ Verify response data structure matches expected format") 
        print("✓ Check authentication token flow")
        print("✓ Confirm all endpoints are accessible")
        
        if self.tests_passed == 0:
            print("\n❌ CRITICAL: No tests passed - Backend may not be running correctly")
        elif self.tests_passed < self.tests_run * 0.5:
            print("\n⚠️  WARNING: Less than 50% tests passed - Major issues detected")
        else:
            print("\n✅ Backend appears to be functioning")
            
        # Check for 404 errors specifically
        not_found_errors = [test for test in self.failed_tests if test.get('actual') == 404]
        if not_found_errors:
            print(f"\n🚨 404 ERRORS FOUND ({len(not_found_errors)} endpoints):")
            for test in not_found_errors:
                print(f"  - {test['name']}: {test['url']}")
        else:
            print("\n✅ No 404 errors detected")

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