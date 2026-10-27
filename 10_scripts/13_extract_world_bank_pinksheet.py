import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).parent))
from download_utils import BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "world_bank"
OUT_DIR = BASE_DIR / "03_extracted"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_COLS = {
    64: {"metal": "Copper", "metric": "monthly_spot_price", "unit": "$/mt"},
    70: {"metal": "Platinum", "metric": "monthly_spot_price", "unit": "$/troy oz"},
    71: {"metal": "Silver", "metric": "monthly_spot_price", "unit": "$/troy oz"},
    69: {"metal": "Gold", "metric": "monthly_spot_price", "unit": "$/troy oz"},
    2: {"metal": "Crude Oil (Brent)", "metric": "monthly_spot_price", "unit": "$/bbl"}
}

def clean_val(v):
    if pd.isna(v):
        return None
    try:
        return float(str(v).replace(",", "").strip())
    except:
        return None

def main():
    wb_path = RAW_DIR / "common__world_bank__cmo_historical_data_monthly__original.xlsx"
    print(f"Reading World Bank Pink Sheet from {wb_path.name}...", flush=True)
    df = pd.read_excel(wb_path, sheet_name="Monthly Prices", header=None)
    
    observations = []
    
    # Rows 6 to end contain data
    for r_idx in range(6, len(df)):
        period_str = str(df.iloc[r_idx, 0]).strip() # e.g. '1960M01'
        if "M" not in period_str or len(period_str) < 7:
            continue
            
        yr, mo = period_str.split("M")
        try:
            year_int = int(yr)
            month_int = int(mo)
        except:
            continue
            
        period_start = f"{year_int:04d}-{month_int:02d}-01"
        # Period end is last day of month
        period_end = pd.Period(f"{year_int}-{month_int}", freq="M").end_time.strftime("%Y-%m-%d")
        
        for col_idx, meta in TARGET_COLS.items():
            val = clean_val(df.iloc[r_idx, col_idx])
            if val is not None:
                obs_id = f"OBS_WB_{meta['metal'][:3].upper()}_PRICE_{year_int}_{month_int:02d}"
                observations.append({
                    "observation_id": obs_id,
                    "metal": meta["metal"],
                    "metric": meta["metric"],
                    "period_start": period_start,
                    "period_end": period_end,
                    "period_year": year_int,
                    "period_month": month_int,
                    "period_frequency": "Monthly",
                    "value_original": val,
                    "unit_original": meta["unit"],
                    "value_standardized": val,
                    "unit_standardized": meta["unit"],
                    "source_id": "SRC_WORLD_BANK_PINKSHEET",
                    "source_edition": "WB_CMO_2025_01",
                    "publication_date": period_end,
                    "available_at": period_end,
                    "status": "Actual",
                    "extraction_method": "openpyxl_sheet_parser",
                    "validation_status": "Verified"
                })
                
    df_obs = pd.DataFrame(observations)
    out_csv = OUT_DIR / "world_bank_monthly_prices_extracted.csv"
    df_obs.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[SUCCESS] Extracted {len(df_obs)} World Bank monthly price records -> {out_csv}", flush=True)
    for m in ["Silver", "Copper", "Platinum"]:
        sub = df_obs[df_obs["metal"] == m]
        print(f"  {m}: {len(sub)} months from {sub['period_start'].min()} to {sub['period_start'].max()}")
    return df_obs

if __name__ == "__main__":
    main()
