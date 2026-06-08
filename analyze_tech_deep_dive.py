import pandas as pd
import numpy as np
import os
from datetime import datetime

INPUT_FILE = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\ReporteHelpdesk29_04_2026.xlsx"
OUTPUT_FILE = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\scratch_deep_dive.md"

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

def categorize_issue(text):
    text = str(text).lower()
    if pd.isna(text): return "OTRO"
    categories = {
        "ACCESOS Y CONTRASEÑAS": ["contraseña", "password", "acceso", "desbloqueo", "bloqueado", "login", "credenciales", "cuenta"],
        "IMPRESORAS Y ESCÁNERES": ["impresora", "imprimir", "toner", "tinta", "escaner", "impresion", "zebra", "etiqueta"],
        "RED Y COMUNICACIONES": ["red", "internet", "wifi", "conexion", "vpn", "ip", "cable", "switch", "enlace"],
        "EQUIPO DE CÓMPUTO": ["pantalla", "monitor", "teclado", "mouse", "bateria", "laptop", "cpu", "lento", "enciende", "hardware", "memoria"],
        "CORREO Y OFFICE": ["correo", "outlook", "excel", "word", "office", "teams", "email", "buzon"],
        "ERP / SISTEMAS CORE": ["sap", "tms", "omegafusion", "wms", "sistema", "error sistema", "erp", "portal"],
        "TELEFONÍA": ["telefono", "extension", "celular", "linea", "diadema"],
        "RESPALDOS / SERVIDORES": ["respaldo", "servidor", "carpeta compartida", "onedrive", "sharepoint", "espacio"],
    }
    for cat, keywords in categories.items():
        if any(kw in text for kw in keywords):
            return cat
    return "OTROS REQUERIMIENTOS MENORES"

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
    ref_date = datetime.now()
    df['Transit_Hours'] = np.where(df['Is_Solved'], 
                                   (df['dt_solucion'] - df['dt_alta']).dt.total_seconds() / 3600, 
                                   (ref_date - df['dt_alta']).dt.total_seconds() / 3600)
    df['Responsable'] = df['Responsable'].fillna("SIN ASIGNAR").astype(str).str.strip().str.upper()
    df['Categoria'] = df['Solicitud'].apply(categorize_issue)
    df['Solicitud_Clean'] = df['Solicitud'].astype(str).str.replace('\n', ' ')

    md = "# Análisis Profundo: Desempeño, Rango de Horas y Top Tickets por Técnico\n\n"
    md += "Este reporte detalla para cada categoría y técnico: el volumen mensual, el Promedio (avg), Piso (Mínimo) y Techo (Máximo) de horas invertidas. Adicionalmente, se muestran los **5 tickets más representativos** (mayor tiempo invertido) para justificar los picos.\n\n"

    categories = df['Categoria'].value_counts().index.tolist()
    
    for cat in categories:
        cat_df = df[df['Categoria'] == cat]
        md += f"## 📌 {cat}\n\n"
        
        tech_group = cat_df.groupby('Responsable')
        tech_stats = []
        for tech, group in tech_group:
            tot_tickets = len(group)
            if tot_tickets == 0: continue
            
            piso = group['Transit_Hours'].min()
            techo = group['Transit_Hours'].max()
            promedio = group['Transit_Hours'].mean()
            
            m_counts = group['Mes alta'].value_counts()
            m1 = m_counts.get(1, 0)
            m2 = m_counts.get(2, 0)
            m3 = m_counts.get(3, 0)
            m4 = m_counts.get(4, 0)
            
            top5 = group.nlargest(5, 'Transit_Hours')[['ID', 'Solicitante', 'Transit_Hours', 'Solicitud_Clean']]
            
            tech_stats.append({
                'tech': tech, 'tickets': tot_tickets, 'avg': promedio, 'min': piso, 'max': techo,
                'm1': m1, 'm2': m2, 'm3': m3, 'm4': m4, 'top5': top5
            })
            
        tech_stats = sorted(tech_stats, key=lambda x: x['avg'], reverse=True)
        
        for t in tech_stats:
            md += f"### 👨‍💻 {t['tech']}\n"
            md += f"- **Tickets:** {t['tickets']} (ENE: {t['m1']} | FEB: {t['m2']} | MAR: {t['m3']} | ABR: {t['m4']})\n"
            
            alert = " ⚠️" if t['avg'] > 72 else ""
            md += f"- **Horas Invertidas:** Promedio: **{t['avg']:,.1f} hrs{alert}** | Piso (Min): {t['min']:,.1f} hrs | Techo (Max): {t['max']:,.1f} hrs\n\n"
            
            md += "**Top 5 Tickets Más Representativos (Mayor Tiempo):**\n"
            md += "| ID | Solicitante | Horas | Resumen del Problema |\n"
            md += "|---|---|---|---|\n"
            for _, r in t['top5'].iterrows():
                short_sol = r['Solicitud_Clean'][:100] + ("..." if len(r['Solicitud_Clean']) > 100 else "")
                md += f"| {r['ID']} | {r['Solicitante']} | {r['Transit_Hours']:,.1f} | {short_sol} |\n"
            
            md += "\n---\n\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    process()
