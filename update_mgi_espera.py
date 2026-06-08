import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Prioridades_IT_2026_18_05_2026_v2.xlsx"

try:
    df = pd.read_excel(file_path)
    
    # Create mask to match the specific requirement
    mask = (df['Cliente'].astype(str).str.strip().str.upper() == 'MGI') & \
           (df['Requerimiento'].astype(str).str.strip() == 'Ecommerce PH')
           
    matches = df[mask].shape[0]
    print(f"Matches found: {matches}")
    
    if matches > 0:
        df.loc[mask, 'Estatus'] = 'EN ESPERA'
        df.to_excel(file_path, index=False)
        print("Excel updated successfully.")
    else:
        print("Warning: Could not find the row to update. Check criteria.")

except Exception as e:
    print(f"Error: {e}")
