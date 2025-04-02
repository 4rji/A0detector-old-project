# Network Device Scanner

Una aplicación web para escanear y visualizar dispositivos en tu red local.

## Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Debian 12 o superior

## Instalación en Debian

### 1. Actualizar el sistema

```bash
sudo apt update
sudo apt upgrade
```

### 2. Instalar dependencias del sistema

```bash
# Instalar Python y herramientas de desarrollo
sudo apt install -y python3 python3-pip python3-venv

# Instalar herramientas de red necesarias
sudo apt install -y \
    avahi-utils \
    samba-common-bin \
    net-tools \
    nmap \
    arping

# Instalar bibliotecas de desarrollo necesarias
sudo apt install -y \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev
```

### 3. Configurar el entorno virtual de Python

```bash
# Crear un entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```

### 4. Instalar dependencias de Python

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar las dependencias
pip install \
    flask \
    python-dotenv \
    dnspython \
    requests \
    werkzeug
```

### 5. Configurar permisos de red

Para que la aplicación pueda escanear la red, necesita permisos especiales para usar ICMP (ping) y ARP.

```bash
# Permitir ping sin privilegios de root
sudo sysctl -w net.ipv4.ping_group_range="0 2147483647"

# Dar permisos para usar raw sockets (necesario para ARP)
sudo setcap cap_net_raw+ep $(readlink -f $(which python3))
```

### 6. Configurar el archivo de configuración

Crear un archivo `settings.json` en el directorio raíz del proyecto:

```json
{
    "subnets": [
        "192.168.1",
        "10.0.0",
        "172.16.0"
    ]
}
```

Ajusta las subredes según tu configuración de red.

## Ejecutar la aplicación

1. Activar el entorno virtual (si no está activado):
```bash
source venv/bin/activate
```

2. Iniciar la aplicación:
```bash
python3 -m flask run --host=0.0.0.0
```

La aplicación estará disponible en `http://localhost:5000`

## Solución de problemas

### No se detectan nombres de host

Si los dispositivos aparecen como "Device-X" en lugar de sus nombres reales:

1. Verifica que avahi-daemon esté instalado y ejecutándose:
```bash
sudo apt install avahi-daemon
sudo systemctl start avahi-daemon
sudo systemctl enable avahi-daemon
```

2. Configura el archivo hosts:
```bash
sudo nano /etc/hosts
```
Agrega las entradas para tus dispositivos conocidos:
```
192.168.1.1    router.local
192.168.1.2    pc1.local
```

### Problemas de permisos

Si tienes problemas de permisos al escanear la red:

1. Verifica que el usuario tenga los permisos necesarios:
```bash
sudo usermod -aG netdev $USER
```

2. Reinicia la sesión para que los cambios tengan efecto.

### Problemas de rendimiento

Si el escaneo es lento:

1. Ajusta el número de workers en `app/__init__.py`:
```python
max_workers=50  # Aumenta o disminuye según tu hardware
```

2. Limita el rango de IPs a escanear modificando `settings.json`

## Características

- Escaneo de múltiples subredes
- Detección automática de routers y dispositivos
- Identificación de fabricantes por MAC
- Visualización interactiva de la red
- Actualización en tiempo real
- Soporte para nombres de host locales

## Seguridad

- No ejecutes la aplicación como root
- Limita el acceso a la red local
- Mantén el sistema actualizado
- Usa un firewall para proteger el puerto de la aplicación

## Contribuir

Si encuentras algún problema o tienes sugerencias, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT. 