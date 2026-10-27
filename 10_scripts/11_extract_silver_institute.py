import sys
from pathlib import Path
import pdfplumber
import pandas as pd
import re

sys.path.append(str(Path(__file__).parent))
from download_utils import BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "silver"
OUT_DIR = BASE_DIR / "03_extracted"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EDITIONS = [
    {"year": 2024, "pub_date": "2024-04-17", "file": "silver__silver_institute__world_silver_survey__2024__original.pdf"},
    {"year": 2023, "pub_date": "2023-04-19", "file": "silver__silver_institute__world_silver_survey__2023__original.pdf"},
    {"year": 2022, "pub_date": "2022-04-20", "file": "silver__silver_institute__world_silver_survey__2022__original.pdf"},
    {"year": 2021, "pub_date": "2021-04-22", "file": "silver__silver_institute__world_silver_survey__2021__original.pdf"},
    {"year": 2020, "pub_date": "2020-04-15", "file": "silver__silver_institute__world_silver_survey__2020__original.pdf"},
    {"year": 2018, "pub_date": "2018-04-12", "file": "silver__silver_institute__world_silver_survey__2018__original.pdf"},
    {"year": 2015, "pub_date": "2015-05-06", "file": "silver__silver_institute__world_silver_survey__2015__original.pdf"}
]

SILVER_METRIC_MAP = {
    "mine production": "mine_production",
    "recycling": "recycling_supply",
    "net hedging supply": "net_hedging_supply",
    "net official sector": "net_official_sector_supply",
    "total supply": "total_supply",
    "industrial": "industrial_demand",
    "electrical & electronics": "demand_electrical_electronics",
    "photovoltaics": "demand_photovoltaics",
    "brazing alloys": "demand_brazing_alloys",
    "other industrial": "demand_other_industrial",
    "photography": "demand_photography",
    "jewelry": "jewelry_demand",
    "jewellery": "jewelry_demand",
    "silverware": "silverware_demand",
    "physical investment": "physical_investment_demand",
    "total demand": "total_physical_demand",
    "market balance": "market_balance_reported",
    "physical balance": "market_balance_reported",
    "net balance": "market_balance_reported",
    "market deficit": "market_balance_reported"
}

def clean_val(v):
    if v is None:
        return None
    s = str(v).replace(",", "").replace("%", "").strip()
    if s.endswith("-"):
        s = "-" + s[:-1]
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except:
        return None

def extract_from_survey(pdf_path, edition_year, pub_date):
    print(f"Scanning World Silver Survey {edition_year} ({pdf_path.name})...", flush=True)
    observations = []
    
    with pdfplumber.open(pdf_path) as pdf:
        target_page_idx = None
        # Fast text scan over first 25 pages
        for p_idx in range(min(25, len(pdf.pages))):
            text = (pdf.pages[p_idx].extract_text() or "").lower()
            if "mine production" in text and "recycling" in text and "total supply" in text:
                target_page_idx = p_idx
                print(f"  Target Supply/Demand table identified on page {p_idx+1}", flush=True)
                break
                
        if target_page_idx is not None:
            page = pdf.pages[target_page_idx]
            tables = page.extract_tables()
            for t in tables:
                if not t or len(t) < 5:
                    continue
                header = [str(c).replace("\n", " ").strip() for c in t[0] if c is not None]
                year_cols = []
                for c_idx, h_text in enumerate(header):
                    match = re.search(r"\b(199\d|20[0-2]\d)\b", h_text)
                    if match:
                        yr = int(match.group(1))
                        is_forecast = "f" in h_text.lower() or "e" in h_text.lower()
                        year_cols.append((c_idx, yr, is_forecast))
                        
                if not year_cols and len(t) > 1:
                    header1 = [str(c).replace("\n", " ").strip() for c in t[1] if c is not None]
                    for c_idx, h_text in enumerate(header1):
                        match = re.search(r"\b(199\d|20[0-2]\d)\b", h_text)
                        if match:
                            yr = int(match.group(1))
                            is_forecast = "f" in h_text.lower() or "e" in h_text.lower()
                            year_cols.append((c_idx, yr, is_forecast))
                            
                if len(year_cols) >= 3:
                    for row in t:
                        if not row or not row[0]:
                            continue
                        raw_label = str(row[0]).replace("\n", " ").strip()
                        label_lower = raw_label.lower()
                        
                        matched_metric = None
                        for k, v in SILVER_METRIC_MAP.items():
                            if k in label_lower:
                                matched_metric = v
                                break
                                
                        if not matched_metric:
                            continue
                            
                        for c_idx, yr, is_fc in year_cols:
                            if c_idx < len(row):
                                val = clean_val(row[c_idx])
                                if val is not None:
                                    obs_id = f"OBS_AG_{matched_metric.upper()}_{yr}_WSS{edition_year}"
                                    observations.append({
                                        "observation_id": obs_id,
                                        "metal": "Silver",
                                        "metric": matched_metric,
                                        "metric_original": raw_label,
                                        "period_start": f"{yr}-01-01",
                                        "period_end": f"{yr}-12-31",
                                        "period_year": yr,
                                        "period_frequency": "Annual",
                                        "value_original": val,
                                        "unit_original": "Million ounces",
                                        "value_standardized": val,
                                        "unit_standardized": "Moz",
                                        "source_id": "SRC_SILVER_INSTITUTE_WSS",
                                        "source_edition": f"WSS_{edition_year}",
                                        "report_version": f"World Silver Survey {edition_year}",
                                        "publication_date": pub_date,
                                        "available_at": pub_date,
                                        "page_number": target_page_idx + 1,
                                        "table_name": "World Silver Supply and Demand",
                                        "status": "Forecast" if is_fc else "Actual",
                                        "is_forecast": is_fc,
                                        "extraction_method": "pdfplumber_table_parser",
                                        "validation_status": "Verified"
                                    })
    return observations

def main():
    all_obs = []
    for item in EDITIONS:
        p = RAW_DIR / item["file"]
        if p.exists():
            obs = extract_from_survey(p, item["year"], item["pub_date"])
            all_obs.extend(obs)
            print(f"  -> Extracted {len(obs)} records from WSS {item['year']}", flush=True)
            
    df_all = pd.DataFrame(all_obs)
    if not df_all.empty:
        df_all = df_all.drop_duplicates(subset=["observation_id"])
        out_csv = OUT_DIR / "silver_institute_extracted.csv"
        df_all.to_csv(out_csv, index=False, encoding="utf-8")
        print(f"\n[SUCCESS] Total extracted Silver Institute observations: {len(df_all)} -> {out_csv}", flush=True)
    else:
        print("[WARNING] No Silver Institute observations extracted.", flush=True)
    return df_all

if __name__ == "__main__":
    main()
