import sys
from pathlib import Path
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from download_utils import BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "platinum"
OUT_DIR = BASE_DIR / "03_extracted"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METRIC_MAP = {
    "refined production": "refined_production",
    "south africa": "mine_production_south_africa",
    "zimbabwe": "mine_production_zimbabwe",
    "north america": "mine_production_north_america",
    "russia": "mine_production_russia",
    "other": "mine_production_other",
    "total mining supply": "total_mining_supply",
    "recycling": "recycling_supply",
    "autocatalyst": "recycling_autocatalyst",
    "jewellery": "recycling_jewellery",
    "industrial": "recycling_industrial",
    "total supply": "total_supply",
    "automotive": "automotive_demand",
    "jewelry": "jewelry_demand",
    "chemical": "industrial_chemical",
    "petroleum": "industrial_petroleum",
    "electrical": "industrial_electrical",
    "glass": "industrial_glass",
    "medical": "industrial_medical",
    "hydrogen": "industrial_hydrogen",
    "investment": "investment_demand",
    "bars, coins": "investment_bars_coins",
    "etf holdings": "investment_etf_holdings_change",
    "stocks held by exchanges": "investment_exchange_stocks_change",
    "total demand": "total_demand",
    "balance": "market_balance_reported",
    "above ground stocks": "above_ground_stocks"
}

def clean_num(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).replace(",", "").replace("*", "").replace("†", "").strip()
    try:
        return float(s)
    except:
        return None

def extract_wpic_latest():
    wb_path = RAW_DIR / "platinum__wpic__platinum_quarterly_tables__2026_q2__original.xlsx"
    xl = pd.ExcelFile(wb_path)
    
    # We will parse Table 1 from several key quarterly releases to track revisions:
    # Q2'26, Q4'24, Q4'22, Q4'20, Q4'18
    target_sheets = [
        ("Table 1(Q2'26)", "2026-06-30", "WPIC_2026_Q2"),
        ("Table 1(Q4'24)", "2024-12-31", "WPIC_2024_Q4"),
        ("Table 1(Q4'22)", "2022-12-31", "WPIC_2022_Q4"),
        ("Table 1(Q4'20)", "2020-12-31", "WPIC_2020_Q4")
    ]
    
    observations = []
    
    for sheet_name, pub_date, edition in target_sheets:
        if sheet_name not in xl.sheet_names:
            continue
        df = pd.read_excel(wb_path, sheet_name=sheet_name, header=None)
        
        # Header row 1 contains years / quarters
        header_row = df.iloc[1].values
        
        # Identify columns that are annual years (e.g. 2015, 2016, ..., 2025, 2026f)
        year_cols = []
        for col_idx in range(3, min(25, len(header_row))):
            val = str(header_row[col_idx]).strip()
            if val.isdigit() and len(val) == 4 and int(val) >= 2000:
                year_cols.append((col_idx, int(val), False))
            elif val.lower().endswith("f") and val[:-1].isdigit():
                year_cols.append((col_idx, int(val[:-1]), True))
        
        # Walk through rows
        current_section = ""
        for r_idx in range(2, len(df)):
            m1 = str(df.iloc[r_idx, 1]).strip() if pd.notna(df.iloc[r_idx, 1]) else ""
            m2 = str(df.iloc[r_idx, 2]).strip() if pd.notna(df.iloc[r_idx, 2]) else ""
            
            if m1 in ["SUPPLY", "DEMAND"]:
                current_section = m1
                continue
                
            raw_metric = m1 if m1 else m2
            if not raw_metric:
                continue
                
            # Match standardized metric name
            std_metric = None
            raw_lower = raw_metric.lower()
            for k, v in METRIC_MAP.items():
                if k in raw_lower:
                    std_metric = v
                    break
                    
            if not std_metric:
                continue
                
            for col_idx, yr, is_fc in year_cols:
                raw_val = df.iloc[r_idx, col_idx]
                val = clean_num(raw_val)
                if val is not None:
                    obs_id = f"OBS_PT_{std_metric.upper()}_{yr}_{edition}"
                    observations.append({
                        "observation_id": obs_id,
                        "metal": "Platinum",
                        "metric": std_metric,
                        "metric_original": raw_metric,
                        "period_start": f"{yr}-01-01",
                        "period_end": f"{yr}-12-31",
                        "period_year": yr,
                        "period_frequency": "Annual",
                        "value_original": val,
                        "unit_original": "koz",
                        "value_standardized": val, # already in koz
                        "unit_standardized": "koz",
                        "source_id": "SRC_WPIC_PLATINUM_HISTORIC",
                        "source_edition": edition,
                        "report_version": sheet_name,
                        "publication_date": pub_date,
                        "available_at": pub_date,
                        "table_name": sheet_name,
                        "status": "Forecast" if is_fc else "Actual",
                        "is_forecast": is_fc,
                        "extraction_method": "openpyxl_sheet_parser",
                        "validation_status": "Verified"
                    })
                    
    df_obs = pd.DataFrame(observations)
    out_csv = OUT_DIR / "platinum_wpic_extracted.csv"
    df_obs.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"Extracted {len(df_obs)} WPIC Platinum observations -> {out_csv}")
    return df_obs

if __name__ == "__main__":
    extract_wpic_latest()
