import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Requerimientos_IT_24_04_2026_VF2.xlsx"
df = pd.read_excel(file_path)

# Filter out rows where Prioridad is empty or NA
mask_notna = df['Prioridad'].notna() & (df['Prioridad'] != '')

# Get boolean mask for rows where 'Mayo' is in the priority
mask_mayo = mask_notna & df['Prioridad'].astype(str).str.contains('Mayo', case=False)

# Count how many we are going to update
count = df[mask_mayo].shape[0]

if count > 0:
    df.loc[mask_mayo, 'Estatus'] = 'PRIORIZADO'
    print(f"Updated Estatus to 'PRIORIZADO' for {count} requirements.")
    df.to_excel(file_path, index=False)
    print("Saved Excel successfully.")
else:
    print("No requirements found with priority 'Mayo'.")
