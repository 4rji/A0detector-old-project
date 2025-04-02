from flask import Blueprint, render_template, jsonify, request, session
import json
import os

dashboard = Blueprint('dashboard', __name__)

SETTINGS_FILE = 'settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {'subnets': ['192.168.140', '192.168.141', '192.168.142']}  # Default subnets

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

@dashboard.route('/')
def index():
    return render_template('dashboard/index.html')

@dashboard.route('/network-devices')
def network_devices():
    return render_template('dashboard/network_devices.html')

@dashboard.route('/settings')
def settings():
    return render_template('dashboard/settings.html')

@dashboard.route('/settings/subnets', methods=['GET', 'POST', 'DELETE'])
def manage_subnets():
    settings = load_settings()
    
    if request.method == 'GET':
        return jsonify({'subnets': settings['subnets']})
    
    elif request.method == 'POST':
        data = request.get_json()
        subnet = data.get('subnet')
        
        if not subnet:
            return jsonify({'success': False, 'message': 'No subnet provided'})
        
        if subnet in settings['subnets']:
            return jsonify({'success': False, 'message': 'Subnet already exists'})
        
        settings['subnets'].append(subnet)
        save_settings(settings)
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        data = request.get_json()
        subnet = data.get('subnet')
        
        if not subnet:
            return jsonify({'success': False, 'message': 'No subnet provided'})
        
        if subnet not in settings['subnets']:
            return jsonify({'success': False, 'message': 'Subnet not found'})
        
        settings['subnets'].remove(subnet)
        save_settings(settings)
        return jsonify({'success': True}) 