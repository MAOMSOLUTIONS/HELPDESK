import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(file_path)

updates = [
    {
        "req": "REQUERIMIENTO PARA INGRESAR CANTIDADES TOTALES",
        "req_num": 2136,
        "estatus": "Terminado"
    },
    {
        "req": "Agregar en el reporte bitacora de pedidos una columna en donde se refleje el peso",
        "cliente": "HERMES",
        "estatus": "Terminado"
    },
    {
        "req": "la carga de prodcutos por medio de plantillas para el alta de productos",
        "cliente": "HYBE",
        "estatus": "Cancelado"
    },
    {
        "req": "AGRGEAR EL ALAMCEN OTROS EN LA TC",
        "cliente": "HERMES",
        "estatus": "Cancelado"
    }
]

for u in updates:
    # Build mask
    mask = df['Requerimiento'].str.contains(u['req'], case=False, na=False)
    
    if 'cliente' in u:
        mask = mask & df['Cliente'].str.contains(u['cliente'], case=False, na=False)
        
    if 'req_num' in u:
        mask = mask | (df['#REQ'].astype(str) == str(u['req_num']))

    if df[mask].empty:
        print(f"Warning: Requerimiento for '{u.get('req')}' not found.")
    else:
        df.loc[mask, 'Estatus'] = u['estatus']
        # If it's Cancelado, maybe also remove the Priority or Fecha? The user didn't specify. I'll just change Estatus.
        print(f"Updated Estatus to '{u['estatus']}' for '{u.get('req')}'")

df.to_excel(file_path, index=False)
print("Saved Excel successfully.")
