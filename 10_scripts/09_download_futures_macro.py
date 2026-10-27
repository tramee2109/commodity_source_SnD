import sys
from pathlib import Path
import yfinance as yf
import pandas as pd
import requests
import io

sys.path.append(str(Path(__file__).parent))
from download_utils import compute_sha256, record_manifest, BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "macro_cross"

TICKERS = {
    "silver_futures": {"ticker": "SI=F", "metal": "Silver", "source_id": "SRC_CME_SILVER_FUTURES"},
    "copper_futures": {"ticker": "HG=F", "metal": "Copper", "source_id": "SRC_CME_COPPER_FUTURES"},
    "platinum_futures": {"ticker": "PL=F", "metal": "Platinum", "source_id": "SRC_NYMEX_PLATINUM_FUTURES"},
    "gold_futures": {"ticker": "GC=F", "metal": "Gold (Cross-metal)", "source_id": "SRC_CME_GOLD_FUTURES"},
    "crude_oil_futures": {"ticker": "CL=F", "metal": "Energy (Cross-market)", "source_id": "SRC_NYMEX_CRUDE_FUTURES"},
    "silver_etf_slv": {"ticker": "SLV", "metal": "Silver", "source_id": "SRC_ISHARES_SLV"},
    "copper_etf_cper": {"ticker": "CPER", "metal": "Copper", "source_id": "SRC_USCF_CPER"},
    "platinum_etf_pplt": {"ticker": "PPLT", "metal": "Platinum", "source_id": "SRC_ABRDN_PPLT"},
    "dollar_index_dxy": {"ticker": "DX-Y.NYB", "metal": "Macro FX", "source_id": "SRC_ICE_DXY"}
}

FRED_SERIES = {
    "us_10y_real_yield": {"id": "DFII10", "metal": "Macro Yields", "desc": "10-Year Real Interest Rate"},
    "us_10y_nominal_yield": {"id": "DGS10", "metal": "Macro Yields", "desc": "10-Year Treasury Constant Maturity"},
    "us_10y_breakeven_inflation": {"id": "T10YIE", "metal": "Macro Inflation", "desc": "10-Year Breakeven Inflation Rate"},
    "us_industrial_production": {"id": "INDPRO", "metal": "Macro Activity", "desc": "Industrial Production Index"},
    "trade_weighted_usd_broad": {"id": "DTWEXBGS", "metal": "Macro FX", "desc": "Nominal Broad U.S. Dollar Index"}
}

def download_market_tickers():
    print("=== Downloading Continuous Futures and ETFs (yfinance) ===")
    for key, info in TICKERS.items():
        ticker = info["ticker"]
        local_name = f"market__{key}__{ticker.replace('^', '').replace('=', '_')}__daily.csv"
        target_path = RAW_DIR / local_name
        file_id = f"RAW_MKT_{key.upper()}"
        
        try:
            df = yf.download(ticker, start="2000-01-01", progress=False)
            if not df.empty:
                df.to_csv(target_path)
                size = target_path.stat().st_size
                sha = compute_sha256(target_path)
                print(f"[DOWNLOADED] {ticker} -> {local_name} ({len(df)} rows, {size} bytes)")
                record_manifest(file_id, info["metal"], info["source_id"], local_name, f"yfinance:{ticker}", "csv", size, "SUCCESS", target_path, sha)
            else:
                print(f"[EMPTY] {ticker}")
        except Exception as e:
            print(f"[ERROR] {ticker} -> {e}")

def download_fred_series():
    print("\n=== Downloading FRED Macro Variables ===")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for key, info in FRED_SERIES.items():
        sid = info["id"]
        local_name = f"macro__fred__{key}__{sid}__daily.csv"
        target_path = RAW_DIR / local_name
        file_id = f"RAW_FRED_{sid.upper()}"
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                with open(target_path, "wb") as f:
                    f.write(r.content)
                size = target_path.stat().st_size
                sha = compute_sha256(target_path)
                print(f"[DOWNLOADED] FRED {sid} -> {local_name} ({size} bytes)")
                record_manifest(file_id, info["metal"], "SRC_FRED_MACRO_FACTORS", local_name, url, "csv", size, "SUCCESS", target_path, sha)
            else:
                print(f"[FAILED] FRED {sid} -> Status {r.status_code}")
        except Exception as e:
            print(f"[ERROR] FRED {sid} -> {e}")

if __name__ == "__main__":
    download_market_tickers()
    download_fred_series()
