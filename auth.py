from flask import Blueprint, request, jsonify, session, redirect, render_template, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import os

auth_bp = Blueprint('auth', __name__)
serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'dev-secret-key'))

@auth_bp.route('/register', methods=['POST'])
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

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json if request.is_json else None
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        login_user(user)
        session.permanent = True
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@auth_bp.route('/forgot', methods=['POST'])
def forgot_password():
    from main import mail
    data = request.json if request.is_json else None
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    email = data.get('email', '').strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'No account with that email'}), 404
    token = serializer.dumps(email, salt='password-reset-salt')
    reset_url = url_for('auth.reset_password_token', token=token, _external=True)
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f'Click the link to reset your password: {reset_url}\nIf you did not request this, please ignore this email.'
    mail.send(msg)
    return jsonify({'status': 'success', 'message': 'Password reset instructions sent to your email.'})

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
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