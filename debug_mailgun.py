import os
import json
import requests
from datetime import datetime

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")

def debug_ping():
    print("Iniciando prueba de PING de correo...")
    if not os.path.exists(CONFIG_PATH):
        print("Config no encontrada.")
        return

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "intranet-cinlat@cinlatlogistics.com")
    to_email = "miguel.ochoa@cinlatlogistics.com"
    
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    
    payload = {
        "from": f"DEBUG Antigravity <{from_email}>",
        "to": to_email,
        "subject": f"TEST PING - {datetime.now().strftime('%H:%M:%S')}",
        "text": "Si recibes esto, el servidor de correo esta funcionando perfectamente. Por favor confirma."
    }

    try:
        response = requests.post(url, auth=auth, data=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error fatal: {e}")

if __name__ == "__main__":
    debug_ping()
