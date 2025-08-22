#!/usr/bin/env python3
"""
SendGrid Password Recovery Testing Script
This script tests the password recovery functionality with SendGrid integration.
"""

import os
import sys
import requests
import json
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SendGridTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "message": message
        }
        self.test_results.append(result)
        print(f"[{timestamp}] {test_name}: {status} - {message}")
        
    def test_server_connection(self):
        """Test if the Flask server is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                self.log_test("Server Connection", "PASS", "Flask server is running")
                return True
            else:
                self.log_test("Server Connection", "FAIL", f"Server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Server Connection", "FAIL", f"Could not connect to server: {str(e)}")
            return False
    
    def test_sendgrid_config(self):
        """Test SendGrid configuration"""
        try:
            # Check environment variables
            api_key = os.environ.get('SENDGRID_API_KEY')
            sender_email = os.environ.get('MAIL_DEFAULT_SENDER')
            
            if not api_key:
                self.log_test("SendGrid Config", "FAIL", "SENDGRID_API_KEY not found in environment")
                return False
                
            if not sender_email:
                self.log_test("SendGrid Config", "FAIL", "MAIL_DEFAULT_SENDER not found in environment")
                return False
                
            self.log_test("SendGrid Config", "PASS", f"API Key: {'*' * 10 + api_key[-4:] if api_key else 'Not set'}, Sender: {sender_email}")
            return True
            
        except Exception as e:
            self.log_test("SendGrid Config", "FAIL", f"Error checking config: {str(e)}")
            return False
    
    def test_sendgrid_smtp_connection(self):
        """Test direct SMTP connection to SendGrid"""
        try:
            api_key = os.environ.get('SENDGRID_API_KEY')
            if not api_key:
                self.log_test("SendGrid SMTP", "SKIP", "No API key available")
                return False
                
            # Test SMTP connection
            server = smtplib.SMTP('smtp.sendgrid.net', 587)
            server.starttls()
            server.login('apikey', api_key)
            server.quit()
            
            self.log_test("SendGrid SMTP", "PASS", "SMTP connection successful")
            return True
            
        except Exception as e:
            self.log_test("SendGrid SMTP", "FAIL", f"SMTP connection failed: {str(e)}")
            return False
    
    def test_user_registration(self, test_email, test_password="TestPassword123!"):
        """Test user registration"""
        try:
            data = {
                "full_name": "Test User",
                "email": test_email,
                "password": test_password
            }
            
            response = requests.post(
                f"{self.base_url}/register",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    self.log_test("User Registration", "PASS", f"User {test_email} registered successfully")
                    return True
                else:
                    self.log_test("User Registration", "FAIL", f"Registration failed: {result.get('message')}")
                    return False
            else:
                self.log_test("User Registration", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", "FAIL", f"Registration error: {str(e)}")
            return False
    
    def test_forgot_password_request(self, test_email):
        """Test forgot password request"""
        try:
            data = {"email": test_email}
            
            response = requests.post(
                f"{self.base_url}/forgot",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    self.log_test("Forgot Password Request", "PASS", f"Reset email sent to {test_email}")
                    return True
                else:
                    self.log_test("Forgot Password Request", "FAIL", f"Request failed: {result.get('message')}")
                    return False
            else:
                self.log_test("Forgot Password Request", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Forgot Password Request", "FAIL", f"Request error: {str(e)}")
            return False
    
    def test_nonexistent_email(self):
        """Test forgot password with non-existent email"""
        try:
            data = {"email": "nonexistent@example.com"}
            
            response = requests.post(
                f"{self.base_url}/forgot",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 404:
                result = response.json()
                if result.get('status') == 'error' and 'No account' in result.get('message', ''):
                    self.log_test("Non-existent Email", "PASS", "Correctly handled non-existent email")
                    return True
                else:
                    self.log_test("Non-existent Email", "FAIL", f"Unexpected response: {result}")
                    return False
            else:
                self.log_test("Non-existent Email", "FAIL", f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Non-existent Email", "FAIL", f"Test error: {str(e)}")
            return False
    
    def test_invalid_email_format(self):
        """Test forgot password with invalid email format"""
        try:
            data = {"email": "invalid-email-format"}
            
            response = requests.post(
                f"{self.base_url}/forgot",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # The endpoint should still process the request even with invalid format
            # as it will just not find a user
            if response.status_code in [200, 404]:
                self.log_test("Invalid Email Format", "PASS", "Handled invalid email format appropriately")
                return True
            else:
                self.log_test("Invalid Email Format", "FAIL", f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Email Format", "FAIL", f"Test error: {str(e)}")
            return False
    
    def test_empty_request(self):
        """Test forgot password with empty request"""
        try:
            response = requests.post(
                f"{self.base_url}/forgot",
                json={},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 400:
                result = response.json()
                if result.get('status') == 'error':
                    self.log_test("Empty Request", "PASS", "Correctly handled empty request")
                    return True
                else:
                    self.log_test("Empty Request", "FAIL", f"Unexpected response: {result}")
                    return False
            else:
                self.log_test("Empty Request", "FAIL", f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Empty Request", "FAIL", f"Test error: {str(e)}")
            return False
    
    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "="*60)
        print("SENDGRID PASSWORD RECOVERY TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['status'] == 'PASS')
        failed_tests = sum(1 for result in self.test_results if result['status'] == 'FAIL')
        skipped_tests = sum(1 for result in self.test_results if result['status'] == 'SKIP')
        
        print(f"\nSUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        print(f"\nDETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⏭️"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result['message']:
                print(f"   └─ {result['message']}")
        
        # Save report to file
        report_filename = f"sendgrid_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w') as f:
            f.write("SENDGRID PASSWORD RECOVERY TEST REPORT\n")
            f.write("="*50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"SUMMARY:\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n")
            f.write(f"Failed: {failed_tests}\n")
            f.write(f"Skipped: {skipped_tests}\n")
            f.write(f"Success Rate: {(passed_tests/total_tests*100):.1f}%\n\n" if total_tests > 0 else "N/A\n\n")
            
            f.write("DETAILED RESULTS:\n")
            for result in self.test_results:
                f.write(f"{result['timestamp']} - {result['test']}: {result['status']}\n")
                if result['message']:
                    f.write(f"  Message: {result['message']}\n")
                f.write("\n")
        
        print(f"\nReport saved to: {report_filename}")
        
        return passed_tests == total_tests - skipped_tests

def main():
    """Main testing function"""
    print("SendGrid Password Recovery Testing")
    print("="*40)
    
    # Check if server URL is provided as argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    tester = SendGridTester(base_url)
    
    # Generate unique test email
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_email = f"testuser_{timestamp}@example.com"
    
    print(f"Testing with email: {test_email}")
    print(f"Server URL: {base_url}")
    print()
    
    # Run tests
    print("Starting tests...\n")
    
    # Basic connectivity tests
    tester.test_server_connection()
    tester.test_sendgrid_config()
    tester.test_sendgrid_smtp_connection()
    
    # User registration test
    tester.test_user_registration(test_email)
    
    # Password recovery tests
    tester.test_forgot_password_request(test_email)
    tester.test_nonexistent_email()
    tester.test_invalid_email_format()
    tester.test_empty_request()
    
    # Generate report
    success = tester.generate_test_report()
    
    # Provide next steps
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    
    if success:
        print("✅ All tests passed! Your SendGrid integration is working correctly.")
        print("\nTo complete the testing:")
        print("1. Check your email inbox for the password reset email")
        print("2. Click the reset link in the email")
        print("3. Test the password reset form")
        print("4. Verify you can log in with the new password")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print("\nCommon issues and solutions:")
        print("1. Make sure your Flask server is running")
        print("2. Verify SENDGRID_API_KEY is set in environment")
        print("3. Verify MAIL_DEFAULT_SENDER is set in environment")
        print("4. Check SendGrid account status and API key permissions")
        print("5. Ensure the sender email is verified in SendGrid")
    
    print(f"\nTest email used: {test_email}")
    print("You can use this email to manually test the password reset flow.")

if __name__ == "__main__":
    main()
