from flask import Flask, render_template, jsonify, request
from network_scanner import NetworkScanner
import json
import os

app = Flask(__name__)
scanner = NetworkScanner()

# Archivo para guardar redes
SAVED_NETWORKS_FILE = 'saved_networks.json'

def load_saved_networks():
    """Cargar redes guardadas desde archivo"""
    if os.path.exists(SAVED_NETWORKS_FILE):
        try:
            with open(SAVED_NETWORKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_networks_to_file(networks):
    """Guardar redes en archivo"""
    try:
        with open(SAVED_NETWORKS_FILE, 'w') as f:
            json.dump(networks, f, indent=2)
        return True
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan')
def scan():
    # Detectar red local automáticamente
    network = scanner.get_local_network()
    
    # Escanear la red
    devices = scanner.scan_network(network)
    
    return jsonify({
        'network': network,
        'devices': devices,
        'total': len(devices)
    })

@app.route('/scan/<path:network>')
def scan_custom(network):
    # Escanear red personalizada
    devices = scanner.scan_network(network)
    
    return jsonify({
        'network': network,
        'devices': devices,
        'total': len(devices)
    })

@app.route('/scan_custom', methods=['POST'])
def scan_custom_post():
    data = request.get_json()
    network = data.get('network', '')
    
    # Escanear red personalizada
    devices = scanner.scan_network(network)
    
    return jsonify({
        'network': network,
        'devices': devices,
        'total': len(devices)
    })

@app.route('/saved_networks', methods=['GET'])
def get_saved_networks():
    """Obtener lista de redes guardadas"""
    networks = load_saved_networks()
    return jsonify({'networks': networks})

@app.route('/save_network', methods=['POST'])
def save_network():
    """Guardar una nueva red"""
    data = request.get_json()
    network = data.get('network', '').strip()
    name = data.get('name', '').strip()
    
    if not network or not name:
        return jsonify({'success': False, 'message': 'Network and name are required'})
    
    # Cargar redes existentes
    networks = load_saved_networks()
    
    # Verificar si ya existe
    for net in networks:
        if net['network'] == network:
            return jsonify({'success': False, 'message': 'Network already saved'})
    
    # Agregar nueva red
    networks.append({
        'name': name,
        'network': network
    })
    
    # Guardar en archivo
    if save_networks_to_file(networks):
        return jsonify({'success': True, 'message': 'Network saved successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error saving network'})

@app.route('/delete_network', methods=['POST'])
def delete_network():
    """Eliminar una red guardada"""
    data = request.get_json()
    network = data.get('network', '')
    
    # Cargar redes existentes
    networks = load_saved_networks()
    
    # Filtrar la red a eliminar
    networks = [net for net in networks if net['network'] != network]
    
    # Guardar cambios
    if save_networks_to_file(networks):
        return jsonify({'success': True, 'message': 'Network deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error deleting network'})

@app.route('/scan_all_saved', methods=['POST'])
def scan_all_saved():
    """Escanear todas las redes guardadas"""
    networks = load_saved_networks()
    all_devices = []
    scanned_networks = []
    
    for net_info in networks:
        network = net_info['network']
        devices = scanner.scan_network(network)
        all_devices.extend(devices)
        scanned_networks.append({
            'name': net_info['name'],
            'network': network,
            'devices': len(devices)
        })
    
    return jsonify({
        'networks': scanned_networks,
        'devices': all_devices,
        'total': len(all_devices)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
