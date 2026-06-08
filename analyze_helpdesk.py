import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configure display for columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

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

def analyze_helpdesk():
    # Detect the latest report file
    import glob
    files = glob.glob('ReporteHelpdesk*.xlsx')
    files = [f for f in files if 'temp' not in f]
    if not files:
        print("No Helpdesk report files found.")
        return
    
    # Sort by modification time to get the newest
    files.sort(key=os.path.getmtime, reverse=True)
    file_path = files[0]
    print(f"Analyzing latest file: {file_path}")

    # Load data
    # Header is at row 4 (0-indexed)
    df = pd.read_excel(file_path, skiprows=4)
    
    # Fix column names (encoding issues)
    # Ao alta -> Año alta
    df.columns = [str(c).replace('Ao alta', 'Año alta').strip() for c in df.columns]
    
    # Ensure date parsing
    date_cols = ['Fecha alta', 'Fecha asignada', 'Fecha solucion']
    available_date_cols = [col for col in date_cols if col in df.columns]
    for col in available_date_cols:
        df[col] = df[col].apply(parse_spanish_date)
    
    # Fill missing values for analysis
    if 'Estado' in df.columns:
        df['Estado'] = df['Estado'].fillna('Desconocido').astype(str)
    if 'Departamento' in df.columns:
        df['Departamento'] = df['Departamento'].fillna('Sin Area').astype(str)
    if 'Responsable' in df.columns:
        df['Responsable'] = df['Responsable'].fillna('Sin Asignar').astype(str)
    
    # 1. STATUS ANALYSIS
    status_counts = df['Estado'].value_counts()
    print("--- Status Distribution ---")
    print(status_counts)
    
    # 2. OPEN TICKETS AGING
    today = datetime.now()
    open_tickets = df[df['Estado'].str.contains('Abierto|Nuevo|Iniciado|Pendiente|Asignado|En proceso', case=False)]
    open_tickets = open_tickets.copy()
    open_tickets['Aging'] = (today - open_tickets['Fecha alta']).dt.days
    
    print("\n--- Open Tickets Aging (Days since higher to lower) ---")
    if not open_tickets.empty:
        print(open_tickets[['ID', 'Fecha alta', 'Departamento', 'Aging']].sort_values(by='Aging', ascending=False).head(10))
    else:
        print("No open tickets found based on 'Estado'.")

    # 3. CLOSED TICKETS & SLA ANALYSIS (3 DAYS)
    closed_states = ['Cerrado', 'Solucionado', 'Finalizado', 'Resuelto']
    closed_tickets = df[df['Estado'].str.contains('|'.join(closed_states), case=False)].copy()
    
    if not closed_tickets.empty:
        # User requested 1, 2, 3... n days curve
        # Note: 'Dias solucion' might already contain this, but let's recalculate for safety
        closed_tickets['Calc_Dias'] = (closed_tickets['Fecha solucion'] - closed_tickets['Fecha alta']).dt.days
        # If Calc_Dias is 0, it means same day.
        
        sla_days = 3
        closed_tickets['SLA_Status'] = closed_tickets['Calc_Dias'].apply(lambda x: 'IN SLA' if x <= sla_days else 'OUT SLA')
        
        print("\n--- SLA Performance (%) ---")
        print(closed_tickets['SLA_Status'].value_counts(normalize=True) * 100)
        
        # Trend Analysis: Improvements in March and April
        closed_tickets['Month'] = closed_tickets['Fecha alta'].dt.month
        march_closed = closed_tickets[closed_tickets['Month'] == 3]
        april_closed = closed_tickets[closed_tickets['Month'] == 4]
        
        print("\n--- SLA Trend (March vs April) ---")
        if not march_closed.empty:
            print("March SLA (% IN SLA):")
            print(march_closed['SLA_Status'].value_counts(normalize=True) * 100)
        if not april_closed.empty:
            print("April SLA (% IN SLA):")
            print(april_closed['SLA_Status'].value_counts(normalize=True) * 100)
            
        print("\n--- Closure Curve (Days to close) ---")
        print(closed_tickets['Calc_Dias'].value_counts().sort_index())
    
    # 4. RECURRING ISSUES (TOP 10)
    # Using 'Solicitud' for keyword analysis or frequency
    print("\n--- Top 10 Recurring Categories ---")
    if 'Categoria' in df.columns:
        print(df['Categoria'].value_counts().head(10))
    
    print("\n--- Top 10 Recurring Requests (Likely Patterns) ---")
    # Simple word/subject frequency for finding patterns
    top_requests = df['Solicitud'].str.lower().value_counts().head(10)
    print(top_requests)
    
    # 5. IT RESOURCE DISPERSION
    print("\n--- IT Resource Performance (Closed Tickets) ---")
    if not closed_tickets.empty:
        resource_perf = closed_tickets['Responsable'].value_counts()
        print(resource_perf)
        
        print("\n--- Delayed Resources (Mean Days to Solucion) ---")
        delayed = closed_tickets.groupby('Responsable')['Calc_Dias'].mean().sort_values(ascending=False)
        print(delayed)

    # Export summarized data to CSV for final report if needed
    # (Optional: save analysis results for the Model to read or to present)
    return df

if __name__ == "__main__":
    df = analyze_helpdesk()
