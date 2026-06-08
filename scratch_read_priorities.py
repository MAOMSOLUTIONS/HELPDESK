import pandas as pd

file_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\Prioridades_IT_13_05_2026.xlsx"
df = pd.read_excel(file_path)
print(df.head(20).to_string())
print("\nColumns:", df.columns.tolist())
