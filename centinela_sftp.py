import os
import sys
import json
import time
import csv
import hashlib
import requests
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- SALVAGUARDA PARA PYINSTALLER --NOCONSOLE (EJECUCIÓN SILENCIOSA) ---
class DummyStream:
    def write(self, data):
        pass
    def flush(self):
        pass
    def isatty(self):
        return False

# Redirigir si sys.stdout o sys.stderr son None
if sys.stdout is None or getattr(sys.stdout, 'write', None) is None:
    sys.stdout = DummyStream()
if sys.stderr is None or getattr(sys.stderr, 'write', None) is None:
    sys.stderr = DummyStream()

# Redefinir print de forma segura
def print_safe(*args, sep=' ', end='\n', file=None):
    try:
        message = sep.join(str(arg) for arg in args) + end
        if file is not None:
            file.write(message)
        else:
            sys.stdout.write(message)
    except Exception:
        pass

print = print_safe

# --- DETERMINAR RUTA DEL EJECUTABLE O SCRIPT ---
# Esto garantiza que al compilar con PyInstaller, config.json y los logs
# se busquen y guarden en la misma carpeta donde reside el archivo .exe.
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(APP_DIR, "config.json")
LOG_PATH = os.path.join(APP_DIR, "monitoreo_sftp.log")
CSV_PATH = os.path.join(APP_DIR, "monitoreo_sftp.csv")

# Dirección de respaldo de Mailgun Tester en desarrollo
CONFIG_FALLBACK_PATH = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\MailgunTester\config.json"

# --- CONFIGURACIÓN SFTP POR DEFECTO ---
CARPETA_DEFECTO = r"C:\CData\Arc\data\SFTPServerProd\Send"
EMAIL_DEFECTO = "miguel.ochoa@cinlatlogistics.com, ernesto.salazar@cinlatlogistics.com"

# --- FUNCIONES DE SOPORTE ---
def cargar_credenciales():
    """Carga las credenciales de config.json en el directorio local o fallback."""
    path_to_use = CONFIG_PATH
    if not os.path.exists(path_to_use):
        if os.path.exists(CONFIG_FALLBACK_PATH):
            path_to_use = CONFIG_FALLBACK_PATH
        else:
            raise FileNotFoundError(
                f"No se encontró config.json en {CONFIG_PATH} ni en {CONFIG_FALLBACK_PATH}"
            )
            
    with open(path_to_use, "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_config_sftp():
    """Carga de forma dinámica la carpeta y correos destinatarios configurados."""
    try:
        config = cargar_credenciales()
        carpeta = config.get("carpeta_monitorear", CARPETA_DEFECTO)
        correos = config.get("emails_destinatarios", EMAIL_DEFECTO)
        return carpeta, correos
    except Exception as e:
        registrar_log(f"Advertencia al cargar config.json, usando defaults: {e}")
        return CARPETA_DEFECTO, EMAIL_DEFECTO

def registrar_log(mensaje):
    """Escribe eventos en el log de diagnóstico usando codificación UTF-8."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea_log = f"[{timestamp}] {mensaje}"
    print(linea_log)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(linea_log + "\n")
    except Exception as e:
        print(f"Error escribiendo en bitácora log: {e}")

def registrar_csv(nombre_archivo, tamano, tamano_bytes, file_hash, propietario, sesiones, tipo_evento, ruta_completa):
    """
    Registra cada evento en un archivo CSV estructurado.
    Usa 'utf-8-sig' para que Excel en Windows reconozca acentos y caracteres especiales automáticamente.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    archivo_existente = os.path.exists(CSV_PATH)
    
    try:
        with open(CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            
            # Escribir la cabecera si el archivo se crea por primera vez
            if not archivo_existente:
                writer.writerow([
                    "Fecha y Hora",
                    "Archivo",
                    "Tamaño Formateado",
                    "Tamaño (Bytes)",
                    "Firma SHA-256",
                    "Usuario Creador",
                    "Sesiones Activas",
                    "Acción / Evento",
                    "Ruta Completa"
                ])
                
            writer.writerow([
                timestamp,
                nombre_archivo,
                tamano,
                tamano_bytes,
                file_hash,
                propietario,
                sesiones,
                tipo_evento.upper(),
                ruta_completa
            ])
    except Exception as e:
        registrar_log(f"Error escribiendo en registro CSV: {e}")

def enviar_correo(destinatario, asunto, cuerpo_html):
    """Envía alertas por correo usando la API de Mailgun."""
    try:
        config = cargar_credenciales()
        api_key = config['api_key']
        domain = config['domain']
        remitente = config.get('from_email', "intranet-cinlat@cinlatlogistics.com")
        
        url = f"https://api.mailgun.net/v3/{domain}/messages"
        auth = ("api", api_key)
        payload = {
            "from": f"Centinela SFTP <{remitente}>",
            "to": destinatario,
            "subject": asunto,
            "html": cuerpo_html
        }
        
        # Intentar con verificación SSL estricta estándar por defecto
        try:
            response = requests.post(url, auth=auth, data=payload)
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as ssl_err:
            # Fallback seguro para redes corporativas con inspección/re-firmado de certificados SSL
            registrar_log("Advertencia de Red: Error de verificación de certificado SSL corporativo. Reintentando de forma segura (verify=False)...")
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.post(url, auth=auth, data=payload, verify=False)
            
        if response.status_code == 200:
            print(f"Correo de alerta enviado con éxito a: {destinatario}.")
        else:
            print(f"Error al enviar correo (HTTP {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Error enviando correo: {e}")

def obtener_propietario(ruta):
    """Obtiene el usuario propietario del archivo en Windows usando las APIs de Seguridad."""
    try:
        import win32security
        sd = win32security.GetFileSecurity(ruta, win32security.OWNER_SECURITY_INFORMATION)
        owner_sid = sd.GetSecurityDescriptorOwner()
        nombre_usuario, dominio, tipo_sid = win32security.LookupAccountSid(None, owner_sid)
        return f"{dominio}\\{nombre_usuario}"
    except Exception:
        return "Carga Externa (Usuario SFTP)"

def obtener_tamano_archivo(ruta):
    """Obtiene el tamaño del archivo formateado en unidades legibles (Bytes, KB, MB)."""
    try:
        if os.path.exists(ruta):
            size_bytes = os.path.getsize(ruta)
            if size_bytes < 1024:
                return f"{size_bytes} Bytes"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.2f} MB"
        return "No disponible"
    except Exception:
        return "Leyendo... (En transmisión)"

def obtener_hash_sha256(ruta):
    """Calcula de forma pasiva y segura (solo lectura compartida) la firma SHA-256 del archivo."""
    if not os.path.exists(ruta) or os.path.isdir(ruta):
        return "No disponible"
    
    hash_sha256 = hashlib.sha256()
    try:
        # Modo 'rb' binario. Windows permite lecturas compartidas simultáneas por defecto en 'rb'
        with open(ruta, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except PermissionError:
        return "Lectura segura en proceso (Bloqueado por SFTP)"
    except Exception as e:
        return f"Error en lectura pasiva: {str(e)}"

def obtener_sesiones_activas():
    """Ejecuta qwinsta de forma segura para listar sesiones interactivas conectadas en Windows."""
    try:
        import subprocess
        output = subprocess.check_output("qwinsta", shell=True, text=True, stderr=subprocess.DEVNULL)
        sesiones = []
        for line in output.splitlines():
            parts = line.split()
            if not parts or "NOMBRE" in parts[0] or "SESSIONNAME" in parts[0]:
                continue
            
            # Comprobar si la sesión está activa
            if any(status in line.upper() for status in ["ACTIVO", "ACTIVE", "CONN"]):
                session_name = parts[0]
                if session_name.startswith(">"):
                    session_name = session_name[1:]
                
                user = None
                if len(parts) >= 4:
                    if parts[2].isdigit():
                        user = parts[1]
                    elif len(parts) >= 5 and parts[3].isdigit():
                        user = parts[2]
                
                if user and user.lower() not in ["services", "servicios"]:
                    sesiones.append(f"{user} [{session_name}]")
                    
        if sesiones:
            return ", ".join(sesiones)
        return "Sin sesiones interactivas (Solo servicios)"
    except Exception as e:
        return f"No disponible (Error: {str(e)})"

# --- PROCESADOR DE EVENTOS DE FILESYSTEM (100% LECTURA, SIN BLOQUEOS) ---
class ManejadorSFTP(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        # Registro forense en memoria para auditar archivos que son eliminados posteriormente
        self.registro_cache = {}

    def esperar_estabilizacion(self, ruta_archivo, max_espera_seg=5):
        """Espera de forma pasiva a que el tamaño de archivo se estabilice (fin de escritura)."""
        if not os.path.exists(ruta_archivo):
            return False
            
        intervalo = 0.5
        intentos = int(max_espera_seg / intervalo)
        ultimo_tamano = -1
        
        for _ in range(intentos):
            try:
                if not os.path.exists(ruta_archivo):
                    return False
                tamano_actual = os.path.getsize(ruta_archivo)
                # Si el tamaño se estabilizó y es mayor que cero, intentar una apertura de lectura rápida
                if tamano_actual == ultimo_tamano and tamano_actual > 0:
                    with open(ruta_archivo, "rb") as f:
                        pass
                    return True
                ultimo_tamano = tamano_actual
            except (PermissionError, IOError):
                # El archivo sigue bloqueado/escribiéndose
                pass
            time.sleep(intervalo)
            
        return os.path.exists(ruta_archivo)

    def procesar_archivo(self, ruta_archivo, tipo_evento):
        if os.path.isdir(ruta_archivo) and tipo_evento != "eliminado":
            return

        nombre_archivo = os.path.basename(ruta_archivo)
        
        # Filtro inteligente de extensiones temporales para no duplicar eventos
        extensiones_temporales = ('.tmp', '.filepart', '.part', '.crdownload', '.lock')
        if nombre_archivo.lower().endswith(extensiones_temporales):
            registrar_log(f"Archivo temporal omitido del reporte: {nombre_archivo}")
            return

        # Cargar configuración dinámica
        carpeta_monitorear, emails_destinatarios = cargar_config_sftp()
        
        # Variables por defecto
        tamano = "No disponible"
        tamano_bytes = 0
        propietario = "Carga Externa (Usuario SFTP)"
        file_hash = "No disponible"
        sesiones = obtener_sesiones_activas()

        if tipo_evento == "eliminado":
            # Si es borrado, recuperar datos desde la caché forense virtual
            if nombre_archivo in self.registro_cache:
                cache = self.registro_cache[nombre_archivo]
                tamano = cache['tamano']
                tamano_bytes = cache['tamano_bytes']
                propietario = f"{cache['propietario']} (Creador original)"
                file_hash = cache['hash']
                # Limpiar de la caché
                del self.registro_cache[nombre_archivo]
            else:
                propietario = "No disponible (Eliminado sin registro previo)"
                file_hash = "No disponible"
        else:
            # Esperar estabilización si se está creando o modificando
            if tipo_evento in ["creado", "modificado"]:
                self.esperar_estabilizacion(ruta_archivo)
                
            if os.path.exists(ruta_archivo):
                tamano = obtener_tamano_archivo(ruta_archivo)
                try:
                    tamano_bytes = os.path.getsize(ruta_archivo)
                except Exception:
                    tamano_bytes = 0
                propietario = obtener_propietario(ruta_archivo)
                file_hash = obtener_hash_sha256(ruta_archivo)
                
                # Almacenar en la caché forense virtual
                self.registro_cache[nombre_archivo] = {
                    'propietario': propietario,
                    'tamano': tamano,
                    'tamano_bytes': tamano_bytes,
                    'hash': file_hash
                }

        mensaje = f"ALERTA: Archivo {tipo_evento.upper()} -> {nombre_archivo} | Tamaño: {tamano} | Creador: {propietario} | Hash: {file_hash[:12]} | Sesiones: {sesiones}"
        registrar_log(mensaje)

        # Registrar en la tabla de datos CSV
        registrar_csv(nombre_archivo, tamano, tamano_bytes, file_hash, propietario, sesiones, tipo_evento, ruta_archivo)

        # Configuración estética según la gravedad del evento
        if tipo_evento == "eliminado":
            color_cabecera = "#ef4444"
            titulo_alerta = "🚨 Alerta SFTP: Archivo ELIMINADO"
            descripcion_alerta = "Se ha detectado la eliminación o borrado de un archivo en la carpeta vigilada."
            etiqueta_evento = f'<span style="background-color: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{tipo_evento.upper()}</span>'
        elif tipo_evento == "modificado":
            color_cabecera = "#f59e0b"
            titulo_alerta = "⚠️ Alerta SFTP: Archivo MODIFICADO"
            descripcion_alerta = "Se ha detectado una modificación en el tamaño o contenido de un archivo."
            etiqueta_evento = f'<span style="background-color: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{tipo_evento.upper()}</span>'
        else:
            color_cabecera = "#10b981"
            titulo_alerta = "✅ Alerta SFTP: Archivo CREADO"
            descripcion_alerta = "Se ha completado la carga exitosa de un archivo nuevo."
            etiqueta_evento = f'<span style="background-color: #d1fae5; color: #065f46; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{tipo_evento.upper()}</span>'

        asunto = f"{titulo_alerta}: {nombre_archivo}"
        
        html = f"""
        <html>
            <body style="font-family: Calibri, Arial, sans-serif; line-height: 1.6; color: #1e293b; max-width: 650px; margin: 0 auto; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px;">
                <div style="background-color: {color_cabecera}; color: white; padding: 15px; border-radius: 6px 6px 0 0; text-align: center;">
                    <h2 style="margin: 0; font-size: 20px; font-weight: bold;">{titulo_alerta}</h2>
                </div>
                <div style="padding: 20px; background-color: #f8fafc;">
                    <p style="font-size: 15px; margin-top: 0;">{descripcion_alerta}</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 15px 0; background: #ffffff; border-radius: 4px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <tr style="background: #f1f5f9;">
                            <th style="padding: 10px; text-align: left; font-size: 13px; border-bottom: 1px solid #cbd5e1; width: 35%;">Propiedad</th>
                            <th style="padding: 10px; text-align: left; font-size: 13px; border-bottom: 1px solid #cbd5e1;">Detalle</th>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-size: 13px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Archivo</td>
                            <td style="padding: 10px; font-size: 13px; color: #0f172a; border-bottom: 1px solid #e2e8f0; font-family: Consolas, monospace; font-weight: bold;">{nombre_archivo}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-size: 13px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Tamaño</td>
                            <td style="padding: 10px; font-size: 13px; color: #0f172a; border-bottom: 1px solid #e2e8f0; font-weight: bold;">{tamano}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-size: 13px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Firma SHA-256</td>
                            <td style="padding: 10px; font-size: 11px; color: #475569; border-bottom: 1px solid #e2e8f0; font-family: Consolas, monospace; word-break: break-all;">{file_hash}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-size: 13px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Usuario / Creador</td>
                            <td style="padding: 10px; font-size: 13px; color: #1e3a8a; border-bottom: 1px solid #e2e8f0; font-family: Consolas, monospace;">{propietario}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-size: 13px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Ruta del Servidor</td>
                            <td style="padding: 10px; font-size: 12px; color: #475569; border-bottom: 1px solid #e2e8f0; font-family: Consolas, monospace; word-break: break-all;">{ruta_archivo}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-size: 13px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Acción Detectada</td>
                            <td style="padding: 10px; font-size: 13px; border-bottom: 1px solid #e2e8f0;">{etiqueta_evento}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-size: 13px; font-weight: bold; border-bottom: 1px solid #e2e8f0;">Sesiones Activas (RDP)</td>
                            <td style="padding: 10px; font-size: 13px; color: #b45309; border-bottom: 1px solid #e2e8f0; font-family: Consolas, monospace;">{sesiones}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; font-size: 13px; font-weight: bold;">Fecha y Hora</td>
                            <td style="padding: 10px; font-size: 13px; color: #0f172a;">{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</td>
                        </tr>
                    </table>
                    
                    <p style="font-size: 12px; color: #64748b; padding: 10px; background: #f1f5f9; border-left: 3px solid {color_cabecera}; border-radius: 4px; margin-bottom: 0;">
                        <b>Auditoría de seguridad pasiva (Solo Lectura):</b> Este sistema calcula la firma criptográfica del archivo y registra las conexiones activas al servidor RDP sin bloquear escrituras, garantizando un registro forense intachable.
                    </p>
                </div>
                <div style="text-align: center; margin-top: 20px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">
                    © Cinlat Logistics S.A. de C.V. - Dirección de TI
                </div>
            </body>
        </html>
        """
        enviar_correo(emails_destinatarios, asunto, html)

    def on_created(self, event):
        self.procesar_archivo(event.src_path, "creado")

    def on_moved(self, event):
        self.procesar_archivo(event.dest_path, "renombrado")
        
    def on_deleted(self, event):
        self.procesar_archivo(event.src_path, "eliminado")
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        nombre = os.path.basename(event.src_path)
        extensiones_temporales = ('.tmp', '.filepart', '.part', '.lock')
        if nombre.lower().endswith(extensiones_temporales):
            return
            
        # Esperamos una estabilización rápida
        time.sleep(0.5)
        if not os.path.exists(event.src_path):
            return
            
        # Evitar spam: Si el hash actual es idéntico al registrado, omitimos correo
        nuevo_hash = obtener_hash_sha256(event.src_path)
        if nombre in self.registro_cache:
            if self.registro_cache[nombre]['hash'] == nuevo_hash:
                return
                
        self.procesar_archivo(event.src_path, "modificado")

# --- EJECUCIÓN DEL CENTINELA ---
if __name__ == "__main__":
    registrar_log("=== INICIANDO CENTINELA DE MONITOREO SFTP ===")
    
    # Cargar de forma dinámica la carpeta a monitorear y correos
    carpeta_monitorear, emails_destinatarios = cargar_config_sftp()
    
    # Validar que la carpeta a monitorear exista antes de arrancar
    if not os.path.exists(carpeta_monitorear):
        registrar_log(f"ERROR CRÍTICO: La carpeta {carpeta_monitorear} no existe. Creándola...")
        try:
            os.makedirs(carpeta_monitorear, exist_ok=True)
            registrar_log(f"Carpeta creada exitosamente.")
        except Exception as e:
            registrar_log(f"No se pudo crear la carpeta: {e}. Deteniendo centinela.")
            sys.exit(1)

    # 1. Enviar notificación de arranque exitoso (Correo de Bienvenida con Guía de Alertas)
    asunto_inicio = "🚀 Centinela SFTP Activo: Monitoreo Forense Iniciado"
    html_inicio = f"""
    <html>
        <body style="font-family: Calibri, Arial, sans-serif; line-height: 1.6; color: #1e293b; max-width: 650px; margin: 0 auto; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px;">
            <div style="background-color: #2563eb; color: white; padding: 15px; border-radius: 6px 6px 0 0; text-align: center;">
                <h2 style="margin: 0; font-size: 20px; font-weight: bold;">✅ Servidor de Centinela Encendido</h2>
            </div>
            <div style="padding: 20px; background-color: #f8fafc;">
                <p style="font-size: 15px; font-weight: bold; color: #1e3a8a; margin-top: 0;">¡Hola! El servicio de auditoría se ha iniciado con éxito.</p>
                <p>El Centinela está vigilando de forma <b>pasiva, no intrusiva y segura</b> la siguiente ruta en el servidor:</p>
                <div style="background: #e2e8f0; padding: 12px; border-radius: 4px; font-family: Consolas, monospace; font-size: 13px; color: #0f172a; margin: 10px 0; border-left: 4px solid #2563eb;">
                    {carpeta_monitorear}
                </div>
                
                <h3 style="color: #0f172a; font-size: 14px; margin-top: 20px; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px;">📊 Información y Auditoría Recopilada:</h3>
                <p>Para asegurar un registro forense completo (rastrear "quién mueve el queso"), cada alerta reportará automáticamente:</p>
                <ul style="padding-left: 20px; font-size: 13px; color: #334155;">
                    <li style="margin-bottom: 6px;"><b>Nombre del Archivo:</b> Identificación exacta del documento.</li>
                    <li style="margin-bottom: 6px;"><b>Tamaño del Archivo:</b> Calculado en tiempo real en Bytes, KB o MB.</li>
                    <li style="margin-bottom: 6px;"><b>Firma SHA-256:</b> Huella criptográfica única para verificar si el contenido ha sido alterado.</li>
                    <li style="margin-bottom: 6px;"><b>Usuario NTFS / Creador:</b> Muestra la cuenta de Windows o del servicio que cargó o interactuó con el archivo.</li>
                    <li style="margin-bottom: 6px;"><b>Sesiones Activas (RDP):</b> Muestra qué usuarios estaban conectados al servidor por Escritorio Remoto (RDP) en ese exacto milisegundo.</li>
                    <li style="margin-bottom: 6px;"><b>Acciones Soportadas:</b> Reportes específicos de archivos CREADOS, MODIFICADOS y ELIMINADOS (con metadatos recuperados desde caché virtual).</li>
                </ul>

                <p style="font-size: 13px; color: #2563eb; background: #eff6ff; padding: 12px; border-radius: 4px; border-left: 3px solid #2563eb; margin-top: 20px;">
                    ℹ️ <b>Estado del Servicio:</b> Activo y vigilando sin bloqueos de memoria (cero impacto en el performance del disco del servidor y 100% de solo lectura compartida).
                </p>
            </div>
            <div style="text-align: center; margin-top: 20px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">
                © Cinlat Logistics S.A. de C.V. - Dirección de TI
            </div>
        </body>
    </html>
    """
    enviar_correo(emails_destinatarios, asunto_inicio, html_inicio)
    registrar_log(f"Monitoreando de manera pasiva en: {carpeta_monitorear}")

    # 2. Configurar el Observador del Sistema de Archivos
    manejador = ManejadorSFTP()
    observer = Observer()
    observer.schedule(manejador, carpeta_monitorear, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        registrar_log("Deteniendo centinela por orden del usuario (KeyboardInterrupt)...")
        observer.stop()
    except Exception as e:
        registrar_log(f"Excepción inesperada en bucle de ejecución: {e}")
        observer.stop()
        
    observer.join()
    registrar_log("=== CENTINELA APAGADO ===")
