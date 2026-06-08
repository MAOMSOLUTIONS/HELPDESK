import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(file_path)

updates = [
    {"req": "Ecommerce PH", "fecha": "TBC"},
    {"req": "Configurar el sistema para que", "fecha": "TBC"},
    {"req": "RECUEPRAR PEDIDOS DE AMAZON", "fecha": "TBC"},
    {"req": "Corregir en remisión", "fecha": "TBC"},
    {"req": "Agregar columna fecha de embarque", "fecha": "TBC"},
    {"req": "Separar los consumibles", "fecha": "TBC"},
    {"req": "No rebasar montos de seguro", "fecha": "TBC"},
    {"req": "AGREGAR EL ALMACEN DESTINO A TC", "prioridad": "7_Mayo", "fecha": "TBC"}
]

for u in updates:
    mask = df['Requerimiento'].str.contains(u['req'], case=False, na=False)
    
    if df[mask].empty:
        print(f"Warning: '{u['req']}' not found.")
    else:
        df.loc[mask, 'Fecha_entrega'] = u['fecha']
        if 'prioridad' in u:
            df.loc[mask, 'Prioridad'] = u['prioridad']
        print(f"Updated: '{u['req']}'")

# ADD NEW ROW
new_req = {
    'ID': 'P',
    'Bloque': 'N/A',
    'Cliente': 'HERMES',
    'Requerimiento': 'Devoluciones automáticas',
    '#REQ': 2148,
    'Prioridad': '9_Mayo',
    'Estatus': 'Desarrollo',
    'Fecha_entrega': 'TBC',
    'IT Team': 'TBD',
    'Comentarios': '',
    'Area Desarrollo': 'TBD'
}
# Append using loc or concat
df = pd.concat([df, pd.DataFrame([new_req])], ignore_index=True)
print("Added new requirement 2148 for HERMES")

df.to_excel(file_path, index=False)
print("Saved Excel successfully.")
