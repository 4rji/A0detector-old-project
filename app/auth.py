from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Accept any credentials
        session['user_id'] = 1  # Simple session management
        return redirect(url_for('dashboard.network_devices'))
    return render_template("login.html")

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))

@auth.route('/dashboard')
def dashboard():
    return render_template("dashboard.html") 