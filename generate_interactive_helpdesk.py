import pandas as pd
import numpy as np
import os
from datetime import datetime

# Paths
INPUT_FILE_TODAY = r"c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\ReporteHelpdesk14_04_2026.xlsx"
INPUT_FILE_YESTERDAY = r"c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\ReporteHelpdesk13_04_2026.xlsx"

# Icons (Overdrive Style)
ICO_SEARCH = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>'
ICO_OMEGA = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="3"><path d="M3 12h3l3-9 6 18 3-9h3"></path></svg>'

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

def get_stats_dict(subset):
    if subset is None or len(subset) == 0: return {'TOTAL':0, 'CERRADOS':0, 'SLA_OK':0, 'SLA_FAIL':0, 'OPEN_OK':0, 'OPEN_FAIL':0, 'KPI':0, 'OPEN_TOTAL':0}
    total = len(subset); solved = subset['Is_Solved'].sum(); c_time = subset['SLA_Compliance'].sum()
    open_df = subset[~subset['Is_Solved']]
    a_time = (open_df['Transit_Hours'] <= 72).sum(); a_late = (open_df['Transit_Hours'] > 72).sum()
    kpi = (c_time / total * 100) if total > 0 else 0; open_total = total - solved
    return {'TOTAL': total, 'CERRADOS': solved, 'SLA_OK': c_time, 'SLA_FAIL': solved - c_time, 'OPEN_OK': a_time, 'OPEN_FAIL': a_late, 'KPI': kpi, 'OPEN_TOTAL': open_total}

def get_delta_html(today_val, yesterday_val, inverse=False):
    if yesterday_val is None: return ""
    delta = today_val - yesterday_val
    if delta == 0: return '<span style="font-size:10px; color:#64748b; margin-left:5px;">=</span>'
    color = "#ef4444" if (delta > 0 if inverse else delta < 0) else "#22c55e"
    arrow = "↑" if delta > 0 else "↓"
    return f'<span style="font-size:10px; color:{color}; font-weight:bold; margin-left:5px;">{arrow}{abs(int(delta))}</span>'

def process_df(path):
    df = pd.read_excel(path, skiprows=4)
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        if "o" in c.lower() and "alta" in c.lower() and "ID" not in c: df.rename(columns={c: "Año"}, inplace=True)
        if "mes" in c.lower() and "alta" in c.lower(): df.rename(columns={c: "Mes alta"}, inplace=True)
    df['dt_alta'] = df['Fecha alta'].apply(parse_spanish_date)
    df['dt_solucion'] = df['Fecha solucion'].apply(parse_spanish_date)
    df['Is_Solved'] = df['dt_solucion'].notnull()
    ref_date = datetime(2026, 4, 14, 10, 0)
    df['Transit_Hours'] = np.where(df['Is_Solved'], (df['dt_solucion'] - df['dt_alta']).dt.total_seconds() / 3600, (ref_date - df['dt_alta']).dt.total_seconds() / 3600)
    df['SLA_Compliance'] = np.where(df['Is_Solved'], df['Transit_Hours'] <= 72, False)
    df['Responsable'] = df['Responsable'].fillna("SIN ASIGNAR").astype(str).str.strip().str.upper()
    df['Departamento'] = df['Departamento'].fillna("GENERAL").astype(str).str.strip().str.upper()
    df['Solicitante'] = df['Solicitante'].fillna("N/A").astype(str).str.strip().str.upper()
    df['SLA_Status'] = np.where(df['Transit_Hours'] <= 72, "DENTRO", "FUERA")
    df['Mes_Nombre'] = df['Mes alta'].map(MONTH_MAP).fillna("N/A").str.upper()
    return df

def generate_interactive_portal():
    if not os.path.exists(INPUT_FILE_TODAY): return "Error: Archivo hoy no encontrado."
    df_t = process_df(INPUT_FILE_TODAY)
    df_y = None
    if os.path.exists(INPUT_FILE_YESTERDAY):
        try: df_y = process_df(INPUT_FILE_YESTERDAY)
        except: df_y = None

    st_t = get_stats_dict(df_t); st_y = get_stats_dict(df_y) if df_y is not None else None
    curr_m = df_t['Mes alta'].max(); curr_m_name = MONTH_MAP.get(curr_m, "N/A").upper()

    depts = sorted(df_t['Departamento'].unique().astype(str).tolist())
    techs = sorted(df_t['Responsable'].unique().astype(str).tolist())
    states = sorted(df_t['Estado'].unique().astype(str).tolist())

    styles = """<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap'); :root { --bg-body: #020617; --bg-card: #0f172a; --text-main: #f1f5f9; --text-sub: #94a3b8; --border-clr: #1e293b; --accent: #3b82f6; } body { font-family: 'Inter', sans-serif; background: var(--bg-body); color: var(--text-main); margin: 0; padding: 0; letter-spacing: -0.015em; } .executive-container { width: 98%; margin: 25px auto; padding: 0 20px; } .hdr-bar { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(12px); border-bottom: 1.5px solid var(--border-clr); padding: 15px 45px; position: sticky; top: 0; z-index: 1000; display: flex; align-items: center; justify-content: space-between; } .kpi-row { display: flex; gap: 15px; margin: 25px 0; } .kpi-card { flex: 1; min-width: 0; background: var(--bg-card); border-radius: 20px; padding: 25px; border: 1.5px solid var(--border-clr); } .kpi-val { font-size: 34px; font-weight: 800; display: block; margin-top: 10px; } .kpi-lab { font-size: 10px; font-weight: 700; text-transform: uppercase; color: var(--text-sub); } .command-ribbon { background: var(--bg-card); border: 1.5px solid var(--border-clr); border-radius: 16px; padding: 15px 25px; display: flex; align-items: center; gap: 12px; margin-bottom: 25px; } .search-input { background: #1e293b; border: 1px solid var(--border-clr); border-radius: 10px; color: #fff; padding: 10px 15px 10px 40px; font-size: 12px; width: 300px; } .select-pro { background: #1e293b; border: 1px solid var(--border-clr); border-radius: 10px; color: #fff; padding: 10px; font-size: 11px; min-width: 140px; } table { width: 100%; border-collapse: separate; border-spacing: 0; background: var(--bg-card); border-radius: 20px; overflow: hidden; font-size: 11px; } th { background: #1e293b; padding: 18px 15px; color: var(--text-sub); text-transform: uppercase; font-size: 10px; font-weight: 800; text-align: left; } td { padding: 12px 15px; border-bottom: 1px solid var(--border-clr); } .status-pill { padding: 5px 10px; border-radius: 8px; font-size: 9px; font-weight: 800; } .sla-dentro { background: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.2); } .sla-fuera { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }</style>"""

    rows_html = "".join([f'<tr class="data-row" data-dept="{r["Departamento"]}" data-tech="{r["Responsable"]}" data-sla="{r["SLA_Status"]}" data-state="{r["Estado"]}"><td><b style="color:#3b82f6;">{r["ID"]}</b></td><td>{r["Fecha alta"]}</td><td>{r["Mes_Nombre"]}</td><td style="font-weight:700;">{r["Departamento"]}</td><td style="color:#94a3b8;">{r["Solicitante"]}</td><td>{r["Responsable"]}</td><td><span class="status-pill {"sla-dentro" if r["SLA_Status"]=="DENTRO" else "sla-fuera"}">{r["SLA_Status"]} SLA</span></td><td><b>{r["Estado"]}</b></td><td style="font-size:10px; color:#94a3b8;">{str(r["Solicitud"])[:80]}...</td></tr>' for _,r in df_t.iterrows()])

    def k_card(val, lab, d_html, border="#3b82f6"): return f'<div class="kpi-card" style="border-left:5px solid {border};"><span class="kpi-lab">{lab}</span><span class="kpi-val">{val}{d_html}</span></div>'

    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>HelpDesk PowerPortal</title>{styles}</head><body><div class="hdr-bar"><div style="display:flex; align-items:center; gap:15px;">{ICO_OMEGA} <span style="font-size:18px; font-weight:900;">HELPDESK <span style="color:#3b82f6;">POWER PORTAL</span></span></div><div id="mCount" style="background:#3b82f6; color:#fff; padding:10px 20px; border-radius:10px; font-size:11px; font-weight:800;">{len(df_t)} TICKETS</div></div><div class="executive-container"><div class="kpi-row">{k_card(st_t['TOTAL'], "Total 2026", get_delta_html(st_t['TOTAL'], st_y['TOTAL'] if st_y else None))}{k_card(st_t['CERRADOS'], "Cerrados", get_delta_html(st_t['CERRADOS'], st_y['CERRADOS'] if st_y else None), "#22c55e")}{k_card(st_t['OPEN_TOTAL'], "Abiertos", get_delta_html(st_t['OPEN_TOTAL'], st_y['OPEN_TOTAL'] if st_y else None, True), "#f97316")}{k_card(st_t['OPEN_FAIL'], "Fuera SLA", get_delta_html(st_t['OPEN_FAIL'], st_y['OPEN_FAIL'] if st_y else None, True), "#ef4444")}{k_card(f"{st_t['KPI']:.1f}%", "Eficacia", "")}</div><div class="command-ribbon"><div style="position:relative;"><span style="position:absolute; left:15px; top:11px; color:#64748b;">{ICO_SEARCH}</span><input type="text" id="sBox" class="search-input" onkeyup="fT()" placeholder="Buscar solicitante o solicitud..."></div><select id="fD" class="select-pro" onchange="fT()"><option value="">🏢 DEPARTAMENTO</option>{"".join([f'<option value="{d}">{d}</option>' for d in depts])}</select><select id="fT" class="select-pro" onchange="fT()"><option value="">🛠️ TÉCNICO</option>{"".join([f'<option value="{t}">{t}</option>' for t in techs])}</select><select id="fS" class="select-pro" onchange="fT()"><option value="">🚥 ESTATUS</option>{"".join([f'<option value="{v}">{v}</option>' for v in states])}</select><select id="fA" class="select-pro" onchange="fT()"><option value="">⏱️ SLA</option><option value="DENTRO">DENTRO</option><option value="FUERA">FUERA</option></select></div><table><thead><tr><th>ID</th><th>FECHA ALTA</th><th>MES</th><th>DEPARTAMENTO</th><th>SOLICITANTE</th><th>TÉCNICO</th><th>SLA</th><th>ESTADO</th><th>DETALLE</th></tr></thead><tbody id="tB">{rows_html}</tbody></table><div style="text-align:center; padding:50px 0; font-size:11px; color:#475569;">IT COMMAND CENTER &bull; 2026</div></div><script>function fT(){{const q=document.getElementById("sBox").value.toUpperCase(), d=document.getElementById("fD").value.toUpperCase(), t=document.getElementById("fT").value.toUpperCase(), s=document.getElementById("fA").value.toUpperCase(), st=document.getElementById("fS").value.toUpperCase(); let c=0; document.querySelectorAll("tr.data-row").forEach(r=>{{const match=r.innerText.toUpperCase().indexOf(q)>-1&&(d==""||r.getAttribute("data-dept")==d)&&(t==""||r.getAttribute("data-tech")==t)&&(s==""||r.getAttribute("data-sla")==s)&&(st==""||r.getAttribute("data-state")==st); r.style.display=match?"":"none"; if(match)c++;}}); document.getElementById("mCount").innerText=c+" TICKETS";}}</script></body></html>"""
    out_path = r"c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\premium_report_full.html"
    with open(out_path, "w", encoding="utf-8") as f: f.write(html)
    return "HelpDesk PowerPortal v26 Interactivo Generado (Solo Miguel)."

if __name__ == "__main__":
    print(generate_interactive_portal())
