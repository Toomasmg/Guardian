# 🛡️ Guardian - Gestión Centralizada

Guardian es un sistema web robusto y de estética premium diseñado para simplificar la administración de clientes y el control de licencias de software para negocios IT. 

Desarrollado en Python con Flask, el sistema permite a los administradores llevar un seguimiento exacto de los pagos, generar *API Keys* únicas, vincular *Hardware IDs* para evitar piratería y gestionar el estado de los clientes con integración rápida a WhatsApp.

## ✨ Características

* **Autenticación Segura:** Sistema de login para administradores con recuperación mediante PIN y código maestro de registro.
* **Gestión de Licencias:** Creación, suspensión, eliminación y renovación rápida de suscripciones.
* **Anti-Piratería (HWID):** Las licencias se vinculan automáticamente al Hardware ID de la PC del cliente en su primer uso. El panel permite desvincular equipos de forma manual.
* **Dashboard Estadístico:** Visualización en tiempo real de ingresos, clientes activos, morosos o bloqueados.
* **Modo Oscuro/Claro:** Interfaz dinámica e intuitiva con estética profesional.
* **Exportación de Datos:** Generación de reportes en formato CSV/Excel con un solo clic.

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python, Flask.
* **Base de Datos:** MySQL, SQLAlchemy (ORM).
* **Seguridad:** Werkzeug (Hashing), Flask-Login, Flask-Limiter (Anti fuerza bruta).
* **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2.

## 🚀 Instalación y Uso Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/guardian.git](https://github.com/TU_USUARIO/guardian.git)
   cd guardian

# Configurar el entorno
python -m venv venv
# Activar en Windows: venv\Scripts\activate
pip install -r requirements.txt

# Ejecutar:
python app.py

# Integración en las Aplicaciones de tus Clientes
Este código debe ser el punto de entrada de la aplicación de tu cliente. 
Valida la licencia al iniciar y mantiene una vigilancia en segundo plano:

import sys
import time
import requests
import subprocess
import threading
import os

# CONFIGURACIÓN
SERVER_URL = "[http://tu-servidor-guardian.com/api/validate_license](http://tu-servidor-guardian.com/api/validate_license)"
CLIENT_API_KEY = "API_KEY_DEL_DASHBOARD" 
CHECK_INTERVAL = 600  # 10 minutos
MAX_TOLERANCIA = 5    # Gracia por micro-cortes de internet

def get_hwid():
    return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()

def validar_licencia_remota():
    try:
        response = requests.post(SERVER_URL, json={
            "api_key": CLIENT_API_KEY,
            "hardware_id": get_hwid()
        }, timeout=10)
        return response.json()
    except:
        return None

def vigilancia_en_segundo_plano():
    fallos = 0
    while True:
        time.sleep(CHECK_INTERVAL)
        res = validar_licencia_remota()
        if res is None:
            fallos += 1
            if fallos >= MAX_TOLERANCIA: os._exit(1)
            continue
        fallos = 0
        if not res.get("valid"): os._exit(1)

def iniciar_sistema_protegido():
    print("🔒 VALIDANDO LICENCIA...")
    res = validar_licencia_remota()
    
    if res and res.get("valid"):
        print(f"✅ BIENVENIDO {res.get('owner')}")
        threading.Thread(target=vigilancia_en_segundo_plano, daemon=True).start()
        ejecutar_app_real()
    else:
        print("⛔ ACCESO DENEGADO")
        sys.exit(1)

def ejecutar_app_real():
    # AQUÍ INICIA TU PROGRAMA (Ej: App de Ventas, Turnos, etc.)
    print("\n--- SISTEMA CORRIENDO PROTEGIDO ---")
    while True: time.sleep(1)

if __name__ == "__main__":
    iniciar_sistema_protegido()

# Seguridad y Distribución Profesional

Para que el sistema sea inviolable y funcione en cualquier computadora sin necesidad 
de instalar Python, se debe seguir este flujo:

# Ofuscación (PyArmor): Encripta el código para que no pueda ser leído ni modificado por el cliente. 
# En terminal hacer lo siguiente:

pyarmor gen -O ofuscado integracion_main.py

# Compilación (PyInstaller): Empaqueta todo en un único archivo .exe.

cd ofuscado
pyinstaller --onefile --noconsole integracion_main.py

El archivo resultante en dist/integracion_main.exe es el que se entrega al cliente. Puede usarse como un Launcher para abrir programas hechos en cualquier otro lenguaje (C#, Java, etc.) o como el ejecutable principal si el sistema fue hecho en Python.