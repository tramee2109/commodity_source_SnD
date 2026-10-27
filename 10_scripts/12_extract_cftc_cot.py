import sys
import zipfile
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from download_utils import BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "cftc_cot"
OUT_DIR = BASE_DIR / "03_extracted"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_METALS = {
    "SILVER": {
        "metal": "Silver",
        "market_pattern": "SILVER - COMMODITY EXCHANGE INC.",
        "contract_code": "084691"
    },
    "COPPER": {
        "metal": "Copper",
        "market_pattern": "COPPER-GRADE #1 - COMMODITY EXCHANGE INC.",
        "contract_code": "085692"
    },
    "PLATINUM": {
        "metal": "Platinum",
        "market_pattern": "PLATINUM - NEW YORK MERCANTILE EXCHANGE",
        "contract_code": "076651"
    }
}

COLS_TO_KEEP = [
    "Market_and_Exchange_Names",
    "Report_Date_as_YYYY-MM-DD",
    "CFTC_Contract_Market_Code",
    "Open_Interest_All",
    "Prod_Merc_Positions_Long_All",
    "Prod_Merc_Positions_Short_All",
    "Swap_Positions_Long_All",
    "Swap_Positions_Short_All",
    "Swap_Positions_Spread_All",
    "M_Money_Positions_Long_All",
    "M_Money_Positions_Short_All",
    "M_Money_Positions_Spread_All",
    "Other_Rept_Positions_Long_All",
    "Other_Rept_Positions_Short_All",
    "Tot_Rept_Positions_Long_All",
    "Tot_Rept_Positions_Short_All",
    "NonRept_Positions_Long_All",
    "NonRept_Positions_Short_All"
]

def clean_col(c):
    return str(c).strip().strip('"')

def process_disaggregated_zip(zip_path, year):
    records = []
    print(f"Reading {zip_path.name} ({year})...", flush=True)
    with zipfile.ZipFile(zip_path) as z:
        for fname in z.namelist():
            if fname.endswith(".txt") or fname.endswith(".csv"):
                with z.open(fname) as f:
                    df = pd.read_csv(f, low_memory=False)
                    # Clean column names
                    df.columns = [clean_col(c) for c in df.columns]
                    
                    # Filter for Silver, Copper, Platinum
                    for key, meta in TARGET_METALS.items():
                        pat = meta["market_pattern"]
                        code = meta["contract_code"]
                        
                        mask = df["Market_and_Exchange_Names"].astype(str).str.contains(key, case=False, na=False)
                        if "CFTC_Contract_Market_Code" in df.columns:
                            mask = mask | (df["CFTC_Contract_Market_Code"].astype(str).str.strip() == code)
                            
                        sub = df[mask].copy()
                        if not sub.empty:
                            sub["metal"] = meta["metal"]
                            sub["report_type"] = "Disaggregated_Futures_Only"
                            sub["source_edition"] = f"CFTC_DISAGG_{year}"
                            records.append(sub)
    if records:
        return pd.concat(records, ignore_index=True)
    return pd.DataFrame()

def main():
    print("=== Extracting CFTC Disaggregated COT Positioning for Silver, Copper, Platinum ===", flush=True)
    dfs = []
    zip_files = sorted(RAW_DIR.glob("cftc__cot_disaggregated_futures__*__original.zip"))
    
    for zp in zip_files:
        yr = zp.stem.split("__")[2]
        df_yr = process_disaggregated_zip(zp, yr)
        if not df_yr.empty:
            print(f"  Extracted {len(df_yr)} positioning records for {yr}", flush=True)
            dfs.append(df_yr)
            
    if dfs:
        df_combined = pd.concat(dfs, ignore_index=True)
        # Sort and clean
        df_combined["Report_Date_as_YYYY-MM-DD"] = pd.to_datetime(df_combined["Report_Date_as_YYYY-MM-DD"])
        df_combined = df_combined.sort_values(by=["metal", "Report_Date_as_YYYY-MM-DD"])
        
        # Calculate Net Positions
        if "M_Money_Positions_Long_All" in df_combined.columns and "M_Money_Positions_Short_All" in df_combined.columns:
            df_combined["managed_money_net"] = df_combined["M_Money_Positions_Long_All"] - df_combined["M_Money_Positions_Short_All"]
        if "Prod_Merc_Positions_Long_All" in df_combined.columns and "Prod_Merc_Positions_Short_All" in df_combined.columns:
            df_combined["commercial_producer_net"] = df_combined["Prod_Merc_Positions_Long_All"] - df_combined["Prod_Merc_Positions_Short_All"]
            
        out_csv = OUT_DIR / "cftc_cot_positioning_extracted.csv"
        df_combined.to_csv(out_csv, index=False, encoding="utf-8")
        print(f"\n[SUCCESS] Extracted {len(df_combined)} COT positioning rows -> {out_csv}", flush=True)
        
        for m in ["Silver", "Copper", "Platinum"]:
            cnt = len(df_combined[df_combined["metal"] == m])
            dates = df_combined[df_combined["metal"] == m]["Report_Date_as_YYYY-MM-DD"]
            if not dates.empty:
                print(f"  {m}: {cnt} weekly reports from {dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}", flush=True)
        return df_combined
    else:
        print("[WARNING] No COT records extracted.", flush=True)
        return pd.DataFrame()

if __name__ == "__main__":
    main()
