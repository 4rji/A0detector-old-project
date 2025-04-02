from flask import Flask, jsonify, request
from dotenv import load_dotenv
import subprocess
import json
import re
import os
import socket
import logging
import concurrent.futures

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def ping(ip):
    """Ping a single IP address and return True if host is up."""
    try:
        # Run ping command and capture output
        result = subprocess.run(['ping', '-c', '1', ip], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
        # Check if we got a successful response (64 bytes)
        return "64 bytes" in result.stdout
    except:
        return False

def get_device_info(ip):
    """Get device information for a given IP."""
    try:
        # Intentar obtener el hostname
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        hostname = f"Device-{ip.split('.')[-1]}"
    
    # Intentar obtener la MAC address usando arp
    try:
        arp_output = subprocess.check_output(['arp', '-n'], stderr=subprocess.STDOUT).decode('utf-8')
        mac_match = re.search(f'{ip}\\s+\\w+\\s+([0-9a-f:]+)', arp_output.lower())
        mac = mac_match.group(1) if mac_match else "Unknown"
    except:
        mac = "Unknown"
    
    # Determinar si es un router basado en el patrón de IP
    is_router = ip.endswith('.1') or ip.endswith('.254')
    
    return {
        'name': hostname,
        'ip': ip,
        'mac': mac,
        'type': 'router' if is_router else 'device'
    }

def get_network_ip():
    """Get the real network IP address of the machine."""
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # We don't actually connect, we just use this to get the local IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # Fallback to hostname if the above method fails
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production

    from .auth import auth
    from .dashboard import dashboard
    
    app.register_blueprint(auth)
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    
    @app.route('/scan_network', methods=['POST'])
    def scan_network():
        """Endpoint to scan the network for connected devices using ping sweep."""
        try:
            logger.info("Starting network scan...")
            devices = []
            
            # Obtener la IP real de la red
            ip_addr = get_network_ip()
            subnet = '.'.join(ip_addr.split('.')[:3])
            
            logger.info(f"Using network IP: {ip_addr}")
            logger.info(f"Scanning subnet: {subnet}.0/24")
            
            # Crear lista de IPs a escanear
            ips_to_scan = [f"{subnet}.{i}" for i in range(1, 255)]
            
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
                            devices.append(device_info)
                    except Exception as e:
                        logger.error(f"Error processing {ip}: {str(e)}")
            
            # Asignar IDs únicos
            for i, device in enumerate(devices):
                device['id'] = i + 1
            
            logger.info(f"Scan complete. Found {len(devices)} devices")
            return jsonify({'devices': devices})
            
        except Exception as e:
            logger.error(f"Error during network scan: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return app