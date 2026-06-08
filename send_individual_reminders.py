import pandas as pd
import numpy as np
import os
import json
import requests
from datetime import datetime

ROOT_DIR = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP"
INPUT_DIR = os.path.join(ROOT_DIR, "HelpDesk")
INPUT_FILE = os.path.join(INPUT_DIR, "ReporteHelpdesk29_04_2026.xlsx")
CONFIG_PATH = os.path.join(ROOT_DIR, "MailgunTester", "config.json")

SPANISH_MONTHS = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12}

EMAIL_MAP = {
    "SALAZAR MARTINEZ ERNESTO": "ernesto.salazar@cinlatlogistics.com",
    "ERNESTO SALAZAR": "ernesto.salazar@cinlatlogistics.com",
    "GARCIA ROMERO MANUEL": "manuel.garcia@cinlatlogistics.com",
    "MANUEL GARCIA": "manuel.garcia@cinlatlogistics.com",
    "CASAS VALDEZ VICTOR MANUEL": "victor.casas@cinlatlogistics.com",
    "VICTOR CASAS": "victor.casas@cinlatlogistics.com",
    "CLEMENTE CLEMENTE ELIZABETH": "elizabeth.clemente@cinlatlogistics.com",
    "ELIZABETH CLEMENTE": "elizabeth.clemente@cinlatlogistics.com",
    "JAIME CABALLERO": "jaime.caballero@cinlatlogistics.com",
    "ERICK POZAS": "erick.pozas@cinlatlogistics.com",
    "SABINO NAVARRO": "sabino.navarro@cinlatlogistics.com",
    "DANIEL OCHOA": "daniel.ochoa@cinlatlogistics.com",
    "SANTANDER MENDOZA": "santander.mendoza@cinlatlogistics.com"
}

def parse_spanish_date(date_str):
    if pd.isna(date_str) or not isinstance(date_str, str): return pd.NaT
    try:
        parts = date_str.replace(",", "").split()
        if len(parts) != 3: return pd.NaT
        month_num = SPANISH_MONTHS.get(parts[0].capitalize())
        if not month_num: return pd.NaT
        return datetime(int(parts[2]), month_num, int(parts[1]))
    except: return pd.NaT

def process():
    df = pd.read_excel(INPUT_FILE, skiprows=4)
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        c_low = c.lower()
        if "alta" in c_low:
            if ("a" in c_low and "o" in c_low and "id" not in c_low) or "ao" in c_low or "año" in c_low or "ano" in c_low:
                df.rename(columns={c: "Año"}, inplace=True)
            elif "mes" in c_low:
                df.rename(columns={c: "Mes alta"}, inplace=True)
                
    df = df.loc[:, ~df.columns.duplicated()]
    df['dt_alta'] = df['Fecha alta'].apply(parse_spanish_date)
    df['dt_solucion'] = df['Fecha solucion'].apply(parse_spanish_date)
    df['Is_Solved'] = df['dt_solucion'].notnull()
    df['Responsable'] = df['Responsable'].fillna("SIN ASIGNAR").astype(str).str.strip().str.upper()
    df['Solicitante'] = df['Solicitante'].fillna("N/A").astype(str).str.strip().str.upper()

    current_month = 4
    now = datetime.now()
    
    # Filter: Not solved, assigned, current month, open for more than 2 days
    mask = (df['Is_Solved'] == False) & \
           (df['Responsable'] != 'SIN ASIGNAR') & \
           (df['Mes alta'] == current_month) & \
           ((now - df['dt_alta']).dt.total_seconds() / 86400 > 2)
           
    open_tickets = df[mask]
    
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
        
    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "it-reporting@cinlatlogistics.com")
    cc_email = "miguel.ochoa@cinlatlogistics.com"
    
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)

    grouped = open_tickets.groupby('Responsable')
    
    print(f"Se encontraron {len(open_tickets)} tickets asignados repartidos en {len(grouped)} responsables.")
    
    for resp_name, group in grouped:
        # Resolve email
        tech_email = EMAIL_MAP.get(resp_name.strip().upper())
        if not tech_email:
            print(f"No se encontro correo para: {resp_name}. Omitiendo.")
            continue
        rows_html = ""
        for _, r in group.iterrows():
            sol_full = str(r.get('Solicitud', '')).replace('\n', '<br>')
            rows_html += f"<tr><td style='padding:8px; border-bottom:1px solid #ccc;'><b>{r['ID']}</b></td><td style='padding:8px; border-bottom:1px solid #ccc;'>{r['Fecha alta']}</td><td style='padding:8px; border-bottom:1px solid #ccc;'>{r['Solicitante']}</td><td style='padding:8px; border-bottom:1px solid #ccc; font-size:11px;'>{sol_full}</td></tr>"

        subject = f"Recordatorio de Atención a Tickets - {resp_name.title()}"
        
        email_body = f"""
        <div style="font-family: Calibri, Arial, sans-serif; font-size: 12pt; color: #333; line-height: 1.5; max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">
            <p>Estimado(a) <strong>{resp_name.title()}</strong>,</p>
            
            <p>Espero que te encuentres muy bien.</p>
            
            <p>Este correo es un amable recordatorio para informarte que actualmente tienes <strong>{len(group)} requerimientos de Help Desk</strong> asignados a ti, generados durante este mes, que aún se encuentran <strong>abiertos y requieren urgentemente tu atención para ser cerrados</strong>.</p>
            
            <table style="border-collapse: collapse; width: 100%; font-size: 12px; text-align: left; margin: 20px 0;">
                <thead style="background-color: #2563eb; color: #fff;">
                    <tr><th style="padding:10px;">ID</th><th style="padding:10px;">FECHA ALTA</th><th style="padding:10px;">SOLICITANTE</th><th style="padding:10px;">DESCRIPCIÓN</th></tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            
            <p style="padding: 15px; background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 4px;">
                <strong>Nota Importante:</strong> Recuerda que la atención oportuna y cierre de estos requerimientos forma parte de los indicadores clave (KPIs) por los cuales nos miden en el departamento de IT.
            </p>
            
            <p><strong>¿Tienes algún impedimento?</strong><br>
            Si existe algún bloqueo, retraso, o dependes de terceros para poder avanzar con la resolución de alguno de estos tickets, por favor coméntalo de inmediato en el área para poder apoyarte y buscar una solución conjunta.</p>
            
            <p>Contamos con tu apoyo.<br><br>
            Saludos,<br>
            <strong>Área de IT / OmegaFusion</strong></p>
        </div>
        """
        
        payload = {
            "from": from_email,
            "to": tech_email,
            "cc": cc_email,
            "subject": subject,
            "html": email_body
        }

        response = requests.post(url, auth=auth, data=payload)
        print(f"Correo enviado a {tech_email} (CC: {cc_email}). Status: {response.status_code}")

if __name__ == "__main__":
    process()
