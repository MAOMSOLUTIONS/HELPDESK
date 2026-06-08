import os
import json
import requests
from datetime import datetime

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")
DASHBOARD_PATH = os.path.join(ROOT_DIR, "HelpDesk", "priority_dashboard.html")

def send_dashboard_only():
    print("Enviando Dashboard HTML (Sin el Excel de 40MB)...")
    
    if not os.path.exists(CONFIG_PATH): return

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "it-reporting@cinlatlogistics.com")
    to_email = "miguel.ochoa@cinlatlogistics.com"
    
    subject = f"DASHBOARD IT - {datetime.now().strftime('%d/%m/%Y')}"
    
    text_content = """Hola Miguel,
    
Adjunto solo el Dashboard Interactivo. 

El archivo Excel que colocaste pesa 40MB, lo cual supera el límite de los servidores de correo (25MB) y por eso no te estaba llegando.

Saludos."""

    files = []
    if os.path.exists(DASHBOARD_PATH):
        files.append(("attachment", ("Dashboard_Prioridad.html", open(DASHBOARD_PATH, "rb"))))

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    
    payload = {
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "text": text_content
    }

    try:
        response = requests.post(url, auth=auth, data=payload, files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_dashboard_only()
