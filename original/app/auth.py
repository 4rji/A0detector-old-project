from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    return redirect(url_for('dashboard.network_devices'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect directly to network devices without login
    return redirect(url_for('dashboard.network_devices'))

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('dashboard.network_devices'))

@auth.route('/dashboard')
def dashboard():
    return render_template("dashboard.html") 