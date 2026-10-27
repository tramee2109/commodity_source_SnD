from curl_cffi import requests
import json

urls = [
    "https://publicreporting.cftc.gov/resource/6dca-qvwv.json?$limit=5",
    "https://www.cftc.gov/files/dea/history/deacot2024.zip",
    "https://www.cftc.gov/dea/futures/deacmxsf.htm"
]

print("Testing CFTC with curl_cffi (impersonating Chrome)...")
for u in urls:
    try:
        r = requests.get(u, impersonate="chrome120", timeout=15)
        print(f"URL: {u}")
        print(f"  Status: {r.status_code}, Length: {len(r.content)}")
        if r.status_code == 200 and "json" in u:
            data = r.json()
            print(f"  First item market name: {data[0].get('market_and_exchange_names')}")
    except Exception as e:
        print(f"URL: {u} -> Exception: {e}")
