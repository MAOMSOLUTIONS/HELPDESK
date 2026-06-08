import os
import json
import requests
import pandas as pd
from datetime import datetime

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")
DASHBOARD_PATH = os.path.join(ROOT_DIR, "HelpDesk", "priority_dashboard.html")
EXCEL_PATH = os.path.join(ROOT_DIR, "HelpDesk", "Prioridades_IT_2026_2_06_2026.xlsx")

def send_private_report():
    print("Generando cuerpo de correo Optimizado...")
    
    # 1. Load Data for the Body
    if not os.path.exists(EXCEL_PATH):
        print("Excel no encontrado.")
        return
    df = pd.read_excel(EXCEL_PATH).fillna("")
    
    # KPIs
    total = len(df)
    terminados = len(df[df['Estatus'].astype(str).str.contains('Terminado', case=False, na=False)])
    success_rate = round((terminados / total * 100), 1) if total > 0 else 0
    pendiente = total - terminados

    # Filter for Lite Table (Top 10 most relevant or all Actives)
    df_lite = df[df['Estatus'] != 'Terminado'].head(15) # Show actives first
    
    rows_html = ""
    for _, r in df_lite.iterrows():
        rows_html += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid #eee; font-size:12px;">{r['ID']}</td>
            <td style="padding:8px; border-bottom:1px solid #eee; font-size:12px;"><b>{r['Cliente']}</b></td>
            <td style="padding:8px; border-bottom:1px solid #eee; font-size:12px;">{r['Requerimiento']}</td>
            <td style="padding:8px; border-bottom:1px solid #eee; font-size:12px; color:#2563eb; font-weight:bold;">{r['Estatus']}</td>
        </tr>
        """

    # 2. Setup Email Lite Body (Safe for Outlook)
    today_str = datetime.now().strftime("%d/%m/%Y")
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
        <div style="background-color: #1e293b; color: white; padding: 20px; border-radius: 10px 10px 0 0;">
            <h2 style="margin:0;">Resumen Ejecutivo: Requerimientos IT</h2>
            <p style="margin:5px 0 0 0; opacity:0.8;">Actualización al {today_str}</p>
        </div>
        
        <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 10px 10px;">
            <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 20px;">
                <tr>
                    <td align="center" style="background:#f8fafc; padding:15px; border-radius:8px; border:1px solid #eee;">
                        <span style="font-size:10px; color:#64748b; text-transform:uppercase; font-weight:bold;">Eficacia Global</span><br>
                        <span style="font-size:24px; font-weight:bold; color:#22c55e;">{success_rate}%</span>
                    </td>
                    <td width="10"></td>
                    <td align="center" style="background:#f8fafc; padding:15px; border-radius:8px; border:1px solid #eee;">
                        <span style="font-size:10px; color:#64748b; text-transform:uppercase; font-weight:bold;">Total Proyectos</span><br>
                        <span style="font-size:24px; font-weight:bold; color:#2563eb;">{total}</span>
                    </td>
                    <td width="10"></td>
                    <td align="center" style="background:#f8fafc; padding:15px; border-radius:8px; border:1px solid #eee;">
                        <span style="font-size:10px; color:#64748b; text-transform:uppercase; font-weight:bold;">Cerrados</span><br>
                        <span style="font-size:24px; font-weight:bold; color:#16a34a;">{terminados}</span>
                    </td>
                </tr>
            </table>

            <h3 style="color:#1e293b; border-bottom: 2px solid #3b82f6; padding-bottom: 5px;">Proyectos Activos (Muestra)</h3>
            <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">
                <thead>
                    <tr style="background:#f1f5f9;">
                        <th align="left" style="padding:10px; font-size:11px;">ID</th>
                        <th align="left" style="padding:10px; font-size:11px;">CLIENTE</th>
                        <th align="left" style="padding:10px; font-size:11px;">REQUERIMIENTO</th>
                        <th align="left" style="padding:10px; font-size:11px;">ESTATUS</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <div style="margin-top:25px; padding:15px; background:#eff6ff; border-radius:8px; border:1px solid #bfdbfe; text-align:center;">
                <p style="margin:0; font-size:13px; color:#1e40af;">
                    <b>💡 Acceso Dinámico:</b> Para ver el reporte con filtros, buscador y detalles completos, abre el archivo adjunto <b>"Dashboard_Privado_IT.html"</b> o utiliza tu Portal IT local.
                </p>
            </div>
        </div>
        
        <p style="font-size:11px; color:#94a3b8; text-align:center; margin-top:20px;">
            CINLAT LOGISTICS &bull; OMEGAFUSION OPS &bull; 2026
        </p>
    </body>
    </html>
    """

    # 3. Setup Mailgun
    if not os.path.exists(CONFIG_PATH): return
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "intranet-cinlat@cinlatlogistics.com")
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
