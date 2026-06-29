import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# Paths
INPUT_FILE = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Prioridades_IT_2026_15_06_2026.xlsx"

# ICONS (Lucide Style Inline SVGs - Fine Strokes)
ICO_SEARCH = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>'
ICO_PLUS = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>'
ICO_CHART = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>'
ICO_USER = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
ICO_OMEGA = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h3l3-9 6 18 3-9h3"></path></svg>'

def render_multiselect(id_attr, label_prefix, items_list):
    options_html = ""
    for item in items_list:
        item_escaped = str(item).replace('"', '&quot;')
        options_html += f"""
        <label class="dropdown-ms-item">
            <input type="checkbox" value="{item_escaped}" checked onchange="updateDropdownLabel(this.closest('.dropdown-ms')); filterTable();">
            <span>{item}</span>
        </label>
        """
    return f"""
    <div id="{id_attr}" class="dropdown-ms">
        <button class="dropdown-ms-btn" data-prefix="{label_prefix}">{label_prefix} (Todos)</button>
        <div class="dropdown-ms-content">
            <input type="text" class="dropdown-ms-search" placeholder="Buscar..." onkeyup="searchDropdown(this)">
            <div class="dropdown-ms-actions">
                <button class="dropdown-ms-action-btn" onclick="toggleAllDropdown(this, true)">Todos</button>
                <button class="dropdown-ms-action-btn" onclick="toggleAllDropdown(this, false)">Ninguno</button>
            </div>
            <div class="dropdown-ms-list">
                {options_html}
            </div>
        </div>
    </div>
    """

def generate_report():
    if not os.path.exists(INPUT_FILE): return f"Error: Archivo {INPUT_FILE} no encontrado."
    df = pd.read_excel(INPUT_FILE).fillna("")
    
    # Normalize column names to avoid encoding issues
    new_cols = {}
    for col in df.columns:
        col_str = str(col)
        if 't' in col_str and 'rmino' in col_str:
            new_cols[col] = 'Fecha_trmino'
        else:
            new_cols[col] = col_str
    df = df.rename(columns=new_cols)
    
    if 'Vista' not in df.columns:
        df['Vista'] = ""
    if 'Recursos' not in df.columns:
        df['Recursos'] = ""
    
    # DATA PREP
    def format_date_html(val):
        if val == "" or pd.isna(val): return ""
        if isinstance(val, (datetime, pd.Timestamp)): return val.strftime('%d/%m/%Y')
        val_str = str(val).strip()
        try:
            dt = pd.to_datetime(val_str)
            return dt.strftime('%d/%m/%Y')
        except:
            return val_str

    df['Fecha_Inicio_Display'] = df['Fecha inicio'].apply(format_date_html)
    df['Fecha_Termino_Display'] = df['Fecha_trmino'].apply(format_date_html)
    
    # LOGIC CLASSIFICATION BASED ON NEW STATUSES
    def categorize(row):
        id_val = str(row['ID']).upper().strip()
        status = str(row['Estatus']).strip().upper()
        
        is_completed = "LIBERADO" in status or "TERMINADO" in status or "VALIDACION" in status or "PRUEBAS" in status
        
        if is_completed:
            try:
                if pd.notna(row['Fecha_trmino']) and row['Fecha_trmino'] != "":
                    dt = pd.to_datetime(row['Fecha_trmino'], dayfirst=True)
                    now = datetime.now()
                    days_diff = (now - dt).days
                    
                    if days_diff >= 7:
                        weeks_ago = days_diff // 7
                        if weeks_ago == 1:
                            return 11, "Concluidos / Validación (Semana Pasada)"
                        elif weeks_ago == 2:
                            return 12, "Concluidos / Validación (Hace 2 Semanas)"
                        elif weeks_ago == 3:
                            return 13, "Concluidos / Validación (Hace 3 Semanas)"
                        else:
                            return 14, "Concluidos / Validación (Más de 1 Mes)"
            except:
                pass
                
            if id_val == 'T':
                return 15, "Histórico (Otros)"
            return 2, "Concluidos / En Validación (Reciente)"
        else:
            if "SIN_PRIORIDAD" in status or "SIN PRIORIDAD" in status:
                return 8, "Sin Prioridad"
            return 1, "Activo" # Current active

    df['Sort_Group'], df['Group_Name'] = zip(*df.apply(categorize, axis=1))

    # SORTING: Actives first, then This week finished, then Historical
    def natural_sort_key(s):
        import re
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    def clean_prior(val):
        v = str(val).upper().strip()
        digits = ''.join(filter(str.isdigit, v))
        return int(digits) if digits else 999

    df['Prior_Num'] = df['Filtro MAO'].apply(clean_prior)
    df = df.sort_values(by=['Sort_Group', 'Prior_Num'], ascending=[True, True])
    df['SEQ_IDX'] = range(1, len(df) + 1)

    if 'Area Desarrollo.1' not in df.columns:
        df['Area Desarrollo.1'] = ""

    # Helper to build lists containing "(Vacío)" for checklist options
    def get_clean_list(col_name, is_priority=False):
        raw_vals = df[col_name].unique()
        has_empty = False
        vals = []
        for x in raw_vals:
            s = str(x).strip()
            if s == "" or s.lower() == 'nan':
                has_empty = True
            else:
                vals.append(s)
        if is_priority:
            vals = sorted(vals, key=natural_sort_key)
        else:
            vals = sorted(vals)
        if has_empty:
            vals.append("(Vacío)")
        return vals

    # Lists for checklist filters
    id_list = get_clean_list('ID')
    vista_list = get_clean_list('Vista')
    clientes_list = get_clean_list('Cliente')
    estatus_list = get_clean_list('Estatus')
    prioridades_list = get_clean_list('Filtro MAO', is_priority=True)
    bloques_list = get_clean_list('Bloque')
    areas_list = get_clean_list('Area Desarrollo')
    dev_areas_list = get_clean_list('Area Desarrollo.1')
    itteam_list = get_clean_list('IT Team')
    grupos_list = sorted(list(set(str(x).strip() for x in df['Group_Name'].unique() if str(x).strip() != "" and str(x).lower() != 'nan')))

    # Chart Dataset: Count finished requirements by month
    concluidos = df[df['Group_Name'].str.startswith("Concluidos", na=False)]
    chart_data = concluidos['Group_Name'].value_counts().to_dict()

    # KPIs - New logic based on Filtro MAO and ID_PRIORIDAD
    total_rows = len(df)
    priorizados = len(df[df['Filtro MAO'].astype(str).str.strip().apply(lambda x: x != "" and x.lower() != "nan" and "sin_prioridad" not in x.lower())])
    completados = len(df[df['Estatus'].astype(str).str.contains('Liberado|Terminado|Pruebas', case=False, na=False, regex=True)])
    success_rate = round((completados / total_rows * 100), 1) if total_rows > 0 else 0
    sin_prioridad = total_rows - priorizados

    styles = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
        
        :root {{ 
            --table-fs: 13px; --bg-body: #f8fafc; --bg-card: #ffffff; --text-main: #0f172a; --text-sub: #64748b;
            --bg-ribbon: #ffffff; --border-clr: #e2e8f0; --accent: #2563eb; --omega: #1e293b;
        }}
        body.dark-mode {{ 
            --bg-body: #020617; --bg-card: #0f172a; --text-main: #f1f5f9; --text-sub: #94a3b8;
            --bg-ribbon: #1e293b; --border-clr: #1e293b; --omega: #f8fafc;
        }}

        body {{ font-family: 'Inter', -apple-system, sans-serif; background: var(--bg-body); margin: 0; padding: 0; color: var(--text-main); transition: background 0.3s; letter-spacing: -0.015em; -webkit-font-smoothing: antialiased; }}
        
        .top-nav {{ background: var(--omega); color: #fff; box-shadow: 0 4px 30px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 1000; }}
        
        .executive-container {{ width: 98%; margin: 25px auto; padding: 40px 20px; box-sizing: border-box; }}
        
        .kpi-row {{ display: flex; justify-content: space-between; gap: 20px; margin-bottom: 45px; flex-wrap: nowrap !important; }}
        .kpi-card {{ flex: 1; min-width: 0; background: var(--bg-card); border-radius: 20px; padding: 25px; border: 1px solid var(--border-clr); box-shadow: 0 10px 30px rgba(0,0,0,0.02); display: flex; align-items: center; justify-content: space-between; transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
        .kpi-card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 40px rgba(37,99,235,0.08); border-color: var(--accent); }}
        .kpi-val {{ font-size: 36px; font-weight: 800; letter-spacing: -1.5px; color: var(--text-main); line-height: 1; }}
        .kpi-lab {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-sub); display: block; margin-bottom: 8px; letter-spacing: 0.5px; }}
        
        .filter-ribbon {{ background: var(--bg-card); padding: 12px 20px; border-radius: 16px; margin-bottom: 30px; display: flex; align-items: center; gap: 15px; border: 1.5px solid var(--border-clr); box-shadow: 0 4px 15px rgba(0,0,0,0.03); flex-wrap: wrap; }}
        .search-group {{ position: relative; flex: 1; min-width: 250px; display: flex; align-items: center; }}
        .search-input {{ width: 100%; padding: 12px 15px 12px 45px; border-radius: 12px; border: 1px solid transparent; background: transparent; color: var(--text-main); font-size: 14px; outline: none; font-weight: 500; }}
        .search-input:focus {{ border-color: var(--accent); background: var(--bg-body); }}
        
        .select-pro {{ padding: 10px 35px 10px 15px; border-radius: 10px; border: 1px solid var(--border-clr); background: var(--bg-card); color: var(--text-main); font-weight: 600; font-size: 13px; cursor: pointer; outline: none; appearance: none; background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e"); background-repeat: no-repeat; background-position: right 12px center; background-size: 14px; transition: 0.2s; }}
        .select-pro:hover {{ border-color: var(--accent); }}
        
        table {{ width: 100%; border-collapse: separate; border-spacing: 0; font-size: var(--table-fs); border-radius: 20px; overflow: hidden; border: 1px solid var(--border-clr); background: var(--bg-card); }}
        th {{ background: var(--omega); color: #fff; padding: 22px 16px; text-align: left; text-transform: uppercase; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; position: sticky; top: 0; z-index: 100; }}
        td {{ padding: 16px; border-bottom: 1px solid var(--border-clr); vertical-align: middle; transition: background 0.2s; }}
        tr.row-item:hover td {{ background: rgba(37,99,235,0.05) !important; }}
        
        .status-pill {{ padding: 6px 14px; border-radius: 12px; font-weight: 800; font-size: 10px; text-transform: uppercase; display: inline-block; text-align: center; min-width: 110px; border: 1px solid rgba(0,0,0,0.05); letter-spacing: 0.3px; }}
        .status-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 12px; vertical-align: middle; }}
        .id-badge {{ background: var(--bg-body); padding: 4px 10px; border-radius: 6px; font-weight: 700; color: var(--accent); border: 1px solid var(--border-clr); }}
        
        .group-header {{ background: #f1f5f9; padding: 10px 20px; font-weight: 800; font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }}

        /* Multi-select Dropdown styling */
        .dropdown-ms {{
            position: relative;
            display: inline-block;
            min-width: 170px;
        }}
        .dropdown-ms-btn {{
            padding: 10px 35px 10px 15px;
            border-radius: 10px;
            border: 1px solid var(--border-clr);
            background: var(--bg-card);
            color: var(--text-main);
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            outline: none;
            text-align: left;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: block;
            width: 100%;
            box-sizing: border-box;
            position: relative;
        }}
        .dropdown-ms-btn::after {{
            content: "";
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            width: 14px;
            height: 14px;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;
            transition: transform 0.2s;
        }}
        .dropdown-ms.open .dropdown-ms-btn::after {{
            transform: translateY(-50%) rotate(180deg);
        }}
        .dropdown-ms-content {{
            display: none;
            position: absolute;
            background-color: var(--bg-card);
            min-width: 260px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-radius: 12px;
            padding: 10px;
            z-index: 1000;
            margin-top: 5px;
            border: 1px solid var(--border-clr);
            box-sizing: border-box;
        }}
        body.dark-mode .dropdown-ms-content {{
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        }}
        .dropdown-ms.open .dropdown-ms-content {{
            display: block;
        }}
        .dropdown-ms-search {{
            width: 100%;
            box-sizing: border-box;
            padding: 8px 10px;
            margin-bottom: 8px;
            border: 1px solid var(--border-clr);
            border-radius: 6px;
            background: var(--bg-body);
            color: var(--text-main);
            font-size: 12px;
            outline: none;
        }}
        .dropdown-ms-search:focus {{
            border-color: var(--accent);
        }}
        .dropdown-ms-actions {{
            display: flex;
            justify-content: space-between;
            padding: 4px 0 8px 0;
            border-bottom: 1px solid var(--border-clr);
            margin-bottom: 8px;
        }}
        .dropdown-ms-action-btn {{
            background: none;
            border: none;
            color: var(--accent);
            font-weight: 700;
            font-size: 11px;
            cursor: pointer;
            padding: 0;
        }}
        .dropdown-ms-action-btn:hover {{
            text-decoration: underline;
        }}
        .dropdown-ms-list {{
            max-height: 200px;
            overflow-y: auto;
            text-align: left;
        }}
        .dropdown-ms-item {{
            display: flex;
            align-items: center;
            padding: 6px 8px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            color: var(--text-main);
            transition: background 0.1s;
            margin-bottom: 2px;
        }}
        .dropdown-ms-item:hover {{
            background: rgba(37,99,235,0.08);
        }}
        .dropdown-ms-item input[type="checkbox"] {{
            margin-right: 10px;
            accent-color: var(--accent);
            cursor: pointer;
            width: 14px;
            height: 14px;
            flex-shrink: 0;
        }}
        .dropdown-ms-item span {{
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
    </style>
    """

    scripts = """
    <script>
    function toggleTheme() {
        document.body.classList.toggle('dark-mode');
        document.getElementById("themeBtn").innerText = document.body.classList.contains('dark-mode') ? "☀️ CLARO" : "🌙 OSCURO";
    }

    function toggleFocus(row) {
        row.classList.toggle('focused');
        if(row.classList.contains('focused')) {
            row.style.boxShadow = "inset 0 0 0 2px var(--accent)";
        } else {
            row.style.boxShadow = "none";
        }
    }
    
    // Toggle open/close of custom dropdowns
    document.addEventListener('click', function(e) {
        const clickedBtn = e.target.closest('.dropdown-ms-btn');
        const activeDropdown = document.querySelector('.dropdown-ms.open');
        
        if (activeDropdown && (!clickedBtn || activeDropdown !== clickedBtn.parentElement)) {
            if (!activeDropdown.contains(e.target)) {
                activeDropdown.classList.remove('open');
            }
        }
        
        if (clickedBtn) {
            const parent = clickedBtn.parentElement;
            const isOpen = parent.classList.contains('open');
            // Close all others
            document.querySelectorAll('.dropdown-ms').forEach(d => {
                if (d !== parent) d.classList.remove('open');
            });
            if (!isOpen) {
                parent.classList.add('open');
                // Auto focus search box inside
                const searchBox = parent.querySelector('.dropdown-ms-search');
                if (searchBox) {
                    searchBox.value = "";
                    searchDropdown(searchBox);
                    searchBox.focus();
                }
            } else {
                parent.classList.remove('open');
            }
            e.stopPropagation();
        }
    });

    // Search functionality inside the dropdown checklist
    function searchDropdown(input) {
        const filter = input.value.toUpperCase();
        const items = input.closest('.dropdown-ms-content').querySelectorAll('.dropdown-ms-item');
        items.forEach(item => {
            const text = item.textContent || item.innerText;
            if (text.toUpperCase().indexOf(filter) > -1) {
                item.style.display = "";
            } else {
                item.style.display = "none";
            }
        });
    }

    // Bulk action (Select All / Clear All)
    function toggleAllDropdown(btn, selectAll) {
        const parent = btn.closest('.dropdown-ms-content');
        const checkboxes = parent.querySelectorAll('.dropdown-ms-item input[type="checkbox"]');
        checkboxes.forEach(cb => {
            if (cb.closest('.dropdown-ms-item').style.display !== "none") {
                cb.checked = selectAll;
            }
        });
        updateDropdownLabel(parent.parentElement);
        filterTable();
    }

    // Update the button label to show current selections
    function updateDropdownLabel(dropdownEl) {
        const checkboxes = dropdownEl.querySelectorAll('.dropdown-ms-item input[type="checkbox"]');
        const checked = [];
        checkboxes.forEach(cb => {
            if (cb.checked) checked.push(cb.value);
        });
        
        const btn = dropdownEl.querySelector('.dropdown-ms-btn');
        const prefix = btn.getAttribute('data-prefix') || "";
        
        if (checked.length === 0) {
            btn.innerText = prefix + " (Ninguno)";
        } else if (checked.length === checkboxes.length) {
            btn.innerText = prefix + " (Todos)";
        } else if (checked.length <= 2) {
            btn.innerText = prefix + ": " + checked.join(", ");
        } else {
            btn.innerText = prefix + " (" + checked.length + ")";
        }
    }

    function filterTable() {
        const query = document.getElementById("searchBox").value.toUpperCase();
        
        // Get checked values from all multi-selects
        const getCheckedValues = (id) => {
            const cb = document.querySelectorAll(`#${id} .dropdown-ms-item input[type="checkbox"]`);
            const vals = [];
            cb.forEach(c => { if(c.checked) vals.push(c.value.toUpperCase()); });
            return vals;
        };
        
        const selectedIds = getCheckedValues("msId");
        const selectedVista = getCheckedValues("msVista");
        const selectedClients = getCheckedValues("msClient");
        const selectedStatuses = getCheckedValues("msStatus");
        const selectedPriorities = getCheckedValues("msPriority");
        const selectedBloques = getCheckedValues("msBloque");
        const selectedAreas = getCheckedValues("msArea");
        const selectedDevAreas = getCheckedValues("msDevArea");
        const selectedITTeams = getCheckedValues("msITTeam");
        const selectedGroup = document.getElementById("filterGroup").value.toUpperCase();
        
        const tr = document.querySelectorAll("#mainTable tr.row-item");
        let visible = 0;

        tr.forEach(row => {
            const rowId = (row.getAttribute("data-id") || "").toUpperCase();
            const rowVista = (row.getAttribute("data-vista") || "").toUpperCase();
            const rowClient = (row.getAttribute("data-client") || "").toUpperCase();
            const rowStatus = (row.getAttribute("data-status") || "").toUpperCase();
            const rowPriority = (row.getAttribute("data-priority") || "").toUpperCase();
            const rowBloque = (row.getAttribute("data-bloque") || "").toUpperCase();
            const rowArea = (row.getAttribute("data-area") || "").toUpperCase();
            const rowDevArea = (row.getAttribute("data-devarea") || "").toUpperCase();
            const rowITTeam = (row.getAttribute("data-itteam") || "").toUpperCase();
            const rowGroup = (row.getAttribute("data-group") || "").toUpperCase();
            const rowReq = (row.getAttribute("data-req") || "").toUpperCase();

            const matchesQuery = query === "" || rowReq.indexOf(query) > -1;
            const matchesId = selectedIds.length === 0 ? false : selectedIds.indexOf(rowId) > -1;
            const matchesVista = selectedVista.length === 0 ? false : selectedVista.indexOf(rowVista) > -1;
            const matchesClient = selectedClients.length === 0 ? false : selectedClients.indexOf(rowClient) > -1;
            const matchesStatus = selectedStatuses.length === 0 ? false : selectedStatuses.indexOf(rowStatus) > -1;
            const matchesPriority = selectedPriorities.length === 0 ? false : selectedPriorities.indexOf(rowPriority) > -1;
            const matchesBloque = selectedBloques.length === 0 ? false : selectedBloques.indexOf(rowBloque) > -1;
            const matchesArea = selectedAreas.length === 0 ? false : selectedAreas.indexOf(rowArea) > -1;
            const matchesDevArea = selectedDevAreas.length === 0 ? false : selectedDevAreas.indexOf(rowDevArea) > -1;
            const matchesITTeam = selectedITTeams.length === 0 ? false : selectedITTeams.indexOf(rowITTeam) > -1;
            const matchesGroup = selectedGroup === "" || rowGroup === selectedGroup;

            if (matchesQuery && matchesId && matchesVista && matchesClient && matchesStatus && matchesPriority && matchesBloque && matchesArea && matchesDevArea && matchesITTeam && matchesGroup) {
                row.style.display = ""; visible++;
            } else {
                row.style.display = "none";
            }
        });
        document.getElementById("matchCount").innerText = visible + " REGISTROS";
    }

    let currentFS = 13;
    function changeZoom(delta) {
        currentFS += delta;
        document.documentElement.style.setProperty('--table-fs', currentFS + 'px');
        document.getElementById("zoomIndicator").innerText = currentFS + "px";
    }
    </script>
    """

    # EXPERT COLORS
    H_R_ACT  = "transparent"; H_S_ACT  = "#2563eb"   # Default active (blue)
    H_R_VAL  = "#e8fdf0";    H_S_VAL  = "#22c55e"    # EN VALIDACION / EN PRUEBAS (Green)
    H_R_LIB  = "#dcfce7";    H_S_LIB  = "#166534"    # LIBERADO (Dark Green)
    H_R_DESA = "#fff7ed";    H_S_DESA = "#f97316"    # EN DESARROLLO (Orange)
    H_R_ESP  = "#f1f5f9";    H_S_ESP  = "#64748b"    # EN ESPERA / CANCELADO (Gray)
    H_R_SIN  = "#ffffff";    H_S_SIN  = "#cbd5e1"    # SIN PRIORIDAD (White bg, light gray accent)
    T_BLACK = "#000000"

    rows_html = ""
    current_group = None
    
    def clean_val(val):
        s = str(val).strip()
        return "(Vacío)" if s == "" or s.lower() == "nan" else s

    for _, r in df.iterrows():
        # Group Header
        if r['Group_Name'] != current_group:
            current_group = r['Group_Name']
            rows_html += f'<tr><td colspan="15" class="group-header">{current_group}</td></tr>'
            
        estatus_val = str(r['Estatus'])
        estatus_upper = estatus_val.upper()
        id_val = str(r['ID']).upper()
        
        # Color Logic adapted to the new statuses
        if "VALIDACION" in estatus_upper or "PRUEBAS" in estatus_upper:
            row_bg, accent_col = H_R_VAL, H_S_VAL
        elif "LIBERADO" in estatus_upper or "TERMINADO" in estatus_upper:
            row_bg, accent_col = H_R_LIB, H_S_LIB
        elif "DESARROLLO" in estatus_upper or "PRIORIZADO" in estatus_upper:
            row_bg, accent_col = H_R_DESA, H_S_DESA
        elif "ESPERA" in estatus_upper or "CANCELADO" in estatus_upper:
            row_bg, accent_col = H_R_ESP, H_S_ESP
        elif "SIN_PRIORIDAD" in estatus_upper or "SIN PRIORIDAD" in estatus_upper:
            row_bg, accent_col = H_R_SIN, H_S_SIN
        else:
            row_bg, accent_col = H_R_ACT, H_S_ACT
        
        # Format Priority & ID_PRIORIDAD representation
        prio_display = str(r['Filtro MAO'])
        if r['ID_PRIORIDAD'] != "" and pd.notna(r['ID_PRIORIDAD']):
            prio_display = f"{prio_display} ({r['ID_PRIORIDAD']})"

        comentarios_val = str(r['Comentarios']).replace('\n', '<br>')

        rows_html += f"""
        <tr class="row-item" data-id="{clean_val(r['ID'])}" data-vista="{clean_val(r['Vista'])}" data-group="{r['Group_Name']}" data-client="{clean_val(r['Cliente'])}" data-status="{clean_val(r['Estatus'])}" data-priority="{clean_val(r['Filtro MAO'])}" data-bloque="{clean_val(r['Bloque'])}" data-area="{clean_val(r['Area Desarrollo'])}" data-devarea="{clean_val(r['Area Desarrollo.1'])}" data-itteam="{clean_val(r['IT Team'])}" data-req="{str(r['Requerimiento']).strip()}" onclick="toggleFocus(this)">
            <td align="center" bgcolor="{row_bg}" style="font-weight:700; color:{T_BLACK};">{r['SEQ_IDX']}</td>
            <td align="center" bgcolor="{row_bg}"><span class="id-badge">{id_val}</span></td>
            <td bgcolor="{row_bg}" style="color:{T_BLACK}; font-size:12px;">{r['Vista']}</td>
            <td bgcolor="{row_bg}" style="color:{T_BLACK}; font-size:12px;">{r['Bloque']}</td>
            <td bgcolor="{row_bg}" style="color:{T_BLACK}; font-weight:700;">{r['Cliente']}</td>
            <td bgcolor="{row_bg}" style="min-width:450px; font-weight:700; font-size:14px; color:{T_BLACK};">
                <span class="status-dot" style="background-color:{accent_col};"></span>
                {r['Requerimiento']}
            </td>
            <td align="center" bgcolor="{row_bg}" style="color:{T_BLACK}; font-size:11px;">{r['#REQ']}</td>
            <td align="center" bgcolor="{row_bg}" style="font-weight:800; color:{accent_col};">{prio_display}</td>
            <td align="center" bgcolor="{row_bg}">
                <span class="status-pill" style="background-color:{accent_col}; color:#fff;">
                    {estatus_val}
                </span>
            </td>
            <td bgcolor="{row_bg}" style="color:{T_BLACK}; white-space:nowrap;">{r['Fecha_Inicio_Display']}</td>
            <td bgcolor="{row_bg}" style="font-weight:700; color:{T_BLACK}; white-space:nowrap;">{r['Fecha_Termino_Display']}</td>
            <td bgcolor="{row_bg}" style="color:{T_BLACK}; font-size:12px;"><b>{ICO_USER} {r['IT Team']}</b></td>
            <td bgcolor="{row_bg}" style="color:{T_BLACK}; font-size:11px;">{r['Recursos']}</td>
            <td bgcolor="{row_bg}" style="font-size:11.5px; color:{T_BLACK}; min-width:350px;">{comentarios_val}</td>
            <td bgcolor="{row_bg}" style="font-size:10px; color:{T_BLACK}; opacity:0.7;">{r['Area Desarrollo']}</td>
            <td bgcolor="{row_bg}" style="font-size:10px; color:{T_BLACK}; opacity:0.7;">{r['Area Desarrollo.1']}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><title>OmegaFusion | Executive Overdrive v50 (Actualizado)</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        {styles} {scripts}
    </head>
    <body oncontextmenu="return false;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#1e293b">
            <tr>
                <td style="padding:20px 45px;">
                     <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td align="left" style="font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
                                {ICO_OMEGA} <span style="margin-left:10px;">OMEGA</span><span style="color:#3b82f6;">FUSION</span>
                            </td>
                            <td align="right">
                                <table cellpadding="0" cellspacing="0" border="0" bgcolor="#2563eb" style="border-radius:12px;">
                                    <tr>
                                        <td align="center" style="padding:12px 30px;">
                                            <a href="#" style="color:#ffffff; font-weight:700; text-decoration:none; font-size:11px; display:inline-block; text-transform:uppercase;">
                                                {ICO_PLUS} NUEVO REQUERIMIENTO
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <div class="executive-container">
            <div class="kpi-row">
                <div class="kpi-card" style="border-left:8px solid #6366f1;">
                    <div><span class="kpi-lab">Total Requerimientos</span><span class="kpi-val">{total_rows}</span></div>
                    <div style="color:var(--text-sub);">{ICO_CHART}</div>
                </div>
                <div class="kpi-card" style="border-left:8px solid #2563eb;">
                    <div><span class="kpi-lab">Total Priorizados</span><span class="kpi-val">{priorizados}</span></div>
                    <div style="color:var(--text-sub);">{ICO_CHART}</div>
                </div>
                <div class="kpi-card" style="border-left:8px solid #22c55e;">
                    <div><span class="kpi-lab">Total Completados</span><span class="kpi-val" style="color:#22c55e;">{completados}</span></div>
                    <div style="color:var(--text-sub);">{ICO_CHART}</div>
                </div>
                <div class="kpi-card" style="border-left:8px solid #ef4444;">
                    <div><span class="kpi-lab">Sin Prioridad</span><span class="kpi-val" style="color:#ef4444;">{sin_prioridad}</span></div>
                    <div style="color:var(--text-sub);">{ICO_CHART}</div>
                </div>
            </div>

            <div class="filter-ribbon">
                <div class="search-group">
                    <span style="position:absolute; left:20px; color:var(--text-sub);">{ICO_SEARCH}</span>
                    <input type="text" id="searchBox" class="search-input" onkeyup="filterTable()" placeholder="Escribe para buscar por Requerimiento...">
                </div>
                {render_multiselect("msId", "🔑 ID", id_list)}
                {render_multiselect("msVista", "👁️ VISTA", vista_list)}
                {render_multiselect("msBloque", "📦 BLOQUE", bloques_list)}
                {render_multiselect("msClient", "🏢 CLIENTE", clientes_list)}
                {render_multiselect("msPriority", "⚡ PRIORIDAD", prioridades_list)}
                {render_multiselect("msStatus", "🚥 ESTATUS", estatus_list)}
                {render_multiselect("msITTeam", "👤 RESPONSABLE", itteam_list)}
                {render_multiselect("msArea", "⚙️ AREA ESTIMADO", areas_list)}
                {render_multiselect("msDevArea", "🛠️ AREA DESARROLLO", dev_areas_list)}
                <select id="filterGroup" class="select-pro" onchange="filterTable()"><option value="">📅 GRUPO SORT</option>{ "".join([f'<option value="{g}">{g}</option>' for g in grupos_list]) }</select>
                
                <div style="margin-left:auto; display:flex; gap:10px; align-items:center;">
                    <div style="display:flex; border:1px solid var(--border-clr); border-radius:10px; overflow:hidden;">
                        <button onclick="changeZoom(1)" style="padding:10px 15px; border:none; background:var(--bg-card); color:var(--text-main); cursor:pointer; font-weight:700;">+</button>
                        <button onclick="changeZoom(-1)" style="padding:10px 15px; border:none; border-left:1px solid var(--border-clr); background:var(--bg-card); color:var(--text-main); cursor:pointer; font-weight:700;">-</button>
                    </div>
                    <span id="zoomIndicator" style="font-size:11px; font-weight:700; background:var(--bg-card); padding:10px 14px; border-radius:10px; border:1px solid var(--border-clr);">13px</span>
                    <button id="themeBtn" onclick="toggleTheme()" style="padding:10px 20px; background:var(--omega); color:#fff; border:none; border-radius:10px; font-size:11px; font-weight:700; cursor:pointer;">🌙 OSCURO</button>
                    <div id="matchCount" style="background:var(--accent); color:#fff; padding:10px 20px; border-radius:10px; font-size:11px; font-weight:700;">{total_rows} REGISTROS</div>
                </div>
            </div>

            <div style="background:var(--bg-card); border-radius:20px; padding:20px; margin-bottom:30px; border:1px solid var(--border-clr); text-align:center;">
                <canvas id="monthChart" style="max-height: 250px; width:100%;"></canvas>
            </div>
            
            <div style="background:var(--bg-card); border-radius:20px; border:1px solid var(--border-clr); overflow:hidden; box-shadow:0 20px 50px rgba(0,0,0,0.05); overflow-x: auto;">
                <table id="mainTable">
                    <thead><tr><th>#</th><th>ID</th><th>VISTA</th><th>BLOQUE</th><th>CLIENTE</th><th>REQUERIMIENTO</th><th>#REQ</th><th>PR (ID)</th><th>ESTATUS</th><th>INICIO</th><th>TÉRMINO</th><th>RESPONSABLE</th><th>RECURSOS</th><th>NOTAS</th><th>AREA DE ESTIMADO</th><th>AREA DE DESARROLLO</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            
            <div style="text-align:center; padding:50px 0 20px 0; font-size:12px; color:var(--text-sub); font-weight:700; letter-spacing:4px; text-transform:uppercase; opacity:0.6;">
                OMEGAFUSION &bull; CINLAT LOGISTICS &bull; 2026
            </div>
        </div>
        <script>
            setTimeout(() => {{
                try {{
                    const ctx = document.getElementById('monthChart').getContext('2d');
                    new Chart(ctx, {{
                        type: 'bar',
                        data: {{
                            labels: {json.dumps(list(chart_data.keys()))},
                            datasets: [{{
                                label: 'Requerimientos Concluidos',
                                data: {json.dumps(list(chart_data.values()))},
                                backgroundColor: 'rgba(34, 197, 94, 0.8)',
                                borderRadius: 6
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{ display: false }},
                                title: {{ display: true, text: 'Rendimiento por Mes (Concluidos)', font: {{ size: 16 }} }}
                            }}
                        }}
                    }});
                }} catch(e) {{ console.error(e); }}
            }}, 500);
        </script>
    </body>
    </html>
    """
    out_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\priority_dashboard.html"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f: f.write(html)
    return "Dashboard v50 EXECUTIVE OVERDRIVE (NOM-012/Shapley Ready) Generado exitosamente."

if __name__ == "__main__":
    print(generate_report())
