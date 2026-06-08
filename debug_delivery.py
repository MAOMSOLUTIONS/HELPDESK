import os
import json
import requests
from datetime import datetime

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")

def send_test_no_attachment():
    print("Iniciando envío de PRUEBA (Sin adjuntos pesados)...")
    
    if not os.path.exists(CONFIG_PATH): 
        print("Config no encontrada")
        return

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "it-reporting@cinlatlogistics.com")
    to_email = "miguel.ochoa@cinlatlogistics.com"
    
    subject = f"PRUEBA DE ENTREGA - {datetime.now().strftime('%H:%M:%S')}"
    
    text_content = """Hola Miguel,
    
Esta es una prueba de entrega sin el archivo de 40MB para verificar si el servidor de correo lo está bloqueando por tamaño.

Si recibes este correo, el problema es el tamaño del Excel (40MB supera el límite estándar de 25MB).

Saludos."""

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    
    payload = {
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "text": text_content
    }

    try:
        response = requests.post(url, auth=auth, data=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_test_no_attachment()
