import pandas as pd
import sys

# Force utf-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

wb_path = r'02_raw/platinum/platinum__wpic__platinum_quarterly_tables__2026_q2__original.xlsx'
df = pd.read_excel(wb_path, sheet_name="Table 1(Q2'26)", header=None)

for idx in range(35, len(df)):
    m1 = str(df.iloc[idx, 1]) if pd.notna(df.iloc[idx, 1]) else ""
    m2 = str(df.iloc[idx, 2]) if pd.notna(df.iloc[idx, 2]) else ""
    metric = m1 or m2
    if metric:
        vals = [str(round(float(x), 1)) if isinstance(x, (int, float)) and pd.notna(x) else str(x)[:8] for x in df.iloc[idx, 3:10] if pd.notna(x)]
        print(f"Row {idx:2d} | {metric[:35]:35s} | {vals}")
