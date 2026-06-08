import pandas as pd
import numpy as np
import os
from datetime import datetime

INPUT_FILE = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\ReporteHelpdesk29_04_2026.xlsx"
OUTPUT_FILE = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\scratch_tech_analysis.md"

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

    # Prepare markdown
    md = "# Detalle de Desempeño Técnico por Categoría (Ene-Abr 2026)\n\n"
    md += "A continuación se desglosa **cada tipo de problema**, indicando cuánto tiempo le invierte cada miembro del equipo de IT, desglosado por mes y mostrando el **Promedio de Atención** por ticket.\n\n"

    # Iterate over each category (sorted by total volume to show the biggest issues first)
    categories = df['Categoria'].value_counts().index.tolist()
    
    for cat in categories:
        cat_df = df[df['Categoria'] == cat]
        
        md += f"## {cat}\n"
        md += f"**Volumen Total:** {len(cat_df)} tickets | **Horas Totales Invertidas:** {cat_df['Transit_Hours'].sum():,.1f} hrs\n\n"
        
        # Group by Responsable
        tech_group = cat_df.groupby('Responsable')
        
        # Build table
        md += "| Técnico Responsable | Total Tickets | Promedio (hrs/ticket) | ENE | FEB | MAR | ABR |\n"
        md += "|---|---|---|---|---|---|---|\n"
        
        # Get data per tech
        tech_stats = []
        for tech, group in tech_group:
            tot_tickets = len(group)
            tot_hrs = group['Transit_Hours'].sum()
            avg_hrs = tot_hrs / tot_tickets if tot_tickets > 0 else 0
            
            # Monthly breakdown
            m_counts = group['Mes alta'].value_counts()
            m1 = m_counts.get(1, 0)
            m2 = m_counts.get(2, 0)
            m3 = m_counts.get(3, 0)
            m4 = m_counts.get(4, 0)
            
            tech_stats.append({
                'tech': tech, 'tickets': tot_tickets, 'avg': avg_hrs, 'hrs': tot_hrs,
                'm1': m1, 'm2': m2, 'm3': m3, 'm4': m4
            })
            
        # Sort by total hours descending within the category
        tech_stats = sorted(tech_stats, key=lambda x: x['hrs'], reverse=True)
        
        for t in tech_stats:
            # Highlight high average
            avg_str = f"{t['avg']:,.1f} hrs"
            if t['avg'] > 72:  # More than 3 days average
                avg_str = f"**{avg_str} ⚠️**"
                
            md += f"| {t['tech']} | {t['tickets']} | {avg_str} | {t['m1']} | {t['m2']} | {t['m3']} | {t['m4']} |\n"
        
        md += "\n"
        
    md += "> [!TIP]\n"
    md += "> Los promedios marcados con **⚠️** indican que el técnico tarda en promedio más de 72 horas (3 días) en dar solución o cerrar los tickets de esa categoría, lo que indica un área de oportunidad, carga excesiva o dependencia externa prolongada.\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    process()
