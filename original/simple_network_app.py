from flask import Flask, render_template, jsonify, Response
import subprocess
import json
import re
import os
import socket
import logging
import concurrent.futures
from queue import Queue
import threading
import dns.resolver

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cola global para almacenar los dispositivos descubiertos
discovered_devices = Queue()

def ping(ip):
    """Ping a single IP address and return True if host is up."""
    try:
        # Ajustar comando ping según el sistema operativo
        if os.name == 'nt':  # Windows
            ping_cmd = ['ping', '-n', '1', '-w', '1000', ip]
        else:  # Unix/Linux/macOS
            ping_cmd = ['ping', '-c', '1', '-W', '1', ip]
            
        # Ejecutar comando ping y capturar salida
        result = subprocess.run(ping_cmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
                              
        # Verificar si obtuvimos una respuesta exitosa
        if os.name == 'nt':  # Windows
            return "TTL=" in result.stdout
        else:  # Unix/Linux/macOS
            return "64 bytes" in result.stdout
    except Exception as e:
        logger.error(f"Error pinging {ip}: {str(e)}")
        return False

def get_device_info(ip):
    """Get device information for a given IP."""
    hostname = None
    
    try:
        # Primer intento: usar gethostbyaddr (método estándar)
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        try:
            # Segundo intento: usar avahi-resolve en Linux (si está disponible)
            if os.name == 'posix' and os.path.exists('/usr/bin/avahi-resolve'):
                try:
                    result = subprocess.check_output(['avahi-resolve', '-a', ip], stderr=subprocess.STDOUT, timeout=1).decode('utf-8')
                    if result:
                        hostname = result.split()[-1].strip()
                except:
                    pass

            # Tercer intento: usar nmblookup para nombres NetBIOS (Windows/Samba)
            if not hostname and os.name == 'posix' and os.path.exists('/usr/bin/nmblookup'):
                try:
                    result = subprocess.check_output(['nmblookup', '-A', ip], stderr=subprocess.STDOUT, timeout=1).decode('utf-8')
                    for line in result.splitlines():
                        if '<00>' in line and not '<GROUP>' in line:
                            hostname = line.split()[0].strip()
                            break
                except:
                    pass

            # Cuarto intento: intentar resolver usando DNS reverso local
            if not hostname:
                try:
                    resolver = dns.resolver.Resolver()
                    resolver.timeout = 1
                    resolver.lifetime = 1
                    addr = dns.reversename.from_address(ip)
                    answer = resolver.resolve(addr, "PTR")
                    if answer:
                        hostname = str(answer[0]).rstrip('.')
                except:
                    pass
        except:
            pass

    # Si no se pudo obtener el hostname, usar un nombre genérico
    if not hostname:
        # Intentar determinar el tipo de dispositivo por el fabricante de la MAC
        try:
            if os.name == 'posix':
                arp_output = subprocess.check_output(['arp', '-n'], stderr=subprocess.STDOUT).decode('utf-8')
                mac_match = re.search(f'{ip}\\s+\\w+\\s+([0-9a-f:]+)', arp_output.lower())
            else:  # Windows
                arp_output = subprocess.check_output(['arp', '-a'], stderr=subprocess.STDOUT).decode('utf-8')
                mac_match = re.search(f'{ip}\\s+([0-9a-f-]+)', arp_output.lower())
            
            if mac_match:
                mac = mac_match.group(1)
                vendor = get_vendor_from_mac(mac)
                if vendor:
                    hostname = f"{vendor}-{ip.split('.')[-1]}"
                else:
                    hostname = f"Device-{ip.split('.')[-1]}"
            else:
                hostname = f"Device-{ip.split('.')[-1]}"
        except:
            hostname = f"Device-{ip.split('.')[-1]}"
    
    # Obtener la MAC address
    try:
        if os.name == 'posix':
            arp_output = subprocess.check_output(['arp', '-n'], stderr=subprocess.STDOUT).decode('utf-8')
            mac_match = re.search(f'{ip}\\s+\\w+\\s+([0-9a-f:]+)', arp_output.lower())
        else:  # Windows
            arp_output = subprocess.check_output(['arp', '-a'], stderr=subprocess.STDOUT).decode('utf-8')
            mac_match = re.search(f'{ip}\\s+([0-9a-f-]+)', arp_output.lower())
        
        mac = mac_match.group(1) if mac_match else "Unknown"
    except:
        mac = "Unknown"
    
    # Determinar si es un router basado en el patrón de IP y nombre
    is_router = (
        ip.endswith('.1') or 
        ip.endswith('.254') or 
        'router' in hostname.lower() or 
        'gateway' in hostname.lower()
    )
    
    return {
        'id': ip.split('.')[-1],  # Usar el último octeto como ID
        'name': hostname,
        'ip': ip,
        'mac': mac,
        'type': 'router' if is_router else 'device'
    }

def get_vendor_from_mac(mac):
    """Get vendor name from MAC address using common prefixes."""
    # Normalizar el formato de la MAC
    mac = mac.replace('-', ':').lower()
    prefix = mac[:8]  # Tomar los primeros 3 bytes (XX:XX:XX)
    
    # Diccionario de prefijos MAC comunes y sus fabricantes
    vendors = {
        '00:50:56': 'VMware',
        '00:0c:29': 'VMware',
        '00:1c:14': 'VMware',
        '00:1c:42': 'Parallels',
        '08:00:27': 'VirtualBox',
        'dc:a6:32': 'Raspberry',
        'b8:27:eb': 'Raspberry',
        '00:1a:11': 'Google',
        'f4:03:43': 'Apple',
        '00:14:22': 'Dell',
        '00:50:ba': 'HP',
        '00:21:b7': 'Lenovo',
        '00:26:18': 'ASUSTek',
        '00:1f:3a': 'Intel',
        '00:e0:4c': 'Realtek',
        'd8:3a:dd': 'Intel',
        '00:25:90': 'Super Micro',
        '00:1b:21': 'Intel',
        '00:1e:67': 'Intel'
    }
    
    return vendors.get(prefix)

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
        
        # Lista para almacenar los dispositivos encontrados
        found_devices = []
        
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
                        found_devices.append(device_info)
                except Exception as e:
                    logger.error(f"Error processing {ip}: {str(e)}")
        
        # Enviar señal de finalización
        discovered_devices.put({'status': 'complete'})
        
    except Exception as e:
        logger.error(f"Error during network scan: {str(e)}")
        discovered_devices.put({'status': 'error', 'message': str(e)})

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'simple-network-app'
    
    @app.route('/')
    def index():
        """Página principal que muestra solo los dispositivos de red."""
        return render_template('simple_network.html')
    
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
