import pandas as pd

master_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
new_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Prioridades_IT_13_05_2026.xlsx"

df_master = pd.read_excel(master_path)
df_new = pd.read_excel(new_path)

print("Master #REQ sample:", df_master['#REQ'].head(5).tolist())
print("New #REQ sample:", df_new['#REQ'].head(5).tolist())

# Check for #REQ 2306 which was added in add_reqs.py
print("\nIs 2306 in Master?", 2306 in df_master['#REQ'].values)
print("Is 2306 in New?", 2306 in df_new['#REQ'].values)

# Check for MGI Ecommerce PH which was in update_excel_priorities.py
print("\nMGI Ecommerce PH in Master Priority:", df_master[df_master['Requerimiento'].str.contains('Ecommerce PH', na=False)]['Prioridad'].tolist())
print("MGI Ecommerce PH in New Priority:", df_new[df_new['Requerimiento'].str.contains('Ecommerce PH', na=False)]['Prioridad'].tolist())
