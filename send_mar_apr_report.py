import os
import json
import requests
import pandas as pd
from datetime import datetime

# Paths
ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")
EXCEL_PATH = os.path.join(ROOT_DIR, "HelpDesk", "Requerimientos_IT_24_04_2026_VF2.xlsx")
DASHBOARD_PATH = os.path.join(ROOT_DIR, "HelpDesk", "dashboard_marzo_abril.html")

def generate_and_send():
    # 1. Load and process data
    if not os.path.exists(EXCEL_PATH):
        print("Excel no encontrado.")
        return
        
    df = pd.read_excel(EXCEL_PATH)
    term = df[df['Estatus'].astype(str).str.contains('Terminado', case=False, na=False)].copy()
    term['Fecha_entrega'] = pd.to_datetime(term['Fecha_entrega'], errors='coerce', dayfirst=True)
    mar_apr = term[(term['Fecha_entrega'].dt.month.isin([3, 4])) & (term['Fecha_entrega'].dt.year == 2026)].copy()
    mar_apr = mar_apr.sort_values('Fecha_entrega')
    
    total_completados = len(mar_apr)
    clientes_unicos = mar_apr['Cliente'].nunique()
    
    # Client count for chart
    client_counts = mar_apr['Cliente'].value_counts().to_dict()
    client_labels = list(client_counts.keys())
    client_values = list(client_counts.values())

    # Format table rows
    mar_apr['Fecha_entrega_str'] = mar_apr['Fecha_entrega'].dt.strftime('%d/%m/%Y')
    
    rows_html = ""
    for _, r in mar_apr.iterrows():
        rows_html += f"""
        <tr>
            <td style="padding:12px; border-bottom:1px solid #e2e8f0; font-size:13px; color:#1e293b;"><b>{r['Cliente']}</b></td>
            <td style="padding:12px; border-bottom:1px solid #e2e8f0; font-size:13px; color:#334155;">{r['Requerimiento']}</td>
            <td style="padding:12px; border-bottom:1px solid #e2e8f0; font-size:13px; color:#0f172a; font-weight:600;">{r['Fecha_entrega_str']}</td>
        </tr>
        """

    # 2. Generate HTML Dashboard
    html_dashboard = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard de Avance - Marzo y Abril 2026</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 20px; }}
            .container {{ max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
            h1 {{ color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; margin-top: 0; }}
            .kpi-container {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .kpi-card {{ flex: 1; background: #eff6ff; padding: 20px; border-radius: 8px; border: 1px solid #bfdbfe; text-align: center; }}
            .kpi-title {{ font-size: 14px; color: #475569; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px; }}
            .kpi-value {{ font-size: 36px; font-weight: bold; color: #2563eb; margin-top: 10px; }}
            .chart-container {{ width: 100%; max-width: 600px; margin: 0 auto 40px auto; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background-color: #f1f5f9; padding: 12px; text-align: left; font-size: 13px; color: #475569; text-transform: uppercase; border-bottom: 2px solid #cbd5e1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Dashboard de Avance: Requerimientos Concluidos (Marzo - Abril 2026)</h1>
            
            <div class="kpi-container">
                <div class="kpi-card">
                    <div class="kpi-title">Total Concluidos</div>
                    <div class="kpi-value">{total_completados}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Clientes Atendidos</div>
                    <div class="kpi-value">{clientes_unicos}</div>
                </div>
            </div>

            <div class="chart-container">
                <canvas id="clientChart"></canvas>
            </div>

            <h2>Detalle de Requerimientos</h2>
            <table>
                <thead>
                    <tr>
                        <th>Cliente</th>
                        <th>Requerimiento</th>
                        <th>Fecha de Entrega</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>

        <script>
            const ctx = document.getElementById('clientChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(client_labels)},
                    datasets: [{{
                        label: 'Requerimientos Concluidos',
                        data: {json.dumps(client_values)},
                        backgroundColor: '#3b82f6',
                        borderRadius: 4
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Requerimientos Concluidos por Cliente',
                            font: {{ size: 16 }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """

    with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
        f.write(html_dashboard)

    # 3. Setup Email
    if not os.path.exists(CONFIG_PATH):
        print("Configuración Mailgun no encontrada.")
        return
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    api_key = config['api_key']
    domain = config['domain']
    to_email = "miguel.ochoa@cinlatlogistics.com"
    from_email = config.get('from_email', "it-reporting@cinlatlogistics.com")
    subject = "📊 Reporte y Dashboard de Avance: Marzo y Abril 2026"

    email_body = f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto; background: #fff; padding: 20px;">
        <h2 style="color: #2563eb;">Reporte de Requerimientos Concluidos</h2>
        <p>Hola Miguel,</p>
        <p>Adjunto a este correo encontrarás el <strong>Dashboard de Avance</strong> interactivo con los {total_completados} requerimientos concluidos durante los meses de marzo y abril de 2026.</p>
        
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin: 20px 0;">
            <p style="margin: 0;"><strong>Resumen Rápido:</strong></p>
            <ul style="margin-top: 10px;">
                <li>Total requerimientos completados: <strong>{total_completados}</strong></li>
                <li>Clientes atendidos: <strong>{clientes_unicos}</strong></li>
            </ul>
        </div>
        
        <p><strong>💡 Instrucciones:</strong> Por favor, descarga y abre el archivo adjunto <code>dashboard_marzo_abril.html</code> en tu navegador para ver las gráficas interactivas y el detalle completo de cada requerimiento.</p>
        <br>
        <p>Saludos,<br><strong>Antigravity AI</strong></p>
    </div>
    """

    files = [("attachment", ("dashboard_marzo_abril.html", open(DASHBOARD_PATH, "rb")))]

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    
    payload = {
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "html": email_body
    }

    print("Enviando correo con Dashboard...")
    response = requests.post(url, auth=auth, data=payload, files=files)
    
    if response.status_code == 200:
        print("¡Reporte enviado exitosamente!")
    else:
        print(f"Error al enviar: {response.status_code} - {response.text}")

if __name__ == "__main__":
    generate_and_send()
