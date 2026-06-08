import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

# Paths
INPUT_FILE = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\ReporteHelpdesk29_04_2026.xlsx"
OUTPUT_MD = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\helpdesk_pattern_analysis.md"

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
    
    # Keyword mapping
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
    
    # 1. Total KPI
    total_tickets = len(df)
    total_hours = df['Transit_Hours'].sum()
    
    # 2. Group by Category
    cat_group = df.groupby('Categoria').agg(
        Total=('ID', 'count'),
        Horas_Invertidas=('Transit_Hours', 'sum'),
    ).reset_index()
    
    # Calculate Impact (%)
    cat_group['Impacto_Operativo_Porcentaje'] = (cat_group['Horas_Invertidas'] / total_hours) * 100
    cat_group = cat_group.sort_values('Total', ascending=False)
    
    # Monthly distribution per category
    pivot_months = df.pivot_table(index='Categoria', columns='Mes alta', values='ID', aggfunc='count', fill_value=0).reset_index()
    
    # Join
    final_df = pd.merge(cat_group, pivot_months, on='Categoria', how='left')
    
    # Create Markdown Output
    md = "# Análisis de Patrones de Help Desk (Últimos 4 Meses)\n\n"
    md += f"**Total de Tickets Analizados:** {total_tickets}\n"
    md += f"**Total de Horas Hombre Invertidas:** {total_hours:,.1f} horas\n\n"
    
    md += "Este análisis detecta palabras clave en la descripción de los requerimientos para agruparlos en categorías y así identificar qué problemas consumen más tiempo del equipo de IT, revelando oportunidades claras de automatización o capacitación.\n\n"
    
    md += "## 1. Distribución y Patrones Principales\n\n"
    md += "| Problema (Categoría) | Frecuencia Total | Horas Invertidas | Impacto en KPI IT (%) | ENE | FEB | MAR | ABR |\n"
    md += "|---|---|---|---|---|---|---|---|\n"
    
    for _, r in final_df.iterrows():
        cat = r['Categoria']
        tot = r['Total']
        hrs = r['Horas_Invertidas']
        imp = r['Impacto_Operativo_Porcentaje']
        m1 = r.get(1, 0); m2 = r.get(2, 0); m3 = r.get(3, 0); m4 = r.get(4, 0)
        
        md += f"| **{cat}** | {tot} | {hrs:,.1f} hrs | {imp:.1f}% | {m1} | {m2} | {m3} | {m4} |\n"
        
    md += "\n## 2. Detalle de Tiempo Invertido por Técnico en el Patrón Principal\n\n"
    top_cat = final_df.iloc[0]['Categoria']
    md += f"Para la categoría número uno (**{top_cat}**), así se divide el esfuerzo del equipo:\n\n"
    
    top_df = df[df['Categoria'] == top_cat]
    tech_group = top_df.groupby('Responsable').agg(Tickets=('ID', 'count'), Horas=('Transit_Hours', 'sum')).sort_values('Horas', ascending=False)
    
    md += "| Recurso (Responsable) | Tickets Atendidos | Horas Invertidas |\n"
    md += "|---|---|---|\n"
    for tech, r in tech_group.iterrows():
        md += f"| {tech} | {r['Tickets']} | {r['Horas']:.1f} hrs |\n"
        
    md += "\n## 3. Oportunidades de Automatización (Recomendación)\n\n"
    
    for _, r in final_df.head(3).iterrows():
        cat = r['Categoria']
        if cat == "ACCESOS Y CONTRASEÑAS":
            md += f"- **{cat}**: Representa un alto volumen. Se recomienda implementar un portal de Autogestión de Contraseñas (SSPR) integrado al Directorio Activo, permitiendo a los usuarios restablecer sus propias contraseñas usando SMS o correo alterno.\n"
        elif cat == "IMPRESORAS Y ESCÁNERES":
            md += f"- **{cat}**: Muchos tickets son por consumibles o atascos. Sugerencia: Automatizar alertas de SNMP desde las impresoras directo a proveedores o colocar guías de 1 minuto cerca de la impresora para atascos simples.\n"
        elif cat == "RED Y COMUNICACIONES":
            md += f"- **{cat}**: Sugerencia: Desplegar un script diagnóstico automático (`RedCheck.bat`) en los equipos de los usuarios para que ejecute una limpieza de DNS o reinicio de adaptador antes de levantar el ticket.\n"
        elif cat == "EQUIPO DE CÓMPUTO":
            md += f"- **{cat}**: Gran consumo de horas. Podría automatizarse parcialmente desplegando un RMM (Remote Monitoring and Management) que alerte a IT de discos duros llenos o CPUs sobrecargados ANTES de que el usuario lo reporte.\n"
        elif cat == "ERP / SISTEMAS CORE":
            md += f"- **{cat}**: Suelen ser de alta criticidad. Se recomienda crear un 'Chatbot de Nivel 1' en OmegaFusion que responda dudas frecuentes del sistema antes de permitir crear el requerimiento de Help Desk.\n"
    
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print("Analisis generado en Markdown.")

if __name__ == "__main__":
    process()
