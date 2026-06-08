import pandas as pd
import os
import subprocess

excel_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(excel_path)

# Find and update statuses
mask1 = df['Requerimiento'].str.contains('Refacturación LIVERPOOL ECOMMERCE', na=False, case=False)
mask2 = df['Requerimiento'].str.contains('Implementación módulo de finanzas avanzadas', na=False, case=False)

df.loc[mask1 | mask2, 'Estatus'] = 'Terminado'

# Save back to Excel
df.to_excel(excel_path, index=False)
print("Excel file updated.")

# Generate Priority Report
subprocess.run(["python", "generate_priority_report.py"], check=True)
print("Dashboard regenerated.")

# Send report privately
subprocess.run(["python", "send_estatus_it_final.py", "--private"], check=True)
print("Report sent to Miguel.")
