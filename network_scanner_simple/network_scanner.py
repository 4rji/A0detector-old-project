import subprocess
import socket
import platform
import ipaddress
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class NetworkScanner:
    def __init__(self):
        self.devices = []
        
    def ping(self, ip):
        """Ping a single IP address and return True if host is up."""
        try:
            # Ajustar comando ping según el sistema operativo
            if platform.system().lower() == "windows":
                ping_cmd = ['ping', '-n', '1', '-w', '1000', ip]
            else:
                ping_cmd = ['ping', '-c', '1', '-W', '1', ip]
                
            # Ejecutar comando ping y capturar salida
            result = subprocess.run(ping_cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True)
                                  
            # Verificar si obtuvimos una respuesta exitosa
            if platform.system().lower() == "windows":
                return "TTL=" in result.stdout
            else:
                return "64 bytes" in result.stdout
        except Exception as e:
            print(f"Error pinging {ip}: {str(e)}")
            return False

    def get_device_info(self, ip):
        """Get device information for a given IP."""
        try:
            # Intentar obtener el hostname
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "Unknown"
            
        # Obtener el último octeto para usar como ID
        device_id = ip.split('.')[-1]
        
        # Obtener la subred
        subnet = '.'.join(ip.split('.')[:3])
        
        return {
            'ip': ip,
            'hostname': hostname,
            'id': device_id,
            'subnet': subnet,
            'status': 'active'
        }
        
    def scan_ip(self, ip):
        """Scan a single IP address."""
        if self.ping(str(ip)):
            return self.get_device_info(str(ip))
        return None
        
    def scan_network(self, network="192.168.1.0/24", max_workers=50):
        """Scan a network range for active devices."""
        print(f"Scanning network: {network}")
        
        try:
            # Crear objeto de red
            net = ipaddress.ip_network(network, strict=False)
            self.devices = []
            
            # Escanear en paralelo
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Enviar todas las IPs para escanear
                future_to_ip = {executor.submit(self.scan_ip, ip): ip for ip in net.hosts()}
                
                # Procesar resultados conforme lleguen
                for future in as_completed(future_to_ip):
                    result = future.result()
                    if result:
                        self.devices.append(result)
                        print(f"Found device: {result['ip']} ({result['hostname']})")
                        
        except Exception as e:
            print(f"Error scanning network: {str(e)}")
            
        return self.devices
        
    def get_local_network(self):
        """Automatically detect the local network range."""
        try:
            # Obtener la IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Construir la red /24
            network_parts = local_ip.split('.')
            network = f"{network_parts[0]}.{network_parts[1]}.{network_parts[2]}.0/24"
            
            return network
        except Exception as e:
            print(f"Error detecting local network: {str(e)}")
            return "192.168.1.0/24"  # Default fallback


if __name__ == "__main__":
    scanner = NetworkScanner()
    
    # Detectar red local automáticamente
    network = scanner.get_local_network()
    print(f"Detected local network: {network}")
    
    # Escanear la red
    devices = scanner.scan_network(network)
    
    # Mostrar resultados
    print(f"\n--- Scan Results ---")
    print(f"Found {len(devices)} active devices:")
    print("-" * 60)
    
    for device in devices:
        print(f"IP: {device['ip']:<15} | Hostname: {device['hostname']}")
    
    print("-" * 60)
