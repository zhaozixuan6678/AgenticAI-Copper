import pandas as pd
import sys

excel_path = sys.argv[1]

try:
    xls = pd.ExcelFile(excel_path)
    print(f"Sheets in {excel_path}:")
    for sheet_name in xls.sheet_names:
        print(f"- {sheet_name}")
except Exception as e:
    print(f"Error reading Excel file {excel_path}: {e}")