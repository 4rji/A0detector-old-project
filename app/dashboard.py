from flask import Blueprint, render_template

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def index():
    return render_template('dashboard/index.html')

@dashboard.route('/network-devices')
def network_devices():
    return render_template('dashboard/network_devices.html')

@dashboard.route('/settings')
def settings():
    return render_template('dashboard/settings.html') 