from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Accept any credentials
        return redirect(url_for('auth.dashboard'))
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return redirect(url_for('auth.login'))

@auth.route('/dashboard')
def dashboard():
    return render_template("dashboard.html") 