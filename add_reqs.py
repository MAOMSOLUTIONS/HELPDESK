import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(file_path)

new_reqs = [
    {
        'ID': 'P', 'Bloque': 'N/A', 'Cliente': 'INTERNO',
        'Requerimiento': 'No rebasar montos de seguro por consolidaciones',
        '#REQ': 2306, 'Prioridad': '', 'Estatus': 'Desarrollo',
        'Fecha_entrega': 'SIN_PRIORIDAD', 'IT Team': 'TBD', 'Comentarios': '', 'Area Desarrollo': 'TBD'
    },
    {
        'ID': 'P', 'Bloque': 'N/A', 'Cliente': 'INTERNO',
        'Requerimiento': 'Implementar un control vía sistema que permita consultar OC, remesa y pedimento',
        '#REQ': 2307, 'Prioridad': '', 'Estatus': 'Desarrollo',
        'Fecha_entrega': 'SIN_PRIORIDAD', 'IT Team': 'TBD', 'Comentarios': '', 'Area Desarrollo': 'TBD'
    },
    {
        'ID': 'P', 'Bloque': 'N/A', 'Cliente': 'HERMES',
        'Requerimiento': 'Realizar la carga de plantilla de pedidos mediante el envío de dichas plantillas a un correo de intranet',
        '#REQ': 2308, 'Prioridad': '', 'Estatus': 'Desarrollo',
        'Fecha_entrega': 'SIN_PRIORIDAD', 'IT Team': 'TBD', 'Comentarios': '', 'Area Desarrollo': 'TBD'
    },
    {
        'ID': 'P', 'Bloque': 'N/A', 'Cliente': 'HERMES',
        'Requerimiento': 'Realizar el alta de productos nuevos mediante una plantilla de excel',
        '#REQ': 2309, 'Prioridad': '', 'Estatus': 'Desarrollo',
        'Fecha_entrega': 'SIN_PRIORIDAD', 'IT Team': 'TBD', 'Comentarios': '', 'Area Desarrollo': 'TBD'
    },
    {
        'ID': 'P', 'Bloque': 'N/A', 'Cliente': 'HERMES',
        'Requerimiento': 'Realizar el alta de productos nuevos mediante una plantilla',
        '#REQ': 2310, 'Prioridad': '', 'Estatus': 'Desarrollo',
        'Fecha_entrega': 'SIN_PRIORIDAD', 'IT Team': 'TBD', 'Comentarios': '', 'Area Desarrollo': 'TBD'
    }
]

# For 2306, check if it already exists, if so update it, otherwise append.
# For others, just append.

for req in new_reqs:
    if req['#REQ'] == 2306:
        mask = df['Requerimiento'].str.contains("No rebasar montos de seguro", case=False, na=False)
        if not df[mask].empty:
            df.loc[mask, '#REQ'] = 2306
            df.loc[mask, 'Fecha_entrega'] = 'SIN_PRIORIDAD'
            print(f"Updated existing requirement {req['#REQ']}")
            continue
            
    df = pd.concat([df, pd.DataFrame([req])], ignore_index=True)
    print(f"Added new requirement {req['#REQ']}")

df.to_excel(file_path, index=False)
print("Saved Excel successfully.")
