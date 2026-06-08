import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configure display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def month_to_num(spanish_month):
    months = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    return months.get(spanish_month.lower(), 1)

def parse_spanish_date(date_str):
    if pd.isna(date_str) or str(date_str).strip() == '':
        return pd.NaT
    try:
        # Example: 'Abril 07, 2026' or 'Marzo 13, 2026'
        parts = str(date_str).replace(',', '').split()
        if len(parts) == 3:
            month = month_to_num(parts[0])
            day = int(parts[1])
            year = int(parts[2])
            return datetime(year, month, day)
    except Exception as e:
        pass
    return pd.to_datetime(date_str, errors='coerce')

def run_deep_dive():
    file_path = 'ReporteHelpdesk09_04_2026.xlsx'
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    # Load data - The inspection showed it starts around row 0 or has no clear header
    # Let's use the columns we identified
    cols = [
        'ID', 'Anio', 'Mes', 'Fecha_alta', 'Fecha_asignada', 'Fecha_solucion', 
        'Dias', 'Categoria', 'No_Empleado', 'Usuario', 'Departamento', 
        'Solicitud', 'Estado', 'Responsable', 'Clasificacion', 'Comentario1', 'Comentario2'
    ]
    
    # Try different starting points to find the real data
    # Based on inspection, data was visible early on
    df = pd.read_excel(file_path, header=None)
    
    # Filter only rows that look like ticket data (starting with a numeric ID > 10000)
    data_rows = []
    for i, row in df.iterrows():
        try:
            if str(row[0]).isdigit() and int(row[0]) > 8000:
                data_rows.append(row)
        except:
            continue
            
    if not data_rows:
        print("No ticket data found.")
        return
        
    df = pd.DataFrame(data_rows)
    df.columns = cols[:len(df.columns)]
    
    # Clean data
    df['Estado'] = df['Estado'].fillna('Desconocido').astype(str).str.strip()
    df['Responsable'] = df['Responsable'].fillna('Sin Asignar').astype(str).str.strip()
    
    # Parse dates
    for col in ['Fecha_alta', 'Fecha_asignada', 'Fecha_solucion']:
        df[col] = df[col].apply(parse_spanish_date)
    
    today = datetime.now()
    
    # 1. DISPERSION ANALYSIS
    print("--- 1. Technician Dispersion (Tickets Assigned vs Solved) ---")
    dispersion = df.groupby('Responsable').agg(
        Total_Asignados=('ID', 'count'),
        Solucionados=('Estado', lambda x: x.str.contains('SOLUCIONADA|SOLUCIONADO', case=False).sum()),
        En_Desarrollo=('Estado', lambda x: x.str.contains('EN DESARROLLO', case=False).sum()),
        Pendientes=('Estado', lambda x: x.str.contains('PENDIENTE', case=False).sum())
    )
    dispersion['%_Efectividad'] = (dispersion['Solucionados'] / dispersion['Total_Asignados'] * 100).round(2)
    print(dispersion.sort_values(by='Total_Asignados', ascending=False))
    
    # 2. DELAYED DEVELOPMENT TICKETS
    print("\n--- 2. Delayed 'EN DESARROLLO' Tickets (> 7 days) ---")
    in_dev = df[df['Estado'].str.contains('EN DESARROLLO', case=False)].copy()
    in_dev['Aging'] = (today - in_dev['Fecha_alta']).dt.days
    delayed = in_dev[in_dev['Aging'] > 7].sort_values(by='Aging', ascending=False)
    
    if not delayed.empty:
        print(delayed[['ID', 'Fecha_alta', 'Responsable', 'Aging', 'Solicitud']].head(20))
    else:
        print("No delayed 'EN DESARROLLO' tickets found.")
        
    # 3. NO PROCEDE LIST
    print("\n--- 3. List of 'NO PROCEDE' Tickets ---")
    no_procede = df[df['Estado'].str.contains('NO PROCEDE', case=False)]
    if not no_procede.empty:
        print(no_procede[['ID', 'Fecha_alta', 'Responsable', 'Solicitud']])
    else:
        print("No 'NO PROCEDE' tickets found.")

    # 4. ADDITIONAL ANALYSIS: Load by Department
    print("\n--- 4. Load by Department (Top 10) ---")
    dept_load = df['Departamento'].value_counts().head(10)
    print(dept_load)

    # Export to results file
    with open('deep_dive_results.txt', 'w', encoding='utf-8') as f:
        f.write("HELP DESK PERFORMANCE DEEP DIVEn")
        f.write(f"Analyzed on: {today.strftime('%Y-%m-%d %H:%M:%S')}n")
        f.write("n--- DISPERSION ---n")
        f.write(dispersion.to_string())
        f.write("n--- DELAYED DEVELOPMENT ---n")
        f.write(delayed[['ID', 'Fecha_alta', 'Responsable', 'Aging']].to_string())
        f.write("n--- NO PROCEDE LIST ---n")
        f.write(no_procede[['ID', 'Fecha_alta', 'Responsable', 'Solicitud']].to_string())

if __name__ == "__main__":
    run_deep_dive()
