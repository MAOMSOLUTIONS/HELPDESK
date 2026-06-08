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

    # Filters: Abril (4), assigned to IT (Responsable != "SIN ASIGNAR"), open (Is_Solved == False)
    # Also filtering out anything that might not be IT if needed, but in HelpDesk usually Responsibility implies IT.
    
    mask = (df['Mes alta'] == 4) & (df['Responsable'] != 'SIN ASIGNAR') & (~df['Is_Solved'])
    open_it = df[mask]
    
    count = len(open_it)
    
    # Send email
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
        
    api_key = config['api_key']
    domain = config['domain']
    from_email = config.get('from_email', "it-reporting@cinlatlogistics.com")
    to_email = "miguel.ochoa@cinlatlogistics.com"
    subject = "Consulta Privada: Tickets de HelpDesk (Abril - Abiertos IT)"
    
    # Build list of tickets in HTML
    rows_html = ""
    for _, r in open_it.iterrows():
        sol_full = str(r.get('Solicitud', '')).replace('\n', '<br>')
        rows_html += f"<tr><td style='padding:5px; border-bottom:1px solid #ccc;'><b>{r['ID']}</b></td><td style='padding:5px; border-bottom:1px solid #ccc;'>{r['Fecha alta']}</td><td style='padding:5px; border-bottom:1px solid #ccc;'>{r['Responsable']}</td><td style='padding:5px; border-bottom:1px solid #ccc;'>{r['Solicitante']}</td><td style='padding:5px; border-bottom:1px solid #ccc; font-size:11px;'>{sol_full}</td></tr>"

    email_body = f"""
    <div style="font-family: Calibri, Arial, sans-serif; font-size: 11pt; color: #000;">
        Hola Miguel,<br><br>
        De acuerdo a tu consulta sobre el reporte de Help Desk, actualmente hay <strong>{count}</strong> tickets de Abril que están asignados a un técnico y <u>aún no están cerrados</u>.<br><br>
        A continuación el listado detallado:<br><br>
        <table style="border-collapse: collapse; width: 100%; font-size: 12px; text-align: left;">
            <thead style="background-color: #1a73e8; color: #fff;">
                <tr><th style="padding:5px;">ID</th><th style="padding:5px;">FECHA ALTA</th><th style="padding:5px;">RESPONSABLE</th><th style="padding:5px;">SOLICITANTE</th><th style="padding:5px;">DESCRIPCIÓN</th></tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        <br>
        Saludos,<br>
        OmegaFusion
    </div>
    """
    
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    payload = {
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "html": email_body
    }

    resp = requests.post(url, auth=auth, data=payload)
    print("Tickets encontrados:", count)
    print("Email Sent:", resp.status_code)

if __name__ == "__main__":
    process()
