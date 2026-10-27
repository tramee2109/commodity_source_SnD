from curl_cffi import requests
from bs4 import BeautifulSoup
import re

url = "https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm"
r = requests.get(url, impersonate="chrome120", timeout=15)
print(f"Status: {r.status_code}, Length: {len(r.content)}")

if r.status_code == 200:
    soup = BeautifulSoup(r.content, "html.parser")
    zip_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".zip" in href.lower() or "cot" in href.lower():
            zip_links.append((a.get_text(strip=True), href))
    print(f"Found {len(zip_links)} links:")
    for txt, link in zip_links[:20]:
        print(f"  {txt} -> {link}")
