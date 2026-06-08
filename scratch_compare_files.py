import pandas as pd
import os

master_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
new_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Prioridades_IT_13_05_2026.xlsx"

df_master = pd.read_excel(master_path)
df_new = pd.read_excel(new_path)

print(f"Master rows: {len(df_master)}")
print(f"New rows: {len(df_new)}")

print("\nMaster Columns:", df_master.columns.tolist())
print("New Columns:", df_new.columns.tolist())

# Check for differences in '#REQ' or 'Requerimiento'
print("\nUnique REQs in Master:", df_master['#REQ'].nunique())
print("Unique REQs in New:", df_new['#REQ'].nunique())
