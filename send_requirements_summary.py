import os
import json
import requests
from datetime import datetime

# Paths - Updated to match the user's structure
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")
OVERVIEW_PATH = os.path.join(ROOT_DIR, "SPECTRA_iTMS", "SPECTRA_iTMS_Functional_Overview.md")

def send_requirements_email():
    # 1. Load Mailgun Configuration
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Configuración no encontrada en {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    api_key = config['api_key']
    domain = config['domain']
    to_email = "miguel.ochoa@cinlatlogistics.com"
    from_email = config.get('from_email', "it-reporting@cinlatlogistics.com")

    # 2. Read Requirements Content
    if not os.path.exists(OVERVIEW_PATH):
        print(f"Error: Documento de requerimientos no encontrado en {OVERVIEW_PATH}")
        return

    with open(OVERVIEW_PATH, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 3. Create HTML Body (Premium Look)
    # Simple conversion from MD headers and bullets for the email
    html_content = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f9; padding: 40px; color: #333;">
        <div style="max-width: 800px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-top: 8px solid #0056b3;">
            <h1 style="color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px;">📋 SPECTRA iTMS - Resumen de Requerimientos y Capacidades</h1>
            <p style="font-size: 1.1em; color: #666;">Hola Miguel, a continuación te comparto el resumen de los requerimientos y capacidades funcionales que hemos consolidado para el proyecto <strong>SPECTRA iTMS Quantum</strong>.</p>
            
            <div style="background: #f0f4f8; padding: 25px; border-radius: 8px; margin: 20px 0;">
                <pre style="white-space: pre-wrap; font-family: inherit; font-size: 1em; line-height: 1.6;">{md_content}</pre>
            </div>
            
            <h3 style="color: #0056b3;">Archivos Complementarios:</h3>
            <ul>
                <li><strong>Detalle Operativo IT:</strong> Requerimientos_IT_08_04_2026_VF.xlsx</li>
                <li><strong>Minuta de Seguimiento:</strong> Reunión_IT_06_04_2026_1.xlsx</li>
            </ul>

            <hr style="border: 0; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="font-size: 0.9em; color: #888; text-align: center;">
                Enviado automáticamente por <strong>Antigravity AI</strong><br>
                <em>Ecosistema de Inteligencia Logística CINLAT</em>
            </p>
        </div>
    </body>
    </html>
    """

    # 4. Send via Mailgun
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    
    payload = {
        "from": from_email,
        "to": to_email,
        "subject": f"📌 Resumen de Requerimientos: SPECTRA iTMS Quantum ({datetime.now().strftime('%d/%m/%Y')})",
        "html": html_content
    }

    print(f"Enviando correo a {to_email}...")
    response = requests.post(url, auth=auth, data=payload)
    
    if response.status_code == 200:
        print("¡Correo enviado con éxito!")
    else:
        print(f"Error al enviar: {response.status_code}")
        print(f"Respuesta Mailgun: {response.text}")

if __name__ == "__main__":
    send_requirements_email()
