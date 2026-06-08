import pandas as pd
import re

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(file_path)

# Filter out rows where Prioridad is empty or NA
df_prioritized = df[df['Prioridad'].notna() & (df['Prioridad'] != '')].copy()

# Keep only rows where 'Mayo' is in the priority
df_mayo = df_prioritized[df_prioritized['Prioridad'].astype(str).str.contains('Mayo', case=False)].copy()

# Sort by the number in the priority string
def extract_num(p):
    nums = re.findall(r'\d+', str(p))
    return int(nums[0]) if nums else 999

df_mayo['Prior_Num'] = df_mayo['Prioridad'].apply(extract_num)
df_mayo = df_mayo.sort_values('Prior_Num')

print("--- REQUERIMIENTOS PRIORIZADOS PARA MAYO ---")
for _, row in df_mayo.iterrows():
    print(f"- Prioridad: {row['Prioridad']} | Cliente: {row['Cliente']} | Requerimiento: {row['Requerimiento']} | #REQ: {row['#REQ']}")
