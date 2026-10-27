import requests
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def probe_url(url, timeout=10, get_content=True):
    try:
        if get_content:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
        else:
            r = requests.head(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return {
            "url": url,
            "status": r.status_code,
            "content_type": r.headers.get("content-type", ""),
            "size": len(r.content) if get_content else int(r.headers.get("content-length", 0)),
            "content": r.content if get_content else b""
        }
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e), "size": 0, "content": b""}

def check_silver_institute():
    print("--- [1/6] Probing Silver Institute ---", flush=True)
    urls = [
        "https://silverinstitute.org/silver-supply-demand/",
        "https://silverinstitute.org/all-world-silver-surveys-2025/",
        "https://silverinstitute.org/world-silver-survey/"
    ]
    results = {}
    for u in urls:
        res = probe_url(u, timeout=12)
        print(f"Silver Institute: {u} -> Status {res['status']}, Size {res['size']}", flush=True)
        if res["status"] == 200:
            soup = BeautifulSoup(res["content"], "html.parser")
            pdf_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if ".pdf" in href.lower() or "survey" in href.lower():
                    pdf_links.append((a.get_text(strip=True), href))
            tables = soup.find_all("table")
            print(f"  Found {len(tables)} HTML tables, {len(pdf_links)} PDF/Survey links", flush=True)
            results[u] = {
                "status": 200,
                "tables_count": len(tables),
                "pdf_links": pdf_links[:15]
            }
        else:
            results[u] = {"status": res["status"]}
    return results

def check_wpic():
    print("\n--- [2/6] Probing WPIC (World Platinum Investment Council) ---", flush=True)
    urls = [
        "https://platinuminvestment.com/supply-and-demand/historic-data",
        "https://platinuminvestment.com/supply-and-demand/platinum-quarterly"
    ]
    results = {}
    for u in urls:
        res = probe_url(u, timeout=12)
        print(f"WPIC: {u} -> Status {res['status']}, Size {res['size']}", flush=True)
        if res["status"] == 200:
            soup = BeautifulSoup(res["content"], "html.parser")
            download_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if any(ext in href.lower() for ext in [".xlsx", ".xls", ".csv", ".pdf", "download"]):
                    download_links.append((a.get_text(strip=True), href))
            tables = soup.find_all("table")
            print(f"  Found {len(tables)} tables, {len(download_links)} downloadable links", flush=True)
            results[u] = {
                "status": 200,
                "tables_count": len(tables),
                "download_links": download_links[:15]
            }
        else:
            results[u] = {"status": res["status"]}
    return results

def check_icsg():
    print("\n--- [3/6] Probing ICSG (International Copper Study Group) ---", flush=True)
    urls = [
        "https://icsg.org/selected-copper-statistics/",
        "https://icsg.org/copper-bulletin/",
        "https://icsg.org/download/icsg-copper-statistical-yearbook-2015-2024-2025-edition-excel-tables/"
    ]
    results = {}
    for u in urls:
        res = probe_url(u, timeout=12)
        print(f"ICSG: {u} -> Status {res['status']}, Size {res['size']}", flush=True)
        if res["status"] == 200:
            soup = BeautifulSoup(res["content"], "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if any(ext in href.lower() for ext in [".xlsx", ".xls", ".pdf", "download", "statistical"]):
                    links.append((a.get_text(strip=True), href))
            tables = soup.find_all("table")
            print(f"  Found {len(tables)} tables, {len(links)} candidate links", flush=True)
            results[u] = {"status": 200, "tables_count": len(tables), "links": links[:15]}
        else:
            results[u] = {"status": res["status"]}
    return results

def check_usgs():
    print("\n--- [4/6] Probing USGS Mineral Commodity Summaries ---", flush=True)
    years = [2025, 2024, 2023, 2022, 2021, 2020, 2018, 2015, 2010, 2005, 2000]
    metals = ["silver", "copper", "platinum"]
    
    probe_tasks = []
    for m in metals:
        for y in years:
            url1 = f"https://pubs.usgs.gov/periodicals/mcs{y}/mcs{y}-{m}.pdf"
            probe_tasks.append((m, y, url1))
    
    found = {m: [] for m in metals}
    
    def check_task(t):
        metal, year, url = t
        res = probe_url(url, timeout=6, get_content=False)
        return (metal, year, url, res["status"], res["size"])
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        for metal, year, url, status, size in executor.map(check_task, probe_tasks):
            if status == 200:
                print(f"  USGS {metal.capitalize()} {year}: FOUND ({size} bytes) -> {url}", flush=True)
                found[metal].append({"year": year, "url": url, "size": size})
            else:
                # Alternate pattern for older years
                pass
    return found

def check_world_bank():
    print("\n--- [5/6] Probing World Bank Pink Sheet ---", flush=True)
    wb_url = "https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx"
    res = probe_url(wb_url, timeout=15, get_content=False)
    print(f"  World Bank Pink Sheet Monthly: Status {res['status']}, Size {res['size']} bytes", flush=True)
    return {"status": res["status"], "size": res["size"], "url": wb_url}

def check_cftc():
    print("\n--- [6/6] Probing CFTC COT ---", flush=True)
    cftc_socrata = "https://publicreporting.cftc.gov/resource/6dca-qvwv.json?$limit=5"
    res_soc = probe_url(cftc_socrata, timeout=10, get_content=True)
    print(f"  CFTC Socrata API: Status {res_soc['status']}, Size {res_soc['size']}", flush=True)
    
    zip_url_2024 = "https://www.cftc.gov/files/dea/history/deacot2024.zip"
    res_zip = probe_url(zip_url_2024, timeout=10, get_content=False)
    print(f"  CFTC Zip Archive (2024): Status {res_zip['status']}, Size {res_zip['size']} bytes", flush=True)
    return {
        "socrata": {"status": res_soc["status"], "size": res_soc["size"]},
        "zip_2024": {"status": res_zip["status"], "size": res_zip["size"]}
    }

if __name__ == "__main__":
    si = check_silver_institute()
    wpic = check_wpic()
    icsg = check_icsg()
    usgs = check_usgs()
    wb = check_world_bank()
    cftc = check_cftc()
    
    out = {
        "silver_institute": si,
        "wpic": wpic,
        "icsg": icsg,
        "usgs": usgs,
        "world_bank": wb,
        "cftc": cftc
    }
    
    out_file = Path(r"e:\My\the20\test_strategy\commodity source\commodity_equilibrium\01_source_registry\probe_discovery_summary.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=4, default=str)
    print(f"\n[ALL DONE] Results saved to {out_file}", flush=True)
