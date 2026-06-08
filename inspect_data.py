import pandas as pd
import sys

# Load the Excel file
file_path = 'ReporteHelpdesk06_04_2026.xlsx'

# Let's inspect the first 10 rows without header to find where it starts
raw_df = pd.read_excel(file_path, header=None)
print("--- Raw First 10 rows ---")
print(raw_df.head(10))

# Looking for common header names like 'ID' or 'Fecha'
header_row = -1
for i, row in raw_df.iterrows():
    if any(str(val).strip().lower() in ['id', 'estatus', 'fecha alta', 'ao alta', 'prioridad'] for val in row):
        header_row = i
        break

if header_row != -1:
    print(f"\n--- Header seems to be at row {header_row} ---")
    df = pd.read_excel(file_path, skiprows=header_row)
else:
    print("\n--- Header not found, using skiprows=4 by default ---")
    df = pd.read_excel(file_path, skiprows=4)

print("\n--- Columns found ---")
print(df.columns.tolist())

print("\n--- Sample Data (First 10 rows) ---")
print(df.head(10))

print("\n--- Value Counts for key columns ---")
for col in ['Estatus', 'Area', 'Responsable', 'Prioridad', 'Clasificacion']:
    if col in df.columns:
        print(f"\nValue counts for {col}:")
        print(df[col].value_counts().head(10))
    else:
        # Search for similar column names
        sim = [c for c in df.columns if col.lower() in c.lower()]
        if sim:
            print(f"\nValue counts for {sim[0]}:")
            print(df[sim[0]].value_counts().head(10))
