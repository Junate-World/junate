#!/usr/bin/env python3
"""
SendGrid Setup and Configuration Helper
This script helps set up SendGrid environment variables and test the configuration.
"""

import os
import sys
import getpass
from datetime import datetime

def setup_environment():
    """Interactive setup for SendGrid environment variables"""
    print("SendGrid Configuration Setup")
    print("="*40)
    print()
    
    # Check current environment
    current_api_key = os.environ.get('SENDGRID_API_KEY')
    current_sender = os.environ.get('MAIL_DEFAULT_SENDER')
    
    print("Current Configuration:")
    print(f"SENDGRID_API_KEY: {'*' * 10 + current_api_key[-4:] if current_api_key else 'Not set'}")
    print(f"MAIL_DEFAULT_SENDER: {current_sender or 'Not set'}")
    print()
    
    # Get SendGrid API Key
    print("SendGrid API Key Setup:")
    print("- Go to https://app.sendgrid.com/settings/api_keys")
    print("- Create a new API key with 'Mail Send' permissions")
    print("- Copy the API key (it starts with 'SG.')")
    print()
    
    api_key = getpass.getpass("Enter your SendGrid API Key (input will be hidden): ").strip()
    
    if not api_key:
        print("❌ API Key is required!")
        return False
    
    if not api_key.startswith('SG.'):
        print("❌ Invalid API Key format. SendGrid API keys start with 'SG.'")
        return False
    
    # Get sender email
    print("\nSender Email Setup:")
    print("- This email must be verified in your SendGrid account")
    print("- Go to https://app.sendgrid.com/settings/sender_auth")
    print("- Verify your sender email address")
    print()
    
    sender_email = input("Enter your verified sender email: ").strip()
    
    if not sender_email or '@' not in sender_email:
        print("❌ Valid email address is required!")
        return False
    
    # Create .env file
    env_content = f"""# SendGrid Configuration
SENDGRID_API_KEY={api_key}
MAIL_DEFAULT_SENDER={sender_email}

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Configuration saved to .env file")
    print("\nTo use these environment variables:")
    print("1. Install python-dotenv: pip install python-dotenv")
    print("2. Add this to the top of your main.py:")
    print("   from dotenv import load_dotenv")
    print("   load_dotenv()")
    print("3. Or set them manually in your system environment")
    
    return True

def test_sendgrid_connection():
    """Test SendGrid connection with current configuration"""
    print("\n" + "="*40)
    print("Testing SendGrid Connection")
    print("="*40)
    
    api_key = os.environ.get('SENDGRID_API_KEY')
    sender_email = os.environ.get('MAIL_DEFAULT_SENDER')
    
    if not api_key:
        print("❌ SENDGRID_API_KEY not found in environment")
        return False
    
    if not sender_email:
        print("❌ MAIL_DEFAULT_SENDER not found in environment")
        return False
    
    print(f"API Key: {'*' * 10 + api_key[-4:]}")
    print(f"Sender Email: {sender_email}")
    print()
    
    try:
        import smtplib
        
        print("Testing SMTP connection...")
        server = smtplib.SMTP('smtp.sendgrid.net', 587)
        server.starttls()
        server.login('apikey', api_key)
        server.quit()
        
        print("✅ SMTP connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ SMTP connection failed: {str(e)}")
        print("\nCommon issues:")
        print("1. API key is invalid or expired")
        print("2. API key doesn't have 'Mail Send' permissions")
        print("3. Sender email is not verified in SendGrid")
        print("4. Network connectivity issues")
        return False

def create_test_email():
    """Create a test email to verify SendGrid is working"""
    print("\n" + "="*40)
    print("SendGrid Test Email")
    print("="*40)
    
    api_key = os.environ.get('SENDGRID_API_KEY')
    sender_email = os.environ.get('MAIL_DEFAULT_SENDER')
    
    if not api_key or not sender_email:
        print("❌ SendGrid configuration not found")
        return False
    
    test_email = input("Enter test recipient email: ").strip()
    
    if not test_email or '@' not in test_email:
        print("❌ Valid email address required")
        return False
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = test_email
        msg['Subject'] = f"SendGrid Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""
        This is a test email from your SendGrid integration.
        
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Sender: {sender_email}
        
        If you receive this email, your SendGrid configuration is working correctly!
        
        Best regards,
        Your Project Management Tool
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print("Sending test email...")
        server = smtplib.SMTP('smtp.sendgrid.net', 587)
        server.starttls()
        server.login('apikey', api_key)
        text = msg.as_string()
        server.sendmail(sender_email, test_email, text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"Check the inbox of {test_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {str(e)}")
        return False

def main():
    """Main function"""
    print("SendGrid Setup and Testing Tool")
    print("="*40)
    print()
    
    while True:
        print("Choose an option:")
        print("1. Setup SendGrid configuration")
        print("2. Test SendGrid connection")
        print("3. Send test email")
        print("4. Run full test suite")
        print("5. Exit")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            setup_environment()
        elif choice == '2':
            test_sendgrid_connection()
        elif choice == '3':
            create_test_email()
        elif choice == '4':
            print("\nRunning full test suite...")
            if test_sendgrid_connection():
                create_test_email()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        print("\n" + "-"*40 + "\n")

if __name__ == "__main__":
    main()
