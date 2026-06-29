import os
import json
import requests
import pandas as pd
from datetime import datetime

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")
DASHBOARD_PATH = os.path.join(ROOT_DIR, "HelpDesk", "priority_dashboard.html")
EXCEL_PATH = os.path.join(ROOT_DIR, "HelpDesk", "Prioridades_IT_2026_15_06_2026.xlsx")
RECIPIENTS_PATH = os.path.join(ROOT_DIR, "HelpDesk", "recipients_config.json")

def send_private_report():
    print("Generando cuerpo de correo Optimizado...")
    
    today_str = datetime.now().strftime("%d/%m/%Y")
    if not os.path.exists(DASHBOARD_PATH):
        print("Dashboard HTML no encontrado.")
        return
    with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
        email_body = f.read()

    # 3. Setup Mailgun
    if not os.path.exists(CONFIG_PATH): return
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "intranet-cinlat@cinlatlogistics.com")
    
    if os.path.exists(RECIPIENTS_PATH):
        with open(RECIPIENTS_PATH, "r") as f:
            recmap = json.load(f)
            to_email = ", ".join(recmap.get("it", ["miguel.ochoa@cinlatlogistics.com"]))
    else:
        to_email = "miguel.ochoa@cinlatlogistics.com"
        
    subject = f"Estatus de Requerimientos IT - {today_str} (Actualizado)"

    # 4. Attachments
    files = []
    if os.path.exists(EXCEL_PATH):
        files.append(("attachment", (f"Prioridades_IT_{today_str.replace('/','_')}.xlsx", open(EXCEL_PATH, "rb"))))
    if os.path.exists(DASHBOARD_PATH):
        files.append(("attachment", ("Dashboard_Privado_IT.html", open(DASHBOARD_PATH, "rb"))))

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    
    payload = {
        "from": f"CINLAT IT Reporting <{from_email}>",
        "to": to_email,
        "subject": subject,
        "html": email_body,
        "o:tag": "priority_report_v4"
    }

    print(f"Enviando reporte con Previsualización a {to_email}...")
    response = requests.post(url, auth=auth, data=payload, files=files if files else None)
    
    if response.status_code == 200:
        print("¡Reporte con previsualización enviado con éxito!")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    send_private_report()
