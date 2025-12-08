import pandas as pd
import sys

try:
    xl = pd.ExcelFile('kada_attendance.xlsx')
    with open('sheets_structure.txt', 'w', encoding='utf-8') as f:
        f.write(f"Sheet Names: {xl.sheet_names}\n")
        for sheet in xl.sheet_names:
            df = xl.parse(sheet)
            f.write(f"\n--- Sheet: {sheet} ---\n")
            f.write(f"Columns: {df.columns.tolist()}\n")
except Exception as e:
    with open('sheets_structure.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {str(e)}")
