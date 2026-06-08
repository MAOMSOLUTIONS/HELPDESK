import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(file_path)

mask3 = df['Requerimiento'].str.contains("Cálculo d eFee de forma electrónica", case=False, na=False)
if df[mask3].empty:
    print("Warning: 'Cálculo d eFee de forma electrónica' not found")
else:
    df.loc[mask3, 'Fecha_entrega'] = pd.to_datetime('2026-06-01')
    print("Updated date for 'Cálculo d eFee de forma electrónica'")

df.to_excel(file_path, index=False)
print("Updated excel successfully")
