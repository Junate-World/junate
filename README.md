📝 Task Manager App (Flask + SendGrid)
A simple Flask-based task management application with user registration, login, password reset functionality (via email), and basic CRUD operations on tasks. Password reset is powered by SendGrid through Flask-Mail.

🚀 Features
User registration and login system

Password reset with secure email tokens

Task creation, editing, deletion, and search

Dashboard with task status counts

SQLite database

REST-style API endpoints for task management

Secure password hashing with werkzeug

Session management with Flask-Login

📦 Requirements
Python 3.7+

Virtualenv (recommended)

Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
🔧 Configuration
1. Environment Variables
Create a .env file or set these in your system environment:

env
Copy
Edit
SENDGRID_API_KEY=your_sendgrid_api_key
MAIL_DEFAULT_SENDER=your_verified_sender@example.com
You may also hardcode these in app.config (not recommended for production).

2. Database Initialization
SQLite will be used as the database.

On first run, the app creates tasks.db automatically:

bash
Copy
Edit
python app.py
✉️ Password Reset Flow
When a user forgets their password:

User submits email via /forgot endpoint.

A secure tokenized URL is emailed using SendGrid.

User clicks the link and resets their password at /reset_password/<token>.

Token is valid for 1 hour and uses Flask’s itsdangerous module for signing.

🛡️ Security Notes
Passwords are hashed using werkzeug.security.

Email reset links are time-limited and tamper-resistant.

Sessions are managed securely with Flask-Login.

🧪 Endpoints Overview
Route	Method	Auth Required	Description
/register	POST	❌	Register new user
/login	POST	❌	Login existing user
/logout	POST	✅	Logout current user
/forgot	POST	❌	Request password reset email
/reset_password/<token>	GET/POST	❌	Reset password via emailed link
/dashboard	GET	✅	View user dashboard and tasks
/add	POST	✅	Add a new task
/update	POST	✅	Update a task
/delete/<id>	DELETE	✅	Delete a task
/search	GET	✅	Search tasks by owner/site/task
/user	GET	✅	View user's task summary

🖥️ Running the App
bash
Copy
Edit
python app.py
Visit: http://localhost:5000

📁 File Structure
arduino
Copy
Edit
.
├── app.py
├── templates/
│   ├── home.html
│   ├── dashboard.html
│   ├── reset_password.html
│   ├── user.html
│   └── task_view.html
├── static/
├── tasks.db
└── README.md
📬 Email Setup (SendGrid)
Set MAIL_USERNAME = 'apikey'

Set MAIL_PASSWORD = your actual API key

Your SendGrid account must have a verified sender email

🔐 Important Security Tip
If you're temporarily using a Full Access API Key due to SendGrid UI issues, ensure that:

You limit its use to only sending emails in your app logic.

You rotate it with a Restricted Access (Mail Send) key as soon as possible.

✅ TODO / Suggestions
 Add unit tests

 Enable CSRF protection for form POSTs

 Add pagination to task views

 Migrate from SQLite to PostgreSQL for production

📄 License
MIT — free for personal or commercial use.#   j u n a t e  
 #   j u n a t e  
 #   j u n a t e  
 #   j u n a t e  
 