import os
import json
import requests
from datetime import datetime
import argparse

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")
RECIPIENTS_PATH = os.path.join(ROOT_DIR, "HelpDesk", "recipients_config.json")
DASHBOARD_PATH = os.path.join(ROOT_DIR, "HelpDesk", "priority_dashboard.html")
EXCEL_PATH = os.path.join(ROOT_DIR, "HelpDesk", "Prioridades_IT_2026_2_06_2026.xlsx")

def send_it_status_email():
    global args
    print("Iniciando proceso de envío de Estatus de Requerimientos IT...")
    
    # 1. Load Configurations
    if not os.path.exists(CONFIG_PATH):
        print("Error: Mailgun config no encontrada.")
        return
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    if not os.path.exists(RECIPIENTS_PATH):
        print("Error: recipients_config.json no encontrada.")
        return
    with open(RECIPIENTS_PATH, "r") as f:
        recipients_map = json.load(f)

    # 2. Setup Recipients from Config
    if args.private:
        all_recipients = ["\"Miguel Ochoa\" <miguel.ochoa@cinlatlogistics.com>"]
    else:
        it_list = recipients_map.get('it', [])
        negocio_list = recipients_map.get('negocio', [])
        all_recipients = list(set(it_list + negocio_list))
        
    to_email = ", ".join(all_recipients)

    # 2. Load Content
    if not os.path.exists(DASHBOARD_PATH):
        print("Error: priority_dashboard.html no encontrado.")
        return
    with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
        html_dashboard = f.read()

    # 3. Prepare Email Body (Matching image)
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    today = datetime.now()
    today_str = f"{today.day} de {meses[today.month - 1]} del {today.year}"
    subject = f"Reporte de Requerimientos Actualizado al {today_str}"
    
    # 4. Prepare Attachments
    files = []
    if os.path.exists(EXCEL_PATH):
        files.append(("attachment", ("Prioridades_IT_2026.xlsx", open(EXCEL_PATH, "rb"))))
    
    if os.path.exists(DASHBOARD_PATH):
        files.append(("attachment", ("Dashboard_Interactivo_IT.html", open(DASHBOARD_PATH, "rb"))))
    else:
        print("Aviso: priority_dashboard.html no encontrado para adjuntar.")

    # 5. Add Interactive Button to Body
    local_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\priority_dashboard.html"
    button_html = f"""
    <div style="margin: 30px 0; text-align: center;">
        <a href="file:///{local_path.replace(' ', '%20')}" style="background-color: #2563eb; color: #ffffff; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-family: Arial, sans-serif; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            🚀 ABRIR DASHBOARD (Acceso Directo)
        </a>
        <br><br>
        <a href="cid:Dashboard_Interactivo_IT.html" style="color: #2563eb; font-weight: bold; text-decoration: underline; font-family: Arial, sans-serif; font-size: 13px;">
            Ver versión adjunta
        </a>
        <p style="font-size: 10px; color: #64748b; margin-top: 10px;">(Nota: El acceso directo funciona si estás en tu equipo. Si no abre, por favor descarga el adjunto)</p>
    </div>
    """
    
    # Prepend button and text message to the HTML content
    email_body = f"""
    <div style="font-family: Calibri, Arial, sans-serif; font-size: 11pt; color: #000; margin-bottom: 20px;">
        Excelente tarde.<br><br>
        Anexo el reporte de requerimientos actualizado al {today_str}.<br><br>
        
        <div style="background-color: #eff6ff; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0; border-radius: 4px;">
            <strong style="color: #1e3a8a; font-size: 14px;">💡 Instrucciones de Uso: Dashboard y Filtros</strong>
            <ul style="margin-top: 8px; margin-bottom: 0; color: #1e40af; font-size: 13px;">
                <li><strong>Gráfica Interactiva:</strong> Al inicio del dashboard verás una gráfica de barras con los requerimientos concluidos agrupados por mes.</li>
                <li><strong>Filtro por Mes:</strong> Usa el botón desplegable <strong style="background:#fff; padding:2px 5px; border-radius:4px; border:1px solid #bfdbfe;">📅 MES / GRUPO</strong> en la barra superior para filtrar la tabla y ver exclusivamente los requerimientos terminados en <em>Marzo, Abril o Mayo</em>.</li>
                <li><strong>Búsqueda:</strong> Puedes escribir cualquier palabra clave en la barra de búsqueda para encontrar requerimientos específicos.</li>
            </ul>
        </div>
        
        {button_html}
        <br>
        Saludos<br>
        <strong>Miguel Ochoa</strong>
    </div>
    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
    {html_dashboard}
    """

    # 5. Send via Mailgun
    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "it-reporting@cinlatlogistics.com")
    
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    
    payload = {
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "html": email_body
    }

    print(f"Enviando reporte a {len(all_recipients)} destinatarios...")
    response = requests.post(url, auth=auth, data=payload, files=files if files else None)
    
    if response.status_code == 200:
        print("¡Estatus de Requerimientos IT enviado con éxito!")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--private", action="store_true")
    args = parser.parse_args()
    send_it_status_email()
