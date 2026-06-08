import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(file_path)

mask_hermes1 = df['Requerimiento'].str.contains("AGREGAR EL ALMACEN DESTINO A TC", case=False, na=False)
print("HERMES 1 found:", not df[mask_hermes1].empty)

# Print #REQ 2148 if it exists
mask_2148 = df['#REQ'] == 2148
# Some #REQ might be strings
mask_2148_str = df['#REQ'].astype(str).str.contains("2148", na=False)

if not df[mask_2148].empty:
    print("2148 found as int")
elif not df[mask_2148_str].empty:
    print("2148 found as string")
else:
    print("2148 NOT found")
