import subprocess
import socket
import platform
import logging

logger = logging.getLogger(__name__)

def ping(ip):
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
        logger.error(f"Error pinging {ip}: {str(e)}")
        return False

def get_device_info(ip):
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