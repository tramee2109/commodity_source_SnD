import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).parent))
from download_utils import BASE_DIR

EXT_DIR = BASE_DIR / "03_extracted"
NORM_DIR = BASE_DIR / "04_normalized"
VAL_DIR = BASE_DIR / "05_validated"
CAN_DIR = BASE_DIR / "06_canonical"

for d in [NORM_DIR, VAL_DIR, CAN_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def build_layer_a_observations():
    print("=== Building Layer A: Immutable Observations ===", flush=True)
    obs_files = [
        EXT_DIR / "platinum_wpic_extracted.csv",
        EXT_DIR / "silver_institute_extracted.csv",
        EXT_DIR / "copper_icsg_usgs_extracted.csv"
    ]
    
    dfs = []
    for f in obs_files:
        if f.exists():
            df = pd.read_csv(f)
            dfs.append(df)
            print(f"  Loaded {len(df)} records from {f.name}", flush=True)
            
    if not dfs:
        raise ValueError("No extracted fundamental observation files found!")
        
    df_obs = pd.concat(dfs, ignore_index=True)
    
    # Fill standard schema fields
    if "is_revision" not in df_obs.columns:
        df_obs["is_revision"] = False
    if "supersedes_observation_id" not in df_obs.columns:
        df_obs["supersedes_observation_id"] = None
    if "notes" not in df_obs.columns:
        df_obs["notes"] = ""
        
    # Sort chronologically by metal, metric, period_year, and publication_date
    df_obs = df_obs.sort_values(by=["metal", "metric", "period_year", "publication_date"])
    
    # Save Layer A
    out_csv = NORM_DIR / "fundamental_observations.csv"
    out_parquet = NORM_DIR / "fundamental_observations.parquet"
    df_obs.to_csv(out_csv, index=False, encoding="utf-8")
    df_obs.to_parquet(out_parquet, index=False)
    print(f"[LAYER A] Saved {len(df_obs)} immutable observations -> {out_csv} and {out_parquet}", flush=True)
    return df_obs

def detect_revisions_and_version_comparison(df_obs):
    print("\n=== Detecting Historical Revisions & Restatements ===", flush=True)
    revisions = []
    
    # Group by metal, metric, period_year, period_frequency
    grouped = df_obs.groupby(["metal", "metric", "period_year", "period_frequency"])
    
    for (metal, metric, yr, freq), group in grouped:
        if len(group) > 1:
            # Sort by publication_date
            g_sorted = group.sort_values(by="publication_date")
            for i in range(1, len(g_sorted)):
                prev_row = g_sorted.iloc[i-1]
                curr_row = g_sorted.iloc[i]
                
                val_prev = prev_row["value_standardized"]
                val_curr = curr_row["value_standardized"]
                
                diff_abs = round(val_curr - val_prev, 4)
                diff_pct = round((diff_abs / val_prev) * 100, 2) if val_prev != 0 else 0.0
                
                # If there's a difference, log revision
                if abs(diff_abs) > 1e-4:
                    revisions.append({
                        "metal": metal,
                        "metric": metric,
                        "period_year": yr,
                        "frequency": freq,
                        "edition_prior": prev_row["source_edition"],
                        "pub_date_prior": prev_row["publication_date"],
                        "value_prior": val_prev,
                        "status_prior": prev_row["status"],
                        "edition_revised": curr_row["source_edition"],
                        "pub_date_revised": curr_row["publication_date"],
                        "value_revised": val_curr,
                        "status_revised": curr_row["status"],
                        "diff_abs": diff_abs,
                        "diff_pct": diff_pct,
                        "unit": curr_row["unit_standardized"],
                        "observation_id_revised": curr_row["observation_id"],
                        "superseded_observation_id": prev_row["observation_id"]
                    })
                    
    df_rev = pd.DataFrame(revisions)
    out_csv = VAL_DIR / "version_comparison.csv"
    df_rev.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[REVISIONS] Detected {len(df_rev)} historical restatements/revisions -> {out_csv}", flush=True)
    
    # Print sample top revisions
    if not df_rev.empty:
        print("\nTop restatements detected:")
        for idx, r in df_rev.nlargest(5, "diff_abs").iterrows():
            print(f"  {r['metal']} {r['metric']} ({r['period_year']}): {r['value_prior']} -> {r['value_revised']} {r['unit']} (Diff: {r['diff_abs']}, {r['diff_pct']}%) [{r['edition_prior']} -> {r['edition_revised']}]")
    return df_rev

def build_layer_b_canonical(df_obs):
    print("\n=== Building Layer B: Latest Canonical Values ===", flush=True)
    # Filter for non-forecast if actual exists, else latest available
    # For each (metal, metric, period_year, period_frequency), pick latest publication_date
    df_sorted = df_obs.sort_values(by=["metal", "metric", "period_year", "publication_date", "is_forecast"], ascending=[True, True, True, True, False])
    
    # Pick last (most recent publication date)
    canonical = df_sorted.groupby(["metal", "metric", "period_year", "period_frequency"]).last().reset_index()
    
    out_csv = CAN_DIR / "fundamental_latest.csv"
    out_parquet = CAN_DIR / "fundamental_latest.parquet"
    canonical.to_csv(out_csv, index=False, encoding="utf-8")
    canonical.to_parquet(out_parquet, index=False)
    print(f"[LAYER B] Saved {len(canonical)} latest canonical series records -> {out_csv} and {out_parquet}", flush=True)
    
    for m in ["Silver", "Copper", "Platinum"]:
        sub = canonical[canonical["metal"] == m]
        metrics = sub["metric"].unique()
        yrs = sub["period_year"]
        print(f"  {m}: {len(sub)} records across {len(metrics)} metrics ({yrs.min()} to {yrs.max()})", flush=True)
    return canonical

def main():
    df_obs = build_layer_a_observations()
    df_rev = detect_revisions_and_version_comparison(df_obs)
    df_can = build_layer_b_canonical(df_obs)
    print("\nPhase 3 & 4 data layers built successfully!\n")

if __name__ == "__main__":
    main()
