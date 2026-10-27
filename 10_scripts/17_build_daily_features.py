import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).parent))
from download_utils import BASE_DIR

CAN_DIR = BASE_DIR / "06_canonical"
RAW_DIR = BASE_DIR / "02_raw" / "macro_cross"
EXT_DIR = BASE_DIR / "03_extracted"
FEAT_DIR = BASE_DIR / "07_daily_features"
FEAT_DIR.mkdir(parents=True, exist_ok=True)

def parse_yf_csv(filepath, val_col_name="price", include_vol=False):
    # yfinance multi-index CSV has 3 header rows:
    # 0: Price,Close,High,Low,Open,Volume
    # 1: Ticker,SI=F,SI=F,SI=F,SI=F,SI=F
    # 2: Date,,,,,
    # 3+: 2000-08-30, 4.9299, 4.9499, 4.8949, 4.9499, 2319
    df = pd.read_csv(filepath, skiprows=3, header=None)
    if include_vol:
        df = df.iloc[:, [0, 1, 5]].copy()
        df.columns = ["date", val_col_name, "volume"]
    else:
        df = df.iloc[:, [0, 1]].copy()
        df.columns = ["date", val_col_name]
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df[val_col_name] = pd.to_numeric(df[val_col_name], errors="coerce")
    if include_vol:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    return df.dropna(subset=["date", val_col_name]).drop_duplicates(subset=["date"])

def load_market_data():
    print("Loading daily futures and macro series...", flush=True)
    mkt = {}
    
    # Silver Futures
    f_ag = RAW_DIR / "market__silver_futures__SI_F__daily.csv"
    mkt["Silver"] = parse_yf_csv(f_ag, val_col_name="price", include_vol=True)
        
    # Copper Futures
    f_cu = RAW_DIR / "market__copper_futures__HG_F__daily.csv"
    mkt["Copper"] = parse_yf_csv(f_cu, val_col_name="price", include_vol=True)
        
    # Platinum Futures
    f_pt = RAW_DIR / "market__platinum_futures__PL_F__daily.csv"
    mkt["Platinum"] = parse_yf_csv(f_pt, val_col_name="price", include_vol=True)
        
    # Gold Futures
    f_au = RAW_DIR / "market__gold_futures__GC_F__daily.csv"
    mkt["Gold"] = parse_yf_csv(f_au, val_col_name="gold_price", include_vol=False)
    
    # Dollar Index
    f_dxy = RAW_DIR / "market__dollar_index_dxy__DX-Y.NYB__daily.csv"
    mkt["DXY"] = parse_yf_csv(f_dxy, val_col_name="dxy_index", include_vol=False)
    
    # FRED Macro Series
    f_ry = RAW_DIR / "macro__fred__us_10y_real_yield__DFII10__daily.csv"
    df_ry = pd.read_csv(f_ry)
    df_ry.columns = ["date", "real_yield_10y"]
    df_ry["date"] = pd.to_datetime(df_ry["date"], errors="coerce").dt.date
    df_ry["real_yield_10y"] = pd.to_numeric(df_ry["real_yield_10y"], errors="coerce")
    mkt["RealYield"] = df_ry.dropna().drop_duplicates(subset=["date"])
    
    f_ny = RAW_DIR / "macro__fred__us_10y_nominal_yield__DGS10__daily.csv"
    df_ny = pd.read_csv(f_ny)
    df_ny.columns = ["date", "nominal_yield_10y"]
    df_ny["date"] = pd.to_datetime(df_ny["date"], errors="coerce").dt.date
    df_ny["nominal_yield_10y"] = pd.to_numeric(df_ny["nominal_yield_10y"], errors="coerce")
    mkt["NominalYield"] = df_ny.dropna().drop_duplicates(subset=["date"])

    return mkt

def load_cot_data():
    cot_path = EXT_DIR / "cftc_cot_positioning_extracted.csv"
    if not cot_path.exists():
        return {}
    df_cot = pd.read_csv(cot_path)
    df_cot["report_date"] = pd.to_datetime(df_cot["Report_Date_as_YYYY-MM-DD"]).dt.date
    # CFTC release date is Friday after Tuesday report date (+3 calendar days)
    df_cot["available_date"] = pd.to_datetime(df_cot["report_date"]) + pd.to_timedelta(3, unit="D")
    df_cot["available_date"] = df_cot["available_date"].dt.date
    
    cot_dict = {}
    for m in ["Silver", "Copper", "Platinum"]:
        sub = df_cot[df_cot["metal"] == m].copy()
        cot_dict[m] = sub.sort_values(by="available_date")
    return cot_dict

def load_fundamental_releases():
    can_path = CAN_DIR / "fundamental_latest.parquet"
    df_can = pd.read_parquet(can_path)
    
    pivoted = {}
    for m in ["Silver", "Copper", "Platinum"]:
        sub = df_can[df_can["metal"] == m].copy()
        if m == "Silver":
            req_metrics = ["total_supply", "total_physical_demand", "market_balance_reported"]
        else:
            req_metrics = ["total_supply", "total_demand", "market_balance_reported", "refined_production", "refined_usage"]
            
        sub_key = sub[sub["metric"].isin(req_metrics)].copy()
        sub_key["available_at"] = pd.to_datetime(sub_key["available_at"]).dt.date
        pivoted[m] = sub_key.sort_values(by="available_at")
    return pivoted

def build_daily_features():
    mkt = load_market_data()
    cot = load_cot_data()
    fund = load_fundamental_releases()
    
    # Master business day trading calendar 2000-01-01 to 2026-10-20
    all_dates = [d.date() for d in pd.date_range("2000-01-01", "2026-10-20", freq="B")]
    
    panel_dfs = []
    
    for metal in ["Silver", "Copper", "Platinum"]:
        print(f"Building daily feature panel for {metal}...", flush=True)
        df_metal = pd.DataFrame({"date": all_dates, "metal": metal})
        
        # 1. Merge Price and Technicals
        df_px = mkt[metal]
        df_metal = pd.merge(df_metal, df_px, on="date", how="left")
        
        # Forward fill price on missing exchange holidays if needed for continuous series
        df_metal["price_ffill"] = df_metal["price"].ffill()
        df_metal["price_return_1d"] = df_metal["price_ffill"].pct_change()
        df_metal["price_return_20d"] = df_metal["price_ffill"].pct_change(20)
        df_metal["price_return_60d"] = df_metal["price_ffill"].pct_change(60)
        df_metal["price_volatility_20d"] = df_metal["price_return_1d"].rolling(20).std() * np.sqrt(252)
        
        # 2. Merge Point-In-Time Fundamentals (No lookahead)
        sub_fund = fund[metal]
        fund_records = []
        for d in all_dates:
            avail = sub_fund[sub_fund["available_at"] <= d]
            if not avail.empty:
                latest_avail_date = avail["available_at"].max()
                days_since = (d - latest_avail_date).days
                latest_rows = avail[avail["available_at"] == latest_avail_date]
                
                sup = latest_rows[latest_rows["metric"].str.contains("supply")]["value_standardized"].values
                dem = latest_rows[latest_rows["metric"].str.contains("demand|usage")]["value_standardized"].values
                bal = latest_rows[latest_rows["metric"] == "market_balance_reported"]["value_standardized"].values
                
                sup_val = float(sup[0]) if len(sup) > 0 else np.nan
                dem_val = float(dem[0]) if len(dem) > 0 else np.nan
                bal_val = float(bal[0]) if len(bal) > 0 else (sup_val - dem_val if pd.notna(sup_val) and pd.notna(dem_val) else np.nan)
                
                bal_to_sup = bal_val / sup_val if pd.notna(sup_val) and sup_val != 0 else np.nan
                
                fund_records.append({
                    "date": d,
                    "latest_supply": sup_val,
                    "latest_demand": dem_val,
                    "latest_market_balance": bal_val,
                    "balance_to_supply_ratio": bal_to_sup,
                    "days_since_fundamental_release": days_since,
                    "fundamental_available_at": latest_avail_date
                })
            else:
                fund_records.append({
                    "date": d,
                    "latest_supply": np.nan,
                    "latest_demand": np.nan,
                    "latest_market_balance": np.nan,
                    "balance_to_supply_ratio": np.nan,
                    "days_since_fundamental_release": np.nan,
                    "fundamental_available_at": None
                })
                
        df_fund = pd.DataFrame(fund_records)
        df_metal = pd.merge(df_metal, df_fund, on="date", how="left")
        
        # 3. Merge Point-In-Time CFTC COT Positioning
        if metal in cot and not cot[metal].empty:
            sub_cot = cot[metal][["available_date", "Open_Interest_All", "managed_money_net", "commercial_producer_net"]].copy()
            sub_cot.rename(columns={"available_date": "date", "Open_Interest_All": "open_interest"}, inplace=True)
            df_metal = pd.merge(df_metal, sub_cot, on="date", how="left")
            df_metal["open_interest"] = df_metal["open_interest"].ffill()
            df_metal["managed_money_net"] = df_metal["managed_money_net"].ffill()
            df_metal["commercial_producer_net"] = df_metal["commercial_producer_net"].ffill()
            df_metal["net_positioning_change_20d"] = df_metal["managed_money_net"].diff(20)
        else:
            df_metal["open_interest"] = np.nan
            df_metal["managed_money_net"] = np.nan
            df_metal["commercial_producer_net"] = np.nan
            df_metal["net_positioning_change_20d"] = np.nan
            
        # 4. Merge Macro Variables
        df_metal = pd.merge(df_metal, mkt["Gold"], on="date", how="left")
        df_metal = pd.merge(df_metal, mkt["DXY"], on="date", how="left")
        df_metal = pd.merge(df_metal, mkt["RealYield"], on="date", how="left")
        df_metal = pd.merge(df_metal, mkt["NominalYield"], on="date", how="left")
        
        df_metal["gold_price"] = df_metal["gold_price"].ffill()
        df_metal["dxy_index"] = df_metal["dxy_index"].ffill()
        df_metal["real_yield_10y"] = df_metal["real_yield_10y"].ffill()
        df_metal["nominal_yield_10y"] = df_metal["nominal_yield_10y"].ffill()
        
        # Ratios
        if metal == "Silver":
            df_metal["gold_silver_ratio"] = df_metal["gold_price"] / df_metal["price_ffill"]
        elif metal == "Copper":
            df_metal["copper_gold_ratio"] = (df_metal["price_ffill"] * 1000) / df_metal["gold_price"]
        elif metal == "Platinum":
            df_metal["platinum_gold_ratio"] = df_metal["price_ffill"] / df_metal["gold_price"]
            
        df_metal["data_quality_status"] = "Verified"
        panel_dfs.append(df_metal)
        
    df_panel = pd.concat(panel_dfs, ignore_index=True)
    df_panel = df_panel.sort_values(by=["metal", "date"])
    
    out_csv = FEAT_DIR / "daily_fundamental_features.csv"
    out_parquet = FEAT_DIR / "daily_fundamental_features.parquet"
    df_panel.to_csv(out_csv, index=False, encoding="utf-8")
    df_panel.to_parquet(out_parquet, index=False)
    print(f"\n[FEATURES] Built Daily Panel with {len(df_panel)} daily rows -> {out_csv} and {out_parquet}", flush=True)
    
    for m in ["Silver", "Copper", "Platinum"]:
        sub = df_panel[df_panel["metal"] == m]
        valid_px = sub["price"].count()
        valid_fund = sub["latest_market_balance"].count()
        valid_cot = sub["managed_money_net"].count()
        print(f"  {m}: {len(sub)} business days | Prices: {valid_px} | PIT Fundamentals: {valid_fund} | COT: {valid_cot}", flush=True)
    return df_panel

if __name__ == "__main__":
    build_daily_features()
