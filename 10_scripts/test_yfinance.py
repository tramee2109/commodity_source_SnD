import yfinance as yf
import pandas as pd

tickers = {
    "silver_futures": "SI=F",
    "copper_futures": "HG=F",
    "platinum_futures": "PL=F",
    "gold_futures": "GC=F",
    "slv_etf": "SLV",
    "cper_etf": "CPER",
    "pplt_etf": "PPLT",
    "dxy_index": "DX-Y.NYB",
    "us10y_yield": "^TNX"
}

print("Testing yfinance continuous data download from 2000-01-01 to present...")
summary = {}
for name, ticker in tickers.items():
    try:
        df = yf.download(ticker, start="2000-01-01", progress=False)
        if not df.empty:
            start_date = str(df.index[0].date())
            end_date = str(df.index[-1].date())
            count = len(df)
            print(f"  {name} ({ticker}): {count} rows from {start_date} to {end_date}")
            summary[name] = {"start": start_date, "end": end_date, "count": count}
        else:
            print(f"  {name} ({ticker}): EMPTY")
    except Exception as e:
        print(f"  {name} ({ticker}): ERROR {e}")
