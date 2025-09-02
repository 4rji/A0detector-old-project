from flask import Flask, render_template, jsonify
from network_scanner import NetworkScanner
import json

app = Flask(__name__)
scanner = NetworkScanner()

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
    from flask import request
    data = request.get_json()
    network = data.get('network', '')
    
    # Escanear red personalizada
    devices = scanner.scan_network(network)
    
    return jsonify({
        'network': network,
        'devices': devices,
        'total': len(devices)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
