import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.cftc.gov/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}
s = requests.Session()
r = s.get('https://www.cftc.gov/dea/futures/deacmxsf.htm', headers=headers)
print('COMEX current report status:', r.status_code, len(r.content))
r2 = s.get('https://www.cftc.gov/files/dea/history/fut_disagg_txt_2024.zip', headers=headers)
print('CFTC Disaggregated 2024 zip status:', r2.status_code, len(r2.content))
r3 = s.get('https://www.cftc.gov/files/dea/history/deacot2024.zip', headers=headers)
print('CFTC Legacy 2024 zip status:', r3.status_code, len(r3.content))
