import os
import json
import requests
from datetime import datetime

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")
REPORT_PATH = os.path.join(ROOT_DIR, "HelpDesk", "premium_report_concise.html")

# Dynamic Excel Path for today
TODAY_STR = datetime.now().strftime("%d_%m_%Y")
EXCEL_PATH = os.path.join(ROOT_DIR, "HelpDesk", f"ReporteHelpdesk{TODAY_STR}.xlsx")

def send_concise_report():
    if not os.path.exists(CONFIG_PATH):
        print("Error: Configuración de API no encontrada.")
        return

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    if not os.path.exists(REPORT_PATH):
        print(f"Error: {REPORT_PATH} no encontrado.")
        return

    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "it-reporting@cinlatlogistics.com")
    to_email = "miguel.ochoa@cinlatlogistics.com"

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    files = []
    # Attach HTML
    files.append(("attachment", ("Reporte_Conciso_HelpDesk.html", open(REPORT_PATH, "rb"))))
    
    # Attach Excel if exists
    if os.path.exists(EXCEL_PATH):
        files.append(("attachment", (f"Data_HelpDesk_{TODAY_STR}.xlsx", open(EXCEL_PATH, "rb"))))
    else:
        print(f"Aviso: Excel {EXCEL_PATH} no encontrado para adjuntar.")

    payload = {
        "from": from_email,
        "to": to_email,
        "subject": f"⚡ RESUMEN CONCISO - Help Desk ({datetime.now().strftime('%d/%m/%Y')})",
        "html": html_content
    }

    print(f"Enviando Reporte Conciso a {to_email}...")
    response = requests.post(url, auth=auth, data=payload, files=files if files else None)
    
    if response.status_code == 200:
        print("¡Reporte Conciso enviado con éxito!")
    else:
        print(f"Error: {response.status_code}")
        print(f"Respuesta: {response.text}")

if __name__ == "__main__":
    send_concise_report()
