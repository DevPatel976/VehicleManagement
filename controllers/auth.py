from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.is_blocked:
                flash('Your account has been blocked. Please contact support for assistance.', 'danger')
            elif user.check_password(password):
                login_user(user)
                flash('Logged in successfully!', 'success')
                if user.is_admin:
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('user.dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        else:
            flash('Invalid username or password', 'danger')
    return render_template('auth/login.html')
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        user = User(
            username=username,
            email=email,
            is_admin=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))