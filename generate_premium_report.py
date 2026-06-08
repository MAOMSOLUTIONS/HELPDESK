import pandas as pd
import numpy as np
import os
import webbrowser
from datetime import datetime

# Paths
INPUT_DIR = r"c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk"
TODAY_STR = datetime.now().strftime("%d_%m_%Y")
YEST_STR = (datetime.now() - pd.Timedelta(days=1)).strftime("%d_%m_%Y")
INPUT_FILE_TODAY = os.path.join(INPUT_DIR, f"ReporteHelpdesk{TODAY_STR}.xlsx")
INPUT_FILE_YESTERDAY = os.path.join(INPUT_DIR, f"ReporteHelpdesk{YEST_STR}.xlsx")

ICO_OMEGA = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1a73e8" stroke-width="3"><path d="M3 12h3l3-9 6 18 3-9h3"></path></svg>'
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
    if subset is None or len(subset) == 0: return {'TOTAL':0,'CERRADOS':0,'SLA_OK':0,'SLA_FAIL':0,'OPEN_OK':0,'OPEN_FAIL':0,'KPI':0,'OPEN_TOTAL':0}
    total = len(subset); solved = subset['Is_Solved'].sum(); c_time = subset['SLA_Compliance'].sum()
    open_df = subset[~subset['Is_Solved']]; a_time = (open_df['Transit_Hours'] <= 72).sum(); a_late = (open_df['Transit_Hours'] > 72).sum()
    kpi = (c_time / total * 100) if total > 0 else 0; open_total = total - solved
    return {'TOTAL': total, 'CERRADOS': solved, 'SLA_OK': c_time, 'SLA_FAIL': solved - c_time, 'OPEN_OK': a_time, 'OPEN_FAIL': a_late, 'KPI': kpi, 'OPEN_TOTAL': open_total}

def process_df(path):
    df = pd.read_excel(path, skiprows=4)
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
    df['Transit_Hours'] = np.where(df['Is_Solved'], (df['dt_solucion'] - df['dt_alta']).dt.total_seconds() / 3600, (ref_date - df['dt_alta']).dt.total_seconds() / 3600)
    df['Transit_Days'] = (df['Transit_Hours'] / 24).fillna(0).round(1)
    df['SLA_Compliance'] = np.where(df['Is_Solved'], df['Transit_Hours'] <= 72, False)
    df['Responsable'] = df['Responsable'].fillna("SIN ASIGNAR").astype(str).str.strip().str.upper()
    df['Departamento'] = df['Departamento'].fillna("GENERAL").astype(str).str.strip().str.upper()
    df['Solicitante'] = df['Solicitante'].fillna("N/A").astype(str).str.strip().str.upper()
    df['SLA_Status'] = np.where(df['Transit_Hours'] <= 72, "DENTRO", "FUERA")
    df['Mes_Nombre'] = df['Mes alta'].map(MONTH_MAP).fillna("N/A").str.upper()
    df['Estado'] = df['Estado'].fillna("PENDIENTE").astype(str).str.upper()
    df['Observaciones'] = df['Observaciones solucion'].fillna("").astype(str)
    df['Solicitud_Full'] = df['Solicitud'].fillna("").astype(str)
    df['Criticidad'] = "DENTRO"
    df.loc[(~df['Is_Solved']) & (df['Transit_Days'] > 3), 'Criticidad'] = "MODERADO"
    df.loc[(~df['Is_Solved']) & (df['Transit_Days'] > 5), 'Criticidad'] = "CRÍTICO"
    return df

def create_single_report(df_t, df_y, flavor, output_filename):
    st_t = get_stats_dict(df_t); st_y = get_stats_dict(df_y) if df_y is not None else None
    cur_m = df_t['Mes alta'].max(); cur_m_name = MONTH_MAP.get(cur_m, "N/A").upper()
    m_st_t = get_stats_dict(df_t[df_t['Mes alta'] == cur_m])
    m_st_y = get_stats_dict(df_y[df_y['Mes alta'] == cur_m]) if df_y is not None else None

    depts = sorted(df_t['Departamento'].unique().astype(str).tolist())
    techs = sorted(df_t['Responsable'].unique().astype(str).tolist())
    users = sorted(df_t['Solicitante'].unique().astype(str).tolist())
    months = sorted(df_t['Mes_Nombre'].unique().astype(str).tolist())
    
    m_df = pd.DataFrame([{'AÑO': a, 'm_num': m, 'MES': n, **get_stats_dict(g)} for (a,m,n),g in df_t.groupby(['Año','Mes alta','Mes_Nombre'], observed=True)]).sort_values(by=['AÑO','m_num'], ascending=False)
    u_df = pd.DataFrame([{'USUARIO': u, **get_stats_dict(g)} for u,g in df_t.groupby('Solicitante')]).sort_values(by='TOTAL', ascending=False).head(20)
    t_df = pd.DataFrame([{'RESPONSABLE': t, **get_stats_dict(g)} for t,g in df_t.groupby('Responsable')]).sort_values(by='TOTAL', ascending=False)
    unassigned = df_t[(~df_t['Is_Solved']) & (df_t['Responsable'] == "SIN ASIGNAR")].sort_values(by='Transit_Days', ascending=False).head(15)

    base_url = "file:///c:/Users/DIRECCION-TI/OneDrive%20-%20CINLAT%20LOGISTICS%20S.A.%20de%20C.V/Miguel%20Ochoa/2025-A/MVP/HelpDesk/"
    file_url = f"{base_url}{output_filename}#portal"
    title = "SOPORTE DE HELP DESK IT" if flavor == 'IT' else "REPORTE EJECUTIVO DE HELP DESK"
    
    def get_delta_html(today_val, yesterday_val, inverse=False):
        if yesterday_val is None: return ""
        delta = today_val - yesterday_val
        if delta == 0: return '<span style="font-size:10px; color:#64748b; margin-left:5px;">=</span>'
        color = "#ef4444" if (delta > 0 if inverse else delta < 0) else "#22c55e"
        arrow = "↑" if delta > 0 else "↓"
        return f'<span style="font-size:11px; color:{color}; font-weight:bold; margin-left:5px;">{arrow}{abs(int(delta))}</span>'

    def kpi_email_v(s, s_y, lbl, color="#3b82f6"):
        return f"""<div style="margin-bottom:20px;">
            <div style="font-size:10px; font-weight:900; color:{color}; border-left:4px solid {color}; padding-left:10px; margin-bottom:10px; text-transform:uppercase;">{lbl}</div>
            <div style="display:flex; gap:10px;">
                <div style="flex:1; background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:15px; text-align:center;">
                    <div style="font-size:20px; font-weight:900; color:{color};">{int(s['TOTAL'])}{get_delta_html(s['TOTAL'], s_y['TOTAL'] if s_y else None)}</div><div style="font-size:8px; color:#64748b;">TOTAL</div>
                </div>
                <div style="flex:1; background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:15px; text-align:center;">
                    <div style="font-size:20px; font-weight:900; color:{color};">{int(s['CERRADOS'])}{get_delta_html(s['CERRADOS'], s_y['CERRADOS'] if s_y else None)}</div><div style="font-size:8px; color:#64748b;">SOLUCIONADO</div>
                </div>
                <div style="flex:1; background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:15px; text-align:center;">
                    <div style="font-size:20px; font-weight:900; color:#22c55e;">{int(s['SLA_OK'])}{get_delta_html(s['SLA_OK'], s_y['SLA_OK'] if s_y else None)}</div><div style="font-size:8px; color:#64748b;">EN TIEMPO</div>
                </div>
                <div style="flex:1; background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:15px; text-align:center;">
                    <div style="font-size:20px; font-weight:900; color:#ef4444;">{int(s['SLA_FAIL'])}{get_delta_html(s['SLA_FAIL'], s_y['SLA_FAIL'] if s_y else None, inverse=True)}</div><div style="font-size:8px; color:#64748b;">FUERA DE TIEMPO</div>
                </div>
                <div style="flex:1; background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:15px; text-align:center;">
                    <div style="font-size:20px; font-weight:900; color:#64748b;">{int(s['OPEN_TOTAL'])}{get_delta_html(s['OPEN_TOTAL'], s_y['OPEN_TOTAL'] if s_y else None, inverse=True)}</div><div style="font-size:8px; color:#64748b;">PENDIENTE</div>
                </div>
                <div style="flex:1; background:#0f172a; border:1px solid #334155; border-radius:12px; padding:15px; text-align:center;">
                    <div style="font-size:20px; font-weight:900; color:{color};">{s['KPI']:.1f}%</div><div style="font-size:8px; color:#64748b;">KPI</div>
                </div>
            </div>
        </div>"""

    def rows_classic(r, c1, c2=None):
        td2 = f"<td><b>{c2}</b></td>" if c2 else ""
        return f"""<tr><td><b>{c1}</b></td>{td2}<td>{int(r['TOTAL'])}</td><td>{int(r['CERRADOS'])}</td><td>{int(r['SLA_OK'])}</td><td>{int(r['SLA_FAIL'])}</td><td style="color:#22c55e; font-weight:bold;">{int(r['OPEN_OK'])}</td><td style="color:#ef4444; font-weight:bold;">{int(r['OPEN_FAIL'])}</td><td style="font-weight:900; color:#3b82f6;">{r['KPI']:.1f}%</td></tr>"""

    m_rows = "".join([rows_classic(r, r['AÑO'], r['MES']) for _,r in m_df.iterrows()])
    u_rows = "".join([rows_classic(r, r['USUARIO']) for _,r in u_df.iterrows()])
    t_rows = "".join([rows_classic(r, r['RESPONSABLE']) for _,r in t_df.iterrows()])
    a_rows = "".join([f"<tr><td><b>{r['ID']}</b></td><td>{r['Fecha alta']}</td><td style='color:#ef4444;'>{r['Transit_Days']}D</td><td>{r['Solicitante']}</td><td>{r['Estado']}</td></tr>" for _, r in unassigned.iterrows()])
    
    it_v = "" if flavor == 'IT' else "display:none;"
    i_rows = "".join([f'<tr class="dr" onclick="toggleDetail(\'{r["ID"]}\')" data-m="{r["Mes_Nombre"]}" data-d="{r["Departamento"]}" data-t="{r["Responsable"]}" data-u="{r["Solicitante"]}" data-s="{r["SLA_Status"]}" data-c="{r["Criticidad"]}" data-days="{r["Transit_Days"]}"><td><b>{r["ID"]}</b></td><td>{r["Fecha alta"]}</td><td style="{it_v}">{r["Responsable"]}</td><td>{r["Solicitante"]}</td><td>{r["Departamento"]}</td><td><span class="tag" style="background:#f8fafc; border:1px solid #e2e8f0;">{r["Estado"]}</span></td><td>{r["SLA_Status"]}</td></tr><tr id="det_{r["ID"]}" class="dr-detail"><td colspan="8"><div class="detail-grid"><div class="detail-box"><span class="detail-lbl">📝 Descripción</span><div class="detail-txt">{r["Solicitud_Full"]}</div></div><div class="detail-box"><span class="detail-lbl">🛠️ Notas</span><div class="detail-txt">{r["Observaciones"] if r["Observaciones"] else "Sin notas."}</div></div></div></td></tr>' for _, r in df_t.iterrows()])

    # Template with double braces escaped manually or just use string replace
    template = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>[[TITLE]]</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
        body { font-family: 'Inter', sans-serif; background: #f1f5f9; margin: 0; padding: 0; color: #1e293b; overflow-x: hidden; }
        .nav-bar { background: #fff; padding: 12px; display: flex; justify-content: center; gap: 15px; border-bottom: 1px solid #e2e8f0; position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .nav-tab { padding: 10px 25px; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; color: #64748b; font-weight: 900; font-size: 13px; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }
        .nav-tab.active { background: #1a73e8; color: #fff; border-color: #1a73e8; box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3); }
        .nav-tab:hover:not(.active) { background: #f8fafc; border-color: #cbd5e1; }
        .view-section { padding: 30px; animation: fadeIn 0.4s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .box { background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); overflow: hidden; margin-bottom: 30px; }
        .hdr { background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); padding: 60px 35px; text-align: center; border-bottom: 1px solid #e2e8f0; color: #0f172a; }
        .hdr h1 { margin: 0 0 10px 0; font-size: 32px; font-weight: 900; letter-spacing: -0.05em; }
        .pill-link { display: inline-block; background: #3b82f6; color: #fff; padding: 15px 40px; border-radius: 50px; font-weight: 900; font-size: 14px; text-decoration: none; margin-top: 20px; transition: transform 0.2s; }
        .pill-link:hover { transform: scale(1.05); }
        .i-kpi-row { display: flex; gap: 20px; margin-bottom: 30px; }
        .i-card { flex: 1; background: #fff; padding: 25px; border: 1.5px solid #e2e8f0; border-radius: 20px; border-left: 5px solid #3b82f6; }
        .i-val { font-size: 34px; font-weight: 900; color: #1e293b; display: block; }
        .i-lab { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; }
        .dr { cursor: pointer; transition: background 0.2s; }
        .dr:hover { background: rgba(59, 130, 246, 0.05); }
        .dr-detail { display: none; background: #f8fafc; }
        .dr-detail td { padding: 20px 40px !important; border-bottom: 2px solid #3b82f6 !important; }
        .detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .detail-box { background: #fff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
        .detail-lbl { font-size: 9px; font-weight: 800; color: #3b82f6; text-transform: uppercase; margin-bottom: 8px; display: block; }
        .detail-txt { font-size: 13px; color: #334155; line-height: 1.6; white-space: pre-wrap; }
        .ribbon { background: #fff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 15px 25px; display: flex; align-items: center; gap: 12px; margin-bottom: 25px; flex-wrap: wrap; }
        .inp, .sel { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; color: #1e293b; padding: 10px 15px; font-size: 12px; font-weight: 600; }
        .i-tbl { width: 100%; border-collapse: collapse; font-size: 11px; }
        .i-tbl th { background: #f8fafc; color: #64748b; padding: 18px 15px; text-align: left; text-transform: uppercase; font-size: 10px; font-weight: 800; border-bottom: 1px solid #e2e8f0; }
        .i-tbl td { padding: 15px; border-bottom: 1px solid #e2e8f0; color: #334155; }
        .tag { padding: 4px 10px; border-radius: 6px; font-size: 9px; font-weight: 900; text-transform: uppercase; }
        .classic-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 11px; margin-bottom: 20px; }
        .classic-table th { padding: 12px; border-bottom: 2px solid #e2e8f0; color: #64748b; background: #f8fafc; }
        .classic-table td { padding: 10px; border-bottom: 1px solid #f1f5f9; }
        .sh { color: #3b82f6; font-size: 12px; font-weight: 900; padding: 15px 0 10px; border-bottom: 1px solid #e2e8f0; margin-bottom: 15px; text-transform: uppercase; }
        .act-btn { padding: 8px 18px; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; font-size: 12px; font-weight: 700; cursor: pointer; }
    </style>
    </head><body>
        <div class="nav-bar">
            <button id="tab_e" onclick="showE()" class="nav-tab active">📊 RESUMEN EJECUTIVO</button>
            <button id="tab_p" onclick="showP()" class="nav-tab">🔍 FILTROS INTERACTIVOS</button>
        </div>
        <div id="v_email" class="view-section" style="display: block;">
            <div class="box">
                <div class="hdr">
                    <h1>[[TITLE]]</h1>
                    <div style="color: #94a3b8; font-size: 12px; margin-bottom:20px;">ACTUALIZADO AL: [[DATE_STR]]</div>
                    <a href="[[FILE_URL]]" class="pill-link">🚀 ABRIR VISTA INTERACTIVA</a>
                </div>
                <div style="padding: 40px;">
                    [[KPI_MONTH]]
                    [[KPI_YEAR]]
                    <div class="sh">1. RESUMEN MENSUAL</div><table class="classic-table"><thead><tr><th>AÑO</th><th>MES</th><th>TOTAL</th><th>SOLUCIONADO</th><th>EN TIEMPO</th><th>FUERA TIEMPO</th><th>PENDIENTE OK</th><th>PENDIENTE BAD</th><th>KPI</th></tr></thead><tbody>[[M_ROWS]]</tbody></table>
                    <div class="sh">2. TOP 20 SOLICITANTES</div><table class="classic-table"><thead><tr><th>USUARIO</th><th>TOTAL</th><th>SOLUCIONADO</th><th>EN TIEMPO</th><th>FUERA TIEMPO</th><th>PENDIENTE OK</th><th>PENDIENTE BAD</th><th>KPI</th></tr></thead><tbody>[[U_ROWS]]</tbody></table>
                    [[T_SECTION]]
                    <div class="sh">BACKLOG CRÍTICO (>3 DÍAS)</div><table class="classic-table"><thead><tr><th>ID</th><th>ALTA</th><th>HIST</th><th>SOLICITANTE</th><th>ESTADO</th></tr></thead><tbody>[[A_ROWS]]</tbody></table>
                </div>
            </div>
        </div>
        <div id="v_portal" class="view-section" style="display: none;">
            <div style="display:flex; justify-content:space-between; margin-bottom:30px; align-items:center;">
                <div style="display:flex; align-items:center; gap:15px;">[[ICO]] <span style="font-size:22px; font-weight:900;">[[FLAVOR]] <span style="color:#3b82f6;">CONTROL</span></span></div>
                <div style="display:flex; gap:10px;"><button class="act-btn" onclick="reset()">🔄 LIMPIAR</button><button class="act-btn" onclick="exp()">📥 EXCEL/CSV</button></div>
            </div>
            <div class="i-kpi-row">
                <div class="i-card"><span class="i-lab">Tickets Filtrados</span><span class="i-val" id="k_t">[[TOTAL_T]]</span></div>
                <div class="i-card"><span class="i-lab">Días Transito Promedio</span><span class="i-val" id="k_p">0.0</span></div>
            </div>
            <div class="ribbon">
                <input type="text" id="s_" class="inp" onkeyup="f()" style="width:250px;" placeholder="🔍 Buscar ticket o usuario...">
                <select id="m_" class="sel" onchange="f()"><option value="">📅 MES</option>[[MONTH_OPTS]]</select>
                <select id="d_" class="sel" onchange="f()"><option value="">🏢 DEPARTAMENTO</option>[[DEPT_OPTS]]</select>
            </div>
            <div class="i-tbl-cont">
                <table class="i-tbl" id="m_t">
                    <thead><tr><th onclick="sortT(0)">ID ⇅</th><th onclick="sortT(1)">ALTA ⇅</th><th style="[[IT_STYLE]]">TECNICO</th><th>USUARIO</th><th>DPTO</th><th>ESTADO</th><th>SLA</th></tr></thead>
                    <tbody id="tb_">[[I_ROWS]]</tbody>
                </table>
            </div>
        </div>
        <script>
            window.onload = function() { if(window.location.hash === "#portal") showP(); }
            function showP() { 
                document.getElementById("v_email").style.display="none"; 
                document.getElementById("v_portal").style.display="block"; 
                document.getElementById("tab_p").classList.add("active");
                document.getElementById("tab_e").classList.remove("active");
                f(); 
            }
            function showE() { 
                document.getElementById("v_portal").style.display="none"; 
                document.getElementById("v_email").style.display="block"; 
                document.getElementById("tab_e").classList.add("active");
                document.getElementById("tab_p").classList.remove("active");
            }
            function f() {
                const q=document.getElementById("s_").value.toUpperCase(), 
                      m=document.getElementById("m_").value, 
                      d=document.getElementById("d_").value;
                let c=0, sumD=0;
                document.querySelectorAll("tr.dr").forEach(r => {
                    const id = r.cells[0].innerText;
                    const detailRow = document.getElementById("det_" + id);
                    const fullText = (r.innerText + (detailRow ? detailRow.innerText : "")).toUpperCase();
                    const matchQ = q === "" || fullText.includes(q);
                    const matchM = m === "" || r.getAttribute("data-m") === m;
                    const matchD = d === "" || r.getAttribute("data-d") === d;
                    
                    if (matchQ && matchM && matchD) {
                        r.style.display = ""; c++; sumD += parseFloat(r.getAttribute("data-days")||0);
                    } else { 
                        r.style.display = "none"; 
                        if(detailRow) detailRow.style.display = "none";
                    }
                });
                document.getElementById("k_t").innerText = c; 
                document.getElementById("k_p").innerText = c > 0 ? (sumD/c).toFixed(1) : "0.0";
            }
            function toggleDetail(id) {
                const el = document.getElementById("det_" + id);
                const isVisible = el.style.display === "table-row";
                document.querySelectorAll(".dr-detail").forEach(d => d.style.display = "none");
                el.style.display = isVisible ? "none" : "table-row";
            }
            function reset() { document.querySelectorAll(".inp, .sel").forEach(i => i.value = ""); f(); }
            function sortT(n) {
                const t = document.getElementById("m_t"), b = t.tBodies[0], rows = Array.from(b.rows).filter(r => r.classList.contains("dr"));
                const dir = t.getAttribute("data-sort") === "asc" ? -1 : 1;
                rows.sort((a,b) => {
                    const v1 = a.cells[n].innerText, v2 = b.cells[n].innerText;
                    return isNaN(v1) || isNaN(v2) ? v1.localeCompare(v2) * dir : (v1 - v2) * dir;
                }); 
                rows.forEach(r => {
                    b.appendChild(r);
                    const det = document.getElementById("det_" + r.cells[0].innerText);
                    if(det) b.appendChild(det);
                }); 
                t.setAttribute("data-sort", dir === 1 ? "asc" : "desc");
            }
            function exp() {
                let csv = "ID,ALTA,TECNICO,USUARIO,DPTO,ESTADO,SLA\\n";
                document.querySelectorAll("tr.dr").forEach(r => {
                    if(r.style.display !== "none") {
                        let row = []; r.querySelectorAll("td").forEach(c => row.push('"' + c.innerText.trim() + '"'));
                        csv += row.join(",") + "\\n";
                    }
                });
                const b = new Blob([csv], { type: 'text/csv;charset=utf-8;' }), u = URL.createObjectURL(b), l = document.createElement("a");
                l.href = u; l.download = "HelpDesk_Report.csv"; l.click();
            }
        </script>
    </body></html>"""

    html = template.replace("[[TITLE]]", title)
    html = html.replace("[[DATE_STR]]", f"{datetime.now().day} DE {MONTH_MAP[datetime.now().month].upper()} DE {datetime.now().year}")
    html = html.replace("[[FILE_URL]]", file_url)
    html = html.replace("[[KPI_MONTH]]", kpi_email_v(m_st_t, m_st_y, f"INDICADORES DEL MES: {cur_m_name}", "#f59e0b"))
    html = html.replace("[[KPI_YEAR]]", kpi_email_v(st_t, st_y, f"RESUMEN ACUMULADO AÑO {datetime.now().year}", "#94a3b8"))
    html = html.replace("[[M_ROWS]]", m_rows)
    html = html.replace("[[U_ROWS]]", u_rows)
    html = html.replace("[[A_ROWS]]", a_rows)
    html = html.replace("[[T_SECTION]]", f"<div class='sh'>3. EVALUACIÓN DE TÉCNICOS</div><table class='classic-table'><thead><tr><th>RESPONSABLE</th><th>TOTAL</th><th>SOL</th><th>OK</th><th>BAD</th><th>O-OK</th><th>O-BAD</th><th>KPI</th></tr></thead><tbody>{t_rows}</tbody></table>" if flavor=='IT' else "")
    html = html.replace("[[ICO]]", ICO_OMEGA)
    html = html.replace("[[FLAVOR]]", "IT" if flavor=='IT' else "EJECUTIVO")
    html = html.replace("[[TOTAL_T]]", str(st_t['TOTAL']))
    html = html.replace("[[MONTH_OPTS]]", "".join([f'<option value="{x}">{x}</option>' for x in months]))
    html = html.replace("[[DEPT_OPTS]]", "".join([f'<option value="{x}">{x}</option>' for x in depts]))
    html = html.replace("[[IT_STYLE]]", it_v)
    html = html.replace("[[I_ROWS]]", i_rows)
    
    full_out_path = os.path.join(INPUT_DIR, output_filename)
    with open(full_out_path, "w", encoding="utf-8") as f: f.write(html)
    return full_out_path

def generate_v48(silent=False):
    if not os.path.exists(INPUT_FILE_TODAY):
        return f"ERROR: Archivo de entrada no encontrado: {INPUT_FILE_TODAY}. Asegúrate de ejecutar el componente de descarga primero."
    
    df_t = process_df(INPUT_FILE_TODAY); df_y = None
    if os.path.exists(INPUT_FILE_YESTERDAY):
        try: df_y = process_df(INPUT_FILE_YESTERDAY)
        except: df_y = None
    p_it = create_single_report(df_t, df_y, 'IT', 'premium_report_it.html')
    p_biz = create_single_report(df_t, df_y, 'NEGOCIO', 'premium_report_negocio.html')
    
    if not silent:
        # Auto-open IT for Miguel
        path_norm = p_it.replace("\\", "/")
        webbrowser.open(f"file:///{path_norm}")
    
    return f"GENERACIÓN v48 EXITOSA actualizados a {datetime.now().strftime('%d/%m/%Y')}."

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generación de reportes de HelpDesk.")
    parser.add_argument("--silent", action="store_true", help="No abrir el navegador al finalizar.")
    args = parser.parse_args()
    print(generate_v48(silent=args.silent))
