import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from download_utils import download_file, BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "cftc_cot"

HEADERS = {
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

YEARS = [2024, 2023, 2022, 2021, 2020, 2019, 2018]

def main():
    print("=== Downloading CFTC COT Historical Zip Archives ===")
    
    # 1. Disaggregated Futures Only (covers Managed Money, Producers, Swap Dealers)
    for y in YEARS:
        url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{y}.zip"
        target = RAW_DIR / f"cftc__cot_disaggregated_futures__{y}__original.zip"
        file_id = f"RAW_CFTC_COT_DISAGG_{y}"
        download_file(url, target, file_id, "Multi-metal (Silver/Copper/Platinum)", "SRC_CFTC_SILVER_COT", custom_headers=HEADERS)

    # 2. Legacy Futures Only
    for y in YEARS:
        url = f"https://www.cftc.gov/files/dea/history/deacot{y}.zip"
        target = RAW_DIR / f"cftc__cot_legacy_futures__{y}__original.zip"
        file_id = f"RAW_CFTC_COT_LEGACY_{y}"
        download_file(url, target, file_id, "Multi-metal (Silver/Copper/Platinum)", "SRC_CFTC_SILVER_COT", custom_headers=HEADERS)

    # 3. Current year / latest release (COMEX report text)
    url_comex = "https://www.cftc.gov/dea/futures/deacmxsf.htm"
    target_comex = RAW_DIR / "cftc__comex_disaggregated_current__original.htm"
    download_file(url_comex, target_comex, "RAW_CFTC_COMEX_CURRENT", "Silver/Copper", "SRC_CFTC_SILVER_COT", custom_headers=HEADERS)
    
    url_nymex = "https://www.cftc.gov/dea/futures/deanymsf.htm"
    target_nymex = RAW_DIR / "cftc__nymex_disaggregated_current__original.htm"
    download_file(url_nymex, target_nymex, "RAW_CFTC_NYMEX_CURRENT", "Platinum", "SRC_CFTC_PLATINUM_COT", custom_headers=HEADERS)

    print("CFTC COT download finished.\n")

if __name__ == "__main__":
    main()
