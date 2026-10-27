import requests
import pandas as pd
import io

series = ["DFII10", "DGS10", "T10YIE", "INDPRO", "DTWEXBGS"]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

print("Testing FRED direct CSV downloads...")
for s in series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}"
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        df = pd.read_csv(io.StringIO(r.text))
        print(f"  FRED {s}: Status 200, {len(df)} rows from {df.iloc[0,0]} to {df.iloc[-1,0]}")
    else:
        print(f"  FRED {s}: Status {r.status_code}")
