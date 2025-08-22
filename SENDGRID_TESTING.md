# SendGrid Password Recovery Testing Guide

This guide will help you test the SendGrid password recovery functionality in your project management tool.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.7+
- Flask application running
- SendGrid account with API key
- Verified sender email in SendGrid

### 2. Install Dependencies

```bash
pip install python-dotenv requests
```

### 3. Setup SendGrid Configuration

#### Option A: Interactive Setup (Recommended)
```bash
python setup_sendgrid.py
```

#### Option B: Manual Setup
1. Create a `.env` file in your project root:
```env
SENDGRID_API_KEY=your_sendgrid_api_key_here
MAIL_DEFAULT_SENDER=your_verified_sender@example.com
SECRET_KEY=your-secret-key-here
```

2. Get your SendGrid API Key:
   - Go to [SendGrid API Keys](https://app.sendgrid.com/settings/api_keys)
   - Create a new API key with "Mail Send" permissions
   - Copy the API key (starts with "SG.")

3. Verify your sender email:
   - Go to [SendGrid Sender Authentication](https://app.sendgrid.com/settings/sender_auth)
   - Verify your sender email address

## 🧪 Testing Methods

### Method 1: Automated Test Suite

Run the comprehensive test suite:

```bash
python test_sendgrid.py
```

This will:
- ✅ Test server connectivity
- ✅ Verify SendGrid configuration
- ✅ Test SMTP connection
- ✅ Register a test user
- ✅ Test password recovery request
- ✅ Test error handling scenarios
- ✅ Generate a detailed test report

### Method 2: Manual Testing

#### Step 1: Start Your Flask Server
```bash
python main.py
```

#### Step 2: Test User Registration
1. Go to `http://localhost:5000`
2. Click "Sign Up"
3. Register a test user with a real email address

#### Step 3: Test Password Recovery
1. Click "Login"
2. Click "Forgot password?"
3. Enter the email address you used for registration
4. Click "Send Reset Link"

#### Step 4: Check Email
1. Check your email inbox
2. Look for an email with subject "Password Reset Request"
3. Click the reset link in the email

#### Step 5: Reset Password
1. Enter a new password
2. Confirm the password
3. Click "Reset Password"
4. Try logging in with the new password

### Method 3: Direct API Testing

Test the API endpoints directly:

```bash
# Test forgot password endpoint
curl -X POST http://localhost:5000/forgot \
  -H "Content-Type: application/json" \
  -d '{"email": "your-test-email@example.com"}'
```

## 🔍 Test Scenarios

### ✅ Happy Path Testing
- [ ] User registration with valid email
- [ ] Password recovery request for existing user
- [ ] Email delivery confirmation
- [ ] Password reset link functionality
- [ ] New password login verification

### ❌ Error Handling Testing
- [ ] Password recovery for non-existent email
- [ ] Invalid email format handling
- [ ] Empty request handling
- [ ] Expired reset token handling
- [ ] Invalid reset token handling

### 🔧 Configuration Testing
- [ ] Missing API key handling
- [ ] Invalid API key handling
- [ ] Unverified sender email handling
- [ ] Network connectivity issues

## 📊 Test Results

After running the test suite, you'll get a detailed report including:

- **Test Summary**: Total tests, passed, failed, success rate
- **Detailed Results**: Individual test results with timestamps
- **Error Messages**: Specific error details for failed tests
- **Next Steps**: Guidance on what to do next

## 🐛 Troubleshooting

### Common Issues

#### 1. "SENDGRID_API_KEY not found"
**Solution**: Set the environment variable or use the setup script

#### 2. "SMTP connection failed"
**Possible Causes**:
- Invalid API key
- API key doesn't have "Mail Send" permissions
- Network connectivity issues

**Solutions**:
- Verify API key in SendGrid dashboard
- Check API key permissions
- Test network connectivity

#### 3. "Email not received"
**Possible Causes**:
- Sender email not verified
- Email in spam folder
- SendGrid account issues

**Solutions**:
- Verify sender email in SendGrid
- Check spam/junk folder
- Check SendGrid account status

#### 4. "Server connection failed"
**Solution**: Make sure your Flask server is running on the correct port

### Debug Mode

Enable debug logging by adding to your Flask app:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📧 Email Templates

The current email template is simple text. You can enhance it by modifying the `forgot_password()` function in `auth.py`:

```python
msg.html = f"""
<html>
<body>
    <h2>Password Reset Request</h2>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_url}">Reset Password</a>
    <p>If you didn't request this, please ignore this email.</p>
    <p>This link expires in 1 hour.</p>
</body>
</html>
"""
```

## 🔒 Security Considerations

- Reset tokens expire after 1 hour
- Tokens are cryptographically signed
- Passwords are hashed using werkzeug
- HTTPS should be used in production
- Rate limiting should be implemented

## 📈 Monitoring

Monitor your SendGrid usage:
- [SendGrid Dashboard](https://app.sendgrid.com/statistics)
- Email delivery rates
- Bounce rates
- Spam reports

## 🚀 Production Deployment

For production:
1. Use environment variables (not .env files)
2. Enable HTTPS
3. Implement rate limiting
4. Monitor email delivery
5. Set up proper logging
6. Use a production-grade database

## 📞 Support

If you encounter issues:
1. Check the test report for specific errors
2. Verify SendGrid configuration
3. Check Flask server logs
4. Test with the setup script
5. Review this troubleshooting guide

---

**Happy Testing! 🎉**
