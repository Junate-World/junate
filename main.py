from flask import Flask, render_template
import os
from datetime import timedelta
from flask_login import LoginManager, current_user
from flask_mail import Mail
from models import db, User
from auth import auth_bp
from tasks import tasks_bp
from chatbot import chatbot_bp  # If you modularize chatbot
from sqlalchemy import text, inspect

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, continue without it

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SUPABASE_DATABASE_URL', 'sqlite:///tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

db.init_app(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()
    # Lightweight migration to add cost columns if missing
    try:
        inspector = inspect(db.engine)
        columns = {col['name'] for col in inspector.get_columns('task')}
        if 'project_cost' not in columns:
            db.session.execute(text('ALTER TABLE task ADD COLUMN project_cost INTEGER NOT NULL DEFAULT 0'))
        if 'execution_cost' not in columns:
            db.session.execute(text('ALTER TABLE task ADD COLUMN execution_cost INTEGER NOT NULL DEFAULT 0'))
        db.session.commit()
    except Exception:
        db.session.rollback()

app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(chatbot_bp)  # If you modularize chatbot

@app.route('/')
def home():
    user_count = User.query.count()
    if current_user.is_authenticated:
        from models import Task
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        active_count = Task.query.filter_by(user_id=current_user.id, status='Active').count()
        onhold_count = Task.query.filter_by(user_id=current_user.id, status='On hold').count()
        closed_count = Task.query.filter_by(user_id=current_user.id, status='Closed').count()
    else:
        total_tasks = active_count = onhold_count = closed_count = None
    return render_template('home.html', total_tasks=total_tasks, active_count=active_count, onhold_count=onhold_count, closed_count=closed_count, user_count=user_count)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
