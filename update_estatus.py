import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(file_path)

reqs_to_update = [2306, 2307, 2308, 2309, 2310]

for req_id in reqs_to_update:
    mask = df['#REQ'] == req_id
    if not df[mask].empty:
        df.loc[mask, 'Estatus'] = 'SIN_PRIORIDAD'
        print(f"Updated Estatus for #REQ {req_id}")
    else:
        # Check if it was saved as a string or float in pandas
        mask_str = df['#REQ'].astype(str) == str(req_id)
        if not df[mask_str].empty:
            df.loc[mask_str, 'Estatus'] = 'SIN_PRIORIDAD'
            print(f"Updated Estatus for #REQ {req_id} (string match)")
        else:
            print(f"Warning: #REQ {req_id} not found")

df.to_excel(file_path, index=False)
print("Saved Excel successfully.")
