import pandas as pd
import sys

try:
    df = pd.read_excel('kada_attendance.xlsx')
    with open('schema.txt', 'w', encoding='utf-8') as f:
        f.write(f"Columns: {df.columns.tolist()}\n")
        if not df.empty:
            f.write(f"First row: {df.iloc[0].tolist()}\n")
except Exception as e:
    with open('schema.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {str(e)}")
