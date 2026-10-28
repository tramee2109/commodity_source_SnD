"""
CFTC Disaggregated Commitments of Traders (COT) Metals Pipeline.
Tracks institutional money flow (Managed Money Long/Short/Net):
- Copper (COMEX)
- Silver (COMEX)
- Platinum (NYMEX)
- Gold (COMEX)

Features:
- Bypasses Cloudflare block via curl subprocess with Chrome User-Agent.
- Checkpoint Watermark: Ingests only new weekly reports published since last run.
- Zero Duplication: Primary key idempotency in SQLite & Parquet.
"""

import io
import zipfile
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import pandas as pd

from config.settings import CFTC_METALS, LAKE_COT_DIR
from core.models import PositioningRecord
from core.checkpoint import CheckpointManager
from database.storage import StorageSink

logger = logging.getLogger(__name__)

PIPELINE_ID = "pipeline_cftc_metals"

def download_cftc_archive(year: int) -> Optional[bytes]:
    """Download CFTC zip file using curl subprocess with Chrome User-Agent."""
    url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    cmd = ["curl.exe", "-s", "-L", "-A", ua, url]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=30)
        if res.returncode == 0 and len(res.stdout) > 50000:
            return res.stdout
    except Exception as e:
        logger.error(f"Curl error downloading {url}: {e}")
    return None

def run_cot_pipeline() -> Dict[str, Any]:
    """Execute CFTC COT metals ingestion."""
    print("\n-------------------------------------------------------")
    print("[3/3] INGESTING CFTC METALS POSITIONING (INCREMENTAL)")
    print("-------------------------------------------------------")

    chk_mgr = CheckpointManager()
    storage = StorageSink()
    results = {}

    current_yr = datetime.utcnow().year
    years_to_try = [current_yr, current_yr - 1, 2024]
    zip_bytes = None
    selected_yr = None

    for yr in years_to_try:
        print(f">> Fetching CFTC reports for year {yr}...")
        zip_bytes = download_cftc_archive(yr)
        if zip_bytes:
            selected_yr = yr
            print(f"  [+] Downloaded archive for {yr} ({len(zip_bytes)} bytes).")
            break

    if not zip_bytes:
        print("[!] Could not download CFTC archive for any recent year.")
        return {'status': 'FAILED', 'error': 'Download failure'}

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            csv_name = [n for n in z.namelist() if n.endswith('.txt') or n.endswith('.csv')][0]
            raw_df = pd.read_csv(z.open(csv_name), low_memory=False)
    except Exception as e:
        print(f"[!] Error unpacking archive: {e}")
        return {'status': 'FAILED', 'error': str(e)}

    raw_df.columns = [c.strip() for c in raw_df.columns]
    raw_df['Market_and_Exchange_Names'] = raw_df['Market_and_Exchange_Names'].str.strip()

    for market_name, meta in CFTC_METALS.items():
        code = meta['code']
        watermark = chk_mgr.get_watermark(PIPELINE_ID, code)
        print(f"\n[-] Inspecting CFTC {code} (Watermark: {watermark.strftime('%Y-%m-%d') if watermark else 'None'})...")

        sub_df = raw_df[raw_df['Market_and_Exchange_Names'] == market_name].copy()
        if sub_df.empty:
            print(f"  [!] Market '{market_name}' not found in CFTC file.")
            results[code] = {'status': 'NOT_FOUND', 'records': 0}
            continue

        date_col = 'Report_Date_as_YYYY-MM-DD' if 'Report_Date_as_YYYY-MM-DD' in sub_df.columns else 'As_of_Date_In_Form_YYMMDD'
        sub_df['date'] = pd.to_datetime(sub_df[date_col])
        sub_df = sub_df.sort_values('date')

        # Filter: strictly newer than watermark
        if watermark is not None:
            new_df = sub_df[sub_df['date'] > watermark].copy()
        else:
            new_df = sub_df.copy()

        if new_df.empty:
            print(f"  [SKIP] {code} COT positioning is already up to date.")
            results[code] = {'status': 'SKIPPED', 'records': 0, 'watermark': watermark.strftime('%Y-%m-%d')}
            continue

        # Compute Net Positioning
        new_df['managed_money_long'] = pd.to_numeric(new_df['M_Money_Positions_Long_All'], errors='coerce')
        new_df['managed_money_short'] = pd.to_numeric(new_df['M_Money_Positions_Short_All'], errors='coerce')
        new_df['managed_money_net'] = new_df['managed_money_long'] - new_df['managed_money_short']
        new_df['total_oi'] = pd.to_numeric(new_df['Open_Interest_All'], errors='coerce')
        new_df['managed_money_pct_oi'] = (new_df['managed_money_net'] / new_df['total_oi'] * 100).round(2)
        new_df['publication_time'] = new_df['date'] + timedelta(days=3, hours=15, minutes=30)

        records = []
        parquet_rows = []

        for _, r in new_df.iterrows():
            dt = r['date'].to_pydatetime()
            dt_str = dt.strftime('%Y-%m-%d')
            rec_id = f"COT_{code}_{dt_str}"

            records.append(PositioningRecord(
                record_id=rec_id,
                market_code=code,
                commodity_id=meta['comm_id'],
                report_date=dt,
                publication_time=r['publication_time'].to_pydatetime(),
                managed_money_long=float(r['managed_money_long']),
                managed_money_short=float(r['managed_money_short']),
                managed_money_net=float(r['managed_money_net']),
                managed_money_pct_oi=float(r['managed_money_pct_oi']),
                total_open_interest=float(r['total_oi']),
                source_id="SRC_CFTC"
            ))

            parquet_rows.append({
                'record_id': rec_id,
                'market_code': code,
                'report_date': dt,
                'publication_time': r['publication_time'].to_pydatetime(),
                'managed_money_long': float(r['managed_money_long']),
                'managed_money_short': float(r['managed_money_short']),
                'managed_money_net': float(r['managed_money_net']),
                'managed_money_pct_oi': float(r['managed_money_pct_oi']),
                'total_open_interest': float(r['total_oi'])
            })

        # Save to SQLite
        storage.save_positioning(records)

        # Save to Parquet
        parquet_file = LAKE_COT_DIR / f"cot_{code.lower()}.parquet"
        storage.update_parquet_dataset(parquet_file, pd.DataFrame(parquet_rows), dedup_keys=['market_code', 'report_date'])

        # Update Checkpoint
        latest_dt = new_df['date'].iloc[-1].to_pydatetime()
        chk_mgr.update_checkpoint(PIPELINE_ID, code, latest_dt, records_synced=len(records), status="SUCCESS")
        print(f"  [+] Ingested {len(records)} weekly COT reports. New Watermark: {latest_dt.strftime('%Y-%m-%d')}")
        results[code] = {'status': 'SUCCESS', 'records': len(records), 'watermark': latest_dt.strftime('%Y-%m-%d')}

    return results
