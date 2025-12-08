import pandas as pd

xl = pd.ExcelFile('kada_attendance.xlsx')
print(f"Sheet names: {xl.sheet_names}")
for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    print(f"\n--- Sheet: {sheet} ---")
    print(f"Columns: {df.columns.tolist()}")
