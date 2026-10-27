import requests
from urllib.parse import quote

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

files = [
    "https://platinuminvestment.com/files/354715/WPIC_PQ_tables_Q2_2026.xlsx",
    "https://platinuminvestment.com/files/" + quote("Johnson Matthey xls-2004-to-2012.xls"),
    "https://platinuminvestment.com/files/" + quote("Johnson Matthey xls-2000-to-2004.xls")
]

for url in files:
    r = requests.get(url, headers=headers, timeout=15)
    print(f"WPIC File: {url.split('/')[-1]} -> Status {r.status_code}, Length {len(r.content)}")
