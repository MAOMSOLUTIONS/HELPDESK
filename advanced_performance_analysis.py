import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

# Configure display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

TODAY = datetime.now()

def month_to_num(spanish_month):
    months = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    return months.get(str(spanish_month).lower().strip(), 1)

def parse_spanish_date(date_str):
    if pd.isna(date_str) or str(date_str).strip() == '' or str(date_str) == 'nan':
        return pd.NaT
    try:
        parts = str(date_str).replace(',', '').split()
        if len(parts) == 3:
            month = month_to_num(parts[0])
            day = int(parts[1])
            year = int(parts[2])
            return datetime(year, month, day)
    except:
        pass
    return pd.to_datetime(date_str, errors='coerce')

def get_latest_report():
    files = glob.glob('ReporteHelpdesk*.xlsx')
    files = [f for f in files if 'temp' not in f]
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def run_final_analysis(file_path=None):
    if not file_path:
        file_path = get_latest_report()
        
    if not file_path or not os.path.exists(file_path):
        return None

    df_raw = pd.read_excel(file_path, header=None)
    cols = [
        'ID', 'Anio', 'Mes_Exp', 'Fecha_alta', 'Fecha_asig', 'Fecha_sol', 'Dias_Export', 
        'Cat', 'Emp', 'User', 'Depto', 'Req', 'Estado', 'Resp', 'Clasificacion', 
        'Comentario1', 'Comentario2'
    ]
    
    rows = []
    for i, row in df_raw.iterrows():
        try:
            val = str(row[0]).replace('.0', '')
            if val.isdigit() and int(val) > 8000:
                rows.append(row.tolist()[:17])
        except:
            continue
            
    df = pd.DataFrame(rows)
    df.columns = cols[:df.shape[1]]
    
    # Cleaning
    df['ID'] = df['ID'].astype(int)
    df['Fecha_alta'] = df['Fecha_alta'].apply(parse_spanish_date)
    df['Fecha_sol'] = df['Fecha_sol'].apply(parse_spanish_date)
    df['Estado'] = df['Estado'].fillna('DESCONOCIDO').astype(str).str.strip().str.upper()
    df['Resp'] = df['Resp'].fillna('SIN ASIGNAR').astype(str).str.strip().str.upper()
    df['User'] = df['User'].fillna('SIN USUARIO').astype(str).str.strip().str.upper()
    df['Depto'] = df['Depto'].fillna('SIN AREA').astype(str).str.strip().str.upper()
    
    # Standard Month Names
    month_names = {
        1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 
        6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'
    }
    df['Mes_Num'] = df['Fecha_alta'].dt.month
    df['Mes_Nombre'] = df['Mes_Num'].map(month_names).fillna('Otro')
    
    # SLA Logic (72h = 3 days)
    df['Is_Closed'] = df['Estado'].apply(lambda x: any(s in x for s in ['CERRADO', 'SOLUCIONADA', 'FINALIZADO', 'RESUELTO']))
    
    def calc_aging(row):
        if row['Is_Closed'] and pd.notna(row['Fecha_sol']):
            delta = (row['Fecha_sol'] - row['Fecha_alta']).days
            return delta if delta >= 0 else 0
        delta = (TODAY - row['Fecha_alta']).days
        return delta if delta >= 0 else 0
        
    df['Aging'] = df.apply(calc_aging, axis=1)
    df['SLA_Status'] = df['Aging'].apply(lambda x: 'IN SLA' if x <= 3 else 'OUT SLA')
    
    # 1. Monthly Matrix (Must include Jan, Feb, Mar, Apr)
    monthly = df.groupby(['Mes_Num', 'Mes_Nombre']).agg(
        Cerrados_InTime=('ID', lambda x: ((df.loc[x.index, 'Is_Closed']) & (df.loc[x.index, 'SLA_Status'] == 'IN SLA')).sum()),
        Cerrados_OutTime=('ID', lambda x: ((df.loc[x.index, 'Is_Closed']) & (df.loc[x.index, 'SLA_Status'] == 'OUT SLA')).sum()),
        Abiertos_InTime=('ID', lambda x: ((~df.loc[x.index, 'Is_Closed']) & (df.loc[x.index, 'SLA_Status'] == 'IN SLA')).sum()),
        Abiertos_OutTime=('ID', lambda x: ((~df.loc[x.index, 'Is_Closed']) & (df.loc[x.index, 'SLA_Status'] == 'OUT SLA')).sum())
    )
    # Calculate KPIs
    monthly['Total_Cerrados'] = monthly['Cerrados_InTime'] + monthly['Cerrados_OutTime']
    monthly['KPI_%_Cerrados_En_Tiempo'] = (monthly['Cerrados_InTime'] / monthly['Total_Cerrados'] * 100).fillna(0).round(1).astype(str) + '%'
    monthly['KPI_%_Cerrados_Fuera_Tiempo'] = (monthly['Cerrados_OutTime'] / monthly['Total_Cerrados'] * 100).fillna(0).round(1).astype(str) + '%'
    
    # Reorder columns to insert KPIs next to closures
    monthly = monthly[['Cerrados_InTime', 'KPI_%_Cerrados_En_Tiempo', 'Cerrados_OutTime', 'KPI_%_Cerrados_Fuera_Tiempo', 
                       'Abiertos_InTime', 'Abiertos_OutTime', 'Total_Cerrados']].sort_index()

    # 2. Closure Curve (Individual days 1, 2, 3, 4, 5, 6...)
    def curve_days(d):
        if d <= 10: return f'Dia {int(d)}'
        return 'Dia 10+'
    
    df['Curve'] = df['Aging'].apply(curve_days)
    closure_curve = df[df['Is_Closed']].groupby(['Mes_Nombre', 'Curve']).size().unstack(fill_value=0)
    # Sort columns by day number
    cols_sorted = sorted(closure_curve.columns, key=lambda x: int(x.split()[1]) if 'Dia' in x and '+' not in x else 100)
    closure_curve = closure_curve[cols_sorted]
    
    # 3. Unassigned with Aging and Description
    unassigned = df[df['Resp'] == 'SIN ASIGNAR'].copy()
    unassigned = unassigned[['ID', 'Fecha_alta', 'Aging', 'Depto', 'User', 'Req']]
    unassigned.columns = ['ID', 'Fecha_Alta', 'Dias_Sin_Asignar', 'Area', 'Usuario', 'Solicitud_Completa']
    
    # 4. Tech Evaluation
    tech_eval = df.groupby('Resp').agg(
        Total_Cerrados=('Is_Closed', 'sum'),
        Cerrados_In_SLA=('ID', lambda x: ((df.loc[x.index, 'Is_Closed']) & (df.loc[x.index, 'SLA_Status'] == 'IN SLA')).sum()),
        Cerrados_Out_SLA=('ID', lambda x: ((df.loc[x.index, 'Is_Closed']) & (df.loc[x.index, 'SLA_Status'] == 'OUT SLA')).sum()),
        Abiertos=('Is_Closed', lambda x: (~x).sum())
    ).sort_values(by='Total_Cerrados', ascending=False)
    
    # 5. Pareto Users (80/20) with ALL requested status
    user_p = df.groupby('User').agg(
        Total_Tickets=('ID', 'count'),
        Abiertos=('Is_Closed', lambda x: (~x).sum()),
        Cerrados=('Is_Closed', 'sum'),
        Cerrados_In_SLA=('ID', lambda x: ((df.loc[x.index, 'Is_Closed']) & (df.loc[x.index, 'SLA_Status'] == 'IN SLA')).sum()),
        Cerrados_Out_SLA=('ID', lambda x: ((df.loc[x.index, 'Is_Closed']) & (df.loc[x.index, 'SLA_Status'] == 'OUT SLA')).sum())
    ).sort_values(by='Total_Tickets', ascending=False)
    
    user_p['CumPerc'] = 100 * user_p['Total_Tickets'].cumsum() / user_p['Total_Tickets'].sum()
    pareto_users = user_p[user_p['CumPerc'] <= 86] # Approx top users representing ~85% of volume

    return {
        'timestamp': TODAY.strftime('%Y-%m-%d %H:%M:%S'),
        'monthly': monthly,
        'closure_curve': closure_curve,
        'tech_eval': tech_eval,
        'unassigned': unassigned.sort_values(by='Dias_Sin_Asignar', ascending=False),
        'user_stats': pareto_users
    }

if __name__ == "__main__":
    res = run_final_analysis()
    if res:
        with open('final_dashboard_data.txt', 'w', encoding='utf-8') as f:
            f.write(f"HEADER: {res['timestamp']}\n\n")
            f.write("MONTHLY:\n")
            f.write(res['monthly'].to_string() + "\n\n")
            f.write("CLOSURE_CURVE:\n")
            f.write(res['closure_curve'].to_string() + "\n\n")
            f.write("TECH_EVAL:\n")
            f.write(res['tech_eval'].to_string() + "\n\n")
            f.write("UNASSIGNED_DETAIL:\n")
            f.write(res['unassigned'].to_string() + "\n\n")
            f.write("USER_PARETO_80_20:\n")
            f.write(res['user_stats'].to_string() + "\n")
