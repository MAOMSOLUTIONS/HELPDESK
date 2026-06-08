import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(file_path)

updates = [
    {"cliente": "MGI", "req": "Ecommerce PH", "prioridad": "1_Mayo"},
    {"cliente": "LATAMEL", "req": "Configurar el sistema para que", "prioridad": "2_Mayo"},
    {"cliente": "MGI", "req": "RECUEPRAR PEDIDOS DE AMAZON", "prioridad": "3_Mayo"},
    {"cliente": "Altamirano", "req": "Corregir en remisión", "prioridad": "4_Mayo"},
    {"cliente": "TPLINK", "req": "Agregar columna fecha de embarque", "prioridad": "6_Mayo"},
    {"cliente": "TPLINK", "req": "Separar los consumibles", "prioridad": "8_Mayo"},
    {"cliente": "INTERNO", "req": "No rebasar montos de seguro", "prioridad": "10"}
]

for u in updates:
    # Handle possible spelling errors or abbreviations by just matching the substring in Requerimiento
    mask = df['Requerimiento'].str.contains(u['req'], case=False, na=False)
    
    if df[mask].empty:
        print(f"Warning: Requerimiento containing '{u['req']}' not found.")
    else:
        # If multiple matches, we might want to also filter by cliente if provided
        if len(df[mask]) > 1:
            mask = mask & df['Cliente'].str.contains(u['cliente'], case=False, na=False)
            
        if df[mask].empty:
            print(f"Warning: Requerimiento '{u['req']}' for client '{u['cliente']}' not found.")
        else:
            df.loc[mask, 'Prioridad'] = u['prioridad']
            print(f"Updated: '{u['req']}' -> {u['prioridad']}")

df.to_excel(file_path, index=False)
print("Saved Excel successfully.")
