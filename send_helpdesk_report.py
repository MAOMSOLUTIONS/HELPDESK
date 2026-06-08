import os
import json
import requests
import argparse
from datetime import datetime

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")
RECIPIENTS_PATH = os.path.join(ROOT_DIR, "HelpDesk", "recipients_config.json")

# Dynamic Excel Path based on today's date
TODAY_STR_FILE = datetime.now().strftime("%d_%m_%Y")
EXCEL_FILENAME = f"ReporteHelpdesk{TODAY_STR_FILE}.xlsx"
EXCEL_PATH = os.path.join(ROOT_DIR, "HelpDesk", EXCEL_FILENAME)

REPORTS = [
    {
        "flavor": "IT",
        "html_file": "premium_report_it.html",
        "subject": "IT - Dashboard Estratégico HelpDesk",
        "branding": "SOPORTE DE HELP DESK IT"
    },
    {
        "flavor": "NEGOCIO",
        "html_file": "premium_report_negocio.html",
        "subject": "EJECUTIVO - Dashboard HelpDesk Negocio",
        "branding": "REPORTE EJECUTIVO DE HELP DESK"
    }
]

def send_reports(flavor_filter=None, private=False):
    if not os.path.exists(CONFIG_PATH):
        print("Error: Configuración de API no encontrada.")
        return

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    if not os.path.exists(RECIPIENTS_PATH):
        print(f"Error: {RECIPIENTS_PATH} no encontrado.")
        return

    with open(RECIPIENTS_PATH, "r") as f:
        recipients_map = json.load(f)

    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "it-reporting@cinlatlogistics.com")

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    
    for report in REPORTS:
        flavor_key = report['flavor'].lower()
        
        # Filter if argument provided
        if flavor_filter and flavor_filter.lower() != flavor_key:
            continue

        if private:
            recipients = ["\"Miguel Ochoa\" <miguel.ochoa@cinlatlogistics.com>"]
        else:
            recipients = recipients_map.get(flavor_key, [recipients_map.get("to", ["miguel.ochoa@cinlatlogistics.com"])[0]])
        
        to_email = ", ".join(recipients)
        report_path = os.path.join(ROOT_DIR, "HelpDesk", report['html_file'])
        
        if not os.path.exists(report_path):
            print(f"Error: {report['html_file']} no encontrado.")
            continue

        with open(report_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        files = []
        # Attached Portal
        files.append(("attachment", (report['html_file'], open(report_path, "rb"))))
        
        # Attached Excel (Both get it for audit)
        if os.path.exists(EXCEL_PATH):
            files.append(("attachment", (f"Data_HelpDesk_{datetime.now().strftime('%d_%m_%Y')}.xlsx", open(EXCEL_PATH, "rb"))))
        else:
            print(f"Aviso: Archivo Excel {EXCEL_FILENAME} no encontrado para adjuntar.")

        subject = f"{report['subject']} - {datetime.now().strftime('%d/%m/%Y')}"

        payload = {
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "html": html_content
        }

        print(f"Enviando Reporte {report['flavor']} a {to_email}...")
        response = requests.post(url, auth=auth, data=payload, files=files if files else None)
        
        if response.status_code == 200:
            print(f"¡Reporte {report['flavor']} enviado con éxito!")
        else:
            print(f"Error al enviar {report['flavor']}: {response.status_code}")
            print(f"Respuesta Mailgun: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Envío de reportes de HelpDesk.")
    parser.add_argument("--flavor", type=str, help="Filtro de reporte a enviar (IT o NEGOCIO)")
    parser.add_argument("--private", action="store_true", help="Enviar solo a Miguel Ochoa (Modo Privado)")
    args = parser.parse_args()
    
    send_reports(flavor_filter=args.flavor, private=args.private)
