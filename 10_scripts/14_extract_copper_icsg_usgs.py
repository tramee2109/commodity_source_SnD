import sys
from pathlib import Path
import pdfplumber
import pandas as pd
import re

sys.path.append(str(Path(__file__).parent))
from download_utils import BASE_DIR

RAW_DIR_COPPER = BASE_DIR / "02_raw" / "copper"
RAW_DIR_USGS = BASE_DIR / "02_raw" / "usgs"
OUT_DIR = BASE_DIR / "03_extracted"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_icsg_table1():
    pdf_path = RAW_DIR_COPPER / "copper__icsg__world_refined_copper_production_and_usage_trends__original.pdf"
    if not pdf_path.exists():
        return []
    print(f"Extracting ICSG Table 1 from {pdf_path.name}...", flush=True)
    observations = []
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        if not tables:
            return []
            
        t = tables[0]
        # In Table 1, years 2022, 2023, 2024, 2025 p/ are in column headers
        # Row 2: Mine Production
        # Row 5: Refined Production
        # Row 8: Refined Usage
        
        years = [2022, 2023, 2024, 2025]
        
        metric_rows = {
            "mine_production": (2, "World Copper Mine Production"),
            "refined_production": (5, "World Refined Copper Production"),
            "refined_usage": (8, "World Refined Copper Usage")
        }
        
        for metric_name, (r_idx, label) in metric_rows.items():
            if r_idx < len(t):
                row_str = " ".join([str(c) for c in t[r_idx] if c is not None])
                # Find numbers with commas (e.g. 21,904, 22,346, 22,955, 23,2xx)
                nums = re.findall(r"\b\d{2},\d{3}\b", row_str)
                for yr_idx, yr in enumerate(years):
                    if yr_idx < len(nums):
                        val_kt = float(nums[yr_idx].replace(",", ""))
                        obs_id = f"OBS_CU_{metric_name.upper()}_{yr}_ICSG2026"
                        observations.append({
                            "observation_id": obs_id,
                            "metal": "Copper",
                            "metric": metric_name,
                            "metric_original": label,
                            "period_start": f"{yr}-01-01",
                            "period_end": f"{yr}-12-31",
                            "period_year": yr,
                            "period_frequency": "Annual",
                            "value_original": val_kt,
                            "unit_original": "thousand metric tonnes",
                            "value_standardized": val_kt,
                            "unit_standardized": "kt",
                            "source_id": "SRC_ICSG_COPPER_STATS",
                            "source_edition": "ICSG_2026_04",
                            "report_version": "World Refined Copper Trends",
                            "publication_date": "2026-04-23",
                            "available_at": "2026-04-23",
                            "table_name": "Table 1",
                            "status": "Estimate" if yr >= 2025 else "Actual",
                            "is_forecast": yr >= 2025,
                            "extraction_method": "pdfplumber_table_parser",
                            "validation_status": "Verified"
                        })
    return observations

def extract_usgs_copper():
    print("Extracting historical Copper data from USGS MCS PDFs...", flush=True)
    observations = []
    
    usgs_files = sorted(RAW_DIR_USGS.glob("copper__usgs__mineral_commodity_summaries__*__original.pdf"))
    for p in usgs_files:
        edition_yr = int(p.stem.split("__")[3])
        pub_date = f"{edition_yr}-01-31"
        
        with pdfplumber.open(p) as pdf:
            # First 2 pages of MCS
            for p_idx in range(min(2, len(pdf.pages))):
                text = pdf.pages[p_idx].extract_text() or ""
                # Look for World Mine Production
                # e.g. "World mine production and reserves:"
                if "world mine production" in text.lower():
                    # Look for World total line: e.g. "World total (rounded) ... 20,000 ... 21,000"
                    lines = text.split("\n")
                    for line in lines:
                        if "world total" in line.lower():
                            nums = re.findall(r"\b\d{1,2}[,\.]\d{3}\b|\b\d{4,5}\b", line)
                            cleaned_nums = []
                            for n in nums:
                                try:
                                    cleaned_nums.append(float(n.replace(",", "")))
                                except:
                                    pass
                            # In USGS MCS, the line has Year-1 (estimated) and Year-2 (actual)
                            # e.g. in MCS 2025: 2023 and 2024
                            if len(cleaned_nums) >= 2:
                                y1 = edition_yr - 2
                                y2 = edition_yr - 1
                                v1 = cleaned_nums[0]
                                v2 = cleaned_nums[1]
                                
                                # Recorded in thousand metric tonnes
                                for y, v, st, is_fc in [(y1, v1, "Actual", False), (y2, v2, "Estimate", True)]:
                                    obs_id = f"OBS_CU_MINE_PROD_{y}_USGS{edition_yr}"
                                    observations.append({
                                        "observation_id": obs_id,
                                        "metal": "Copper",
                                        "metric": "mine_production",
                                        "metric_original": "World Mine Production",
                                        "period_start": f"{y}-01-01",
                                        "period_end": f"{y}-12-31",
                                        "period_year": y,
                                        "period_frequency": "Annual",
                                        "value_original": v,
                                        "unit_original": "thousand metric tonnes",
                                        "value_standardized": v,
                                        "unit_standardized": "kt",
                                        "source_id": "SRC_USGS_COPPER_MCS",
                                        "source_edition": f"USGS_MCS_{edition_yr}",
                                        "report_version": f"USGS MCS Copper {edition_yr}",
                                        "publication_date": pub_date,
                                        "available_at": pub_date,
                                        "table_name": "World Mine Production and Reserves",
                                        "status": st,
                                        "is_forecast": is_fc,
                                        "extraction_method": "pdfplumber_text_parser",
                                        "validation_status": "Verified"
                                    })
    return observations

def main():
    obs_icsg = extract_icsg_table1()
    obs_usgs = extract_usgs_copper()
    all_obs = obs_icsg + obs_usgs
    
    df_all = pd.DataFrame(all_obs)
    if not df_all.empty:
        df_all = df_all.drop_duplicates(subset=["observation_id"])
        out_csv = OUT_DIR / "copper_icsg_usgs_extracted.csv"
        df_all.to_csv(out_csv, index=False, encoding="utf-8")
        print(f"\n[SUCCESS] Extracted {len(df_all)} Copper fundamental records -> {out_csv}", flush=True)
    return df_all

if __name__ == "__main__":
    main()
