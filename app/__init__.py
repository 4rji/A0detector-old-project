from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv
import subprocess
import json
import re
import os
import socket
import logging
import concurrent.futures
from queue import Queue
import threading
from .network_scanner import ping, get_device_info

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cola global para almacenar los dispositivos descubiertos
discovered_devices = Queue()

def get_device_info(ip):
    """Get device information for a given IP."""
    try:
        # Intentar obtener el hostname
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        hostname = f"Device-{ip.split('.')[-1]}"
    
    # Intentar obtener la MAC address usando arp
    try:
        if os.name == 'posix':  # Linux/Mac
            arp_output = subprocess.check_output(['arp', '-n'], stderr=subprocess.STDOUT).decode('utf-8')
            mac_match = re.search(f'{ip}\\s+\\w+\\s+([0-9a-f:]+)', arp_output.lower())
        else:  # Windows
            arp_output = subprocess.check_output(['arp', '-a'], stderr=subprocess.STDOUT).decode('utf-8')
            mac_match = re.search(f'{ip}\\s+([0-9a-f-]+)', arp_output.lower())
        
        mac = mac_match.group(1) if mac_match else "Unknown"
    except:
        mac = "Unknown"
    
    # Determinar si es un router basado en el patrón de IP
    is_router = ip.endswith('.1') or ip.endswith('.254')
    
    return {
        'id': ip.split('.')[-1],  # Usar el último octeto como ID
        'name': hostname,
        'ip': ip,
        'mac': mac,
        'type': 'router' if is_router else 'device'
    }

def load_settings():
    """Load network settings from settings.json"""
    try:
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                return settings.get('subnets', ['192.168.1'])
        return ['192.168.1']  # Default subnet if no settings file
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return ['192.168.1']  # Default subnet on error

def scan_network_worker():
    """Worker function to perform network scanning in background."""
    try:
        logger.info("Starting network scan...")
        
        # Cargar subredes configuradas
        subnets = load_settings()
        logger.info(f"Scanning configured subnets: {subnets}")
        
        # Crear lista de IPs a escanear para cada subred
        ips_to_scan = []
        for subnet in subnets:
            # Asegurar que la subred tenga el formato correcto
            base_subnet = subnet.rstrip('.')  # Eliminar punto final si existe
            ips_to_scan.extend([f"{base_subnet}.{i}" for i in range(1, 255)])
        
        logger.info(f"Total IPs to scan: {len(ips_to_scan)}")
        
        # Usar ThreadPoolExecutor para hacer ping en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            # Mapear las IPs a la función ping
            future_to_ip = {executor.submit(ping, ip): ip for ip in ips_to_scan}
            
            # Procesar los resultados conforme se completan
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    if future.result():  # Si el ping fue exitoso
                        logger.info(f"Found active host: {ip}")
                        device_info = get_device_info(ip)
                        discovered_devices.put(device_info)
                except Exception as e:
                    logger.error(f"Error processing {ip}: {str(e)}")
        
        # Enviar señal de finalización
        discovered_devices.put({'status': 'complete'})
        
    except Exception as e:
        logger.error(f"Error during network scan: {str(e)}")
        discovered_devices.put({'status': 'error', 'message': str(e)})

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production

    from .auth import auth
    from .dashboard import dashboard
    
    app.register_blueprint(auth)
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    
    @app.route('/scan_network', methods=['POST'])
    def start_network_scan():
        """Endpoint to start network scanning process."""
        # Limpiar la cola de dispositivos descubiertos
        while not discovered_devices.empty():
            discovered_devices.get()
        
        # Iniciar el escaneo en un hilo separado
        scan_thread = threading.Thread(target=scan_network_worker)
        scan_thread.daemon = True
        scan_thread.start()
        
        return jsonify({'status': 'started'})
    
    @app.route('/scan_network/events')
    def network_scan_events():
        """Endpoint for Server-Sent Events to receive real-time updates."""
        def generate():
            while True:
                try:
                    # Obtener el siguiente dispositivo o mensaje de estado
                    data = discovered_devices.get(timeout=30)
                    
                    # Si es un mensaje de estado, enviar y terminar
                    if isinstance(data, dict) and 'status' in data:
                        yield f"data: {json.dumps(data)}\n\n"
                        if data['status'] in ['complete', 'error']:
                            break
                        continue
                    
                    # Enviar el dispositivo descubierto
                    yield f"data: {json.dumps({'device': data})}\n\n"
                    
                except Exception as e:
                    logger.error(f"Error in event stream: {str(e)}")
                    yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
                    break
        
        return Response(generate(), mimetype='text/event-stream')

    return app