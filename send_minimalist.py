import os
import json
import requests
from datetime import datetime

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")
DASHBOARD_PATH = os.path.join(ROOT_DIR, "HelpDesk", "priority_dashboard.html")
EXCEL_PATH = os.path.join(ROOT_DIR, "HelpDesk", "Requerimientos_IT_24_04_2026_VF2.xlsx")

def send_minimalist_report():
    print("Iniciando envío MINIMALISTA (para evitar filtros)...")
    
    if not os.path.exists(CONFIG_PATH): return

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "intranet-cinlat@cinlatlogistics.com")
    to_email = "miguel.ochoa@cinlatlogistics.com"
    
    subject = f"REPORTE IT - {datetime.now().strftime('%d/%m/%Y')}"
    
    # SIMPLE TEXT BODY (No HTML markers, no JavaScript)
    text_content = """Hola Miguel,
    
Adjunto el reporte de requerimientos IT actualizado en formato Excel y el Dashboard Interactivo en formato HTML.

Favor de descargar el archivo HTML y abrirlo en Chrome para ver las funciones dinamicas.

Saludos."""

    files = []
    if os.path.exists(EXCEL_PATH):
        files.append(("attachment", ("Prioridades_IT_20_04.xlsx", open(EXCEL_PATH, "rb"))))
    if os.path.exists(DASHBOARD_PATH):
        files.append(("attachment", ("Dashboard_Interactivo.html", open(DASHBOARD_PATH, "rb"))))

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    
    payload = {
        "from": f"IT Reports <{from_email}>",
        "to": to_email,
        "subject": subject,
        "text": text_content
    }

    try:
        response = requests.post(url, auth=auth, data=payload, files=files if files else None)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_minimalist_report()
