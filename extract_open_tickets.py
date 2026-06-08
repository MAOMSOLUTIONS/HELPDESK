import pandas as pd
import os
import json
from datetime import datetime

INPUT_FILE = r"c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\ReporteHelpdesk04_05_2026.xlsx"

MONTH_MAP = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
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

ref_date = datetime(2026, 5, 4)
df['Transit_Hours'] = df.apply(lambda r: (r['dt_solucion'] - r['dt_alta']).total_seconds() / 3600 if r['Is_Solved'] else (ref_date - r['dt_alta']).total_seconds() / 3600, axis=1)
df['Transit_Days'] = (df['Transit_Hours'] / 24).fillna(0).round(1)

df['Responsable'] = df['Responsable'].fillna("SIN ASIGNAR").astype(str).str.strip().str.upper()
df['Departamento'] = df['Departamento'].fillna("GENERAL").astype(str).str.strip().str.upper()
df['Solicitante'] = df['Solicitante'].fillna("N/A").astype(str).str.strip().str.upper()
df['Estado'] = df['Estado'].fillna("PENDIENTE").astype(str).str.upper()
df['Solicitud'] = df['Solicitud'].fillna("").astype(str)

open_tickets = df[~df['Is_Solved']].copy()

# Let's filter specifically for Miguel Ochoa if any, or just all.
# If he said "para mi", he might mean assigned to him.
# Let's print out the open tickets assigned to MIGUEL OCHOA, and total open tickets.

miguel_open = open_tickets[open_tickets['Responsable'].str.contains("MIGUEL OCHOA", na=False)].copy()

print(f"Total open tickets: {len(open_tickets)}")
print(f"Open tickets for Miguel Ochoa: {len(miguel_open)}")

# Let's export Miguel's open tickets to a markdown file
miguel_open = miguel_open.sort_values(by='Transit_Days', ascending=False)

md_content = "# Tickets Abiertos - Miguel Ochoa\n\n"
for _, row in miguel_open.iterrows():
    md_content += f"## Ticket {row['ID']} - {row['Transit_Days']} días abiertos\n"
    md_content += f"- **Alta:** {row['Fecha alta']}\n"
    md_content += f"- **Solicitante:** {row['Solicitante']} ({row['Departamento']})\n"
    md_content += f"- **Estado:** {row['Estado']}\n"
    md_content += f"**Solicitud:**\n{row['Solicitud']}\n\n"
    md_content += "---\n\n"

with open("miguel_open_tickets.md", "w", encoding="utf-8") as f:
    f.write(md_content)

# Also let's just generate a summary of ALL open tickets just in case he meant all of them for him to review.
all_open = open_tickets.sort_values(by='Transit_Days', ascending=False)
md_all = "# Todos los Tickets Abiertos a Nivel Detalle\n\n"
for _, row in all_open.iterrows():
    md_all += f"## Ticket {row['ID']} - {row['Responsable']} ({row['Transit_Days']} días)\n"
    md_all += f"- **Alta:** {row['Fecha alta']}\n"
    md_all += f"- **Solicitante:** {row['Solicitante']} ({row['Departamento']})\n"
    md_all += f"- **Estado:** {row['Estado']}\n"
    md_all += f"**Solicitud:**\n{row['Solicitud']}\n\n"
    md_all += "---\n\n"

with open("all_open_tickets.md", "w", encoding="utf-8") as f:
    f.write(md_all)

print("Exported to miguel_open_tickets.md and all_open_tickets.md")
