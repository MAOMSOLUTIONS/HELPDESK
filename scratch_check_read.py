import pandas as pd
import os
from datetime import datetime

INPUT_DIR = r"c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk"
TODAY_STR = datetime.now().strftime("%d_%m_%Y")
INPUT_FILE_TODAY = os.path.join(INPUT_DIR, f"ReporteHelpdesk{TODAY_STR}.xlsx")

print(f"Checking {INPUT_FILE_TODAY}...")
if os.path.exists(INPUT_FILE_TODAY):
    try:
        df = pd.read_excel(INPUT_FILE_TODAY, skiprows=4)
        print(f"Read success: {len(df)} rows")
    except Exception as e:
        print(f"Read failed: {e}")
else:
    print("File does not exist")
