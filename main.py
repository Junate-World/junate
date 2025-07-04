from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
from sqlalchemy import or_
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SUPABASE_DATABASE_URL', 'sqlite:///tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')  # REQUIRED for session management and Flask-Login
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Flask-Mail and SendGrid configuration
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'  # This is the literal string 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
mail = Mail(app)

# Token serializer for password reset
serializer = URLSafeTimedSerializer(app.secret_key)

db = SQLAlchemy(app)

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(500), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    site_name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

def init_db():
    with app.app_context():
        db.create_all()

init_db()  # Ensure tables are created on every startup

@app.route('/')
def home():
    user_count = User.query.count()
    if current_user.is_authenticated:
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        active_count = Task.query.filter_by(user_id=current_user.id, status='Active').count()
        onhold_count = Task.query.filter_by(user_id=current_user.id, status='On hold').count()
        closed_count = Task.query.filter_by(user_id=current_user.id, status='Closed').count()
    else:
        total_tasks = active_count = onhold_count = closed_count = None
    return render_template('home.html', total_tasks=total_tasks, active_count=active_count, onhold_count=onhold_count, closed_count=closed_count, user_count=user_count)

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    total_tasks = len(tasks)
    active_count = sum(1 for t in tasks if t.status == 'Active')
    onhold_count = sum(1 for t in tasks if t.status == 'On hold')
    closed_count = sum(1 for t in tasks if t.status == 'Closed')
    return render_template('dashboard.html', tasks=tasks, total_tasks=total_tasks, active_count=active_count, onhold_count=onhold_count, closed_count=closed_count)

@app.route('/add', methods=['POST'])
@login_required
def add_task():
    data = request.json if request.is_json else None
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    task = data.get('task')
    owner = data.get('owner')
    contact = data.get('contact')
    if not task or not owner or not contact:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    new_task = Task()
    new_task.task = task
    new_task.owner = owner
    new_task.contact = contact
    new_task.summary = data.get('summary', '')
    new_task.phone = data.get('phone', '')
    new_task.site_name = data.get('site_name', '')
    new_task.status = data.get('status', 'Active')
    new_task.user_id = current_user.id
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'id': new_task.id, 'task': new_task.task, 'owner': new_task.owner, 'contact': new_task.contact, 'summary': new_task.summary, 'phone': new_task.phone, 'site_name': new_task.site_name, 'created_at': new_task.created_at.isoformat(), 'status': new_task.status})

@app.route('/update', methods=['POST'])
@login_required
def update_task():
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    task = Task.query.filter_by(id=data['id'], user_id=current_user.id).first()
    if task:
        task.task = data['task']
        task.owner = data['owner']
        task.contact = data['contact']
        task.summary = data.get('summary', '')
        task.phone = data.get('phone', '')
        task.site_name = data.get('site_name', '')
        task.status = data.get('status', task.status)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 404

@app.route('/delete/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'status': 'deleted'})
    return jsonify({'status': 'error'}), 404

@app.route('/task/<int:task_id>')
@login_required
def view_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    return render_template('task_view.html', task=task)

@app.route('/search')
@login_required
def search_tasks():
    q = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'task')
    if not q:
        return jsonify([])
    if search_type == 'owner':
        tasks = Task.query.filter(Task.owner.ilike(f'%{q}%'), Task.user_id == current_user.id).all()
    elif search_type == 'site_name':
        tasks = Task.query.filter(Task.site_name.ilike(f'%{q}%'), Task.user_id == current_user.id).all()
    else:
        tasks = Task.query.filter(Task.task.ilike(f'%{q}%'), Task.user_id == current_user.id).all()
    return jsonify([
        {
            'id': t.id,
            'task': t.task,
            'owner': t.owner,
            'contact': t.contact,
            'summary': t.summary,
            'phone': t.phone,
            'site_name': t.site_name,
            'created_at': t.created_at.isoformat() if t.created_at else '',
            'status': t.status
        } for t in tasks
    ])

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/register', methods=['POST'])
def register():
    data = request.json if request.is_json else None
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    if not full_name or not email or not password:
        return jsonify({'status': 'error', 'message': 'Full name, email, and password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'Email already registered'}), 400
    user = User()
    user.full_name = full_name
    user.email = email
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({'status': 'success'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json if request.is_json else None
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        login_user(user)
        session.permanent = True  # Enable session timeout
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/forgot', methods=['POST'])
def forgot_password():
    data = request.json if request.is_json else None
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    email = data.get('email', '').strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'No account with that email'}), 404
    # Generate token
    token = serializer.dumps(email, salt='password-reset-salt')
    reset_url = url_for('reset_password_token', token=token, _external=True)
    # Send email
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f'Click the link to reset your password: {reset_url}\nIf you did not request this, please ignore this email.'
    mail.send(msg)
    return jsonify({'status': 'success', 'message': 'Password reset instructions sent to your email.'})

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour expiry
    except SignatureExpired:
        return render_template('reset_password.html', error='The reset link has expired.'), 400
    except BadSignature:
        return render_template('reset_password.html', error='Invalid or tampered reset link.'), 400
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not password or not confirm:
            return render_template('reset_password.html', error='All fields are required.', token=token)
        if password != confirm:
            return render_template('reset_password.html', error='Passwords do not match.', token=token)
        user = User.query.filter_by(email=email).first()
        if not user:
            return render_template('reset_password.html', error='No account with that email.'), 400
        user.set_password(password)
        db.session.commit()
        return render_template('reset_password.html', success='Your password has been reset. You can now log in.')
    return render_template('reset_password.html', token=token)

@app.route('/user')
@login_required
def user_page():
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    active_count = Task.query.filter_by(user_id=current_user.id, status='Active').count()
    onhold_count = Task.query.filter_by(user_id=current_user.id, status='On hold').count()
    closed_count = Task.query.filter_by(user_id=current_user.id, status='Closed').count()
    return render_template('user.html', total_tasks=total_tasks, active_count=active_count, onhold_count=onhold_count, closed_count=closed_count)

if __name__ == '__main__':
    app.run(debug=True)
