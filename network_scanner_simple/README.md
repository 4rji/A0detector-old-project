# Network Device Scanner

Un escáner de dispositivos de red simple y eficiente sin autenticación ni configuraciones complejas.

## Características

- 🔍 **Escaneo automático**: Detecta automáticamente tu red local y escanea dispositivos
- 🎯 **Escaneo personalizado**: Permite escanear cualquier rango de red que especifiques
- ⚡ **Rápido**: Escaneo en paralelo para máxima velocidad
- 🌐 **Interfaz web**: Interfaz simple y limpia para ver los resultados
- 📱 **Responsive**: Funciona en desktop y móvil

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Modo consola (línea de comandos)
```bash
python network_scanner.py
```

### Modo web (interfaz gráfica)
```bash
python app.py
```

Luego abre tu navegador en: http://localhost:5000

## Funcionalidades

- **Auto Scan**: Detecta automáticamente tu red local (ej: 192.168.1.0/24) y escanea todos los dispositivos
- **Custom Scan**: Permite especificar cualquier rango de red (ej: 10.0.0.0/24, 172.16.0.0/16)
- **Información de dispositivos**: Muestra IP, hostname y estado de cada dispositivo encontrado

## Ejemplos de uso

### Escanear red local automáticamente
- Click en "Auto Scan Local Network"

### Escanear red personalizada
- Ingresa el rango: `192.168.0.0/24`
- Click en "Scan Custom Network"

## Compatibilidad

- ✅ Windows, macOS, Linux
- ✅ Python 3.6+
- ✅ Flask 2.0.1 con Werkzeug 2.0.3 (versiones compatibles)

## Sin dependencias externas

No requiere:
- ❌ Autenticación
- ❌ Base de datos  
- ❌ Configuración compleja
- ❌ Permisos especiales

¡Simplemente instala y ejecuta!
