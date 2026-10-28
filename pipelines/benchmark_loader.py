"""
Benchmark Metals, Equities & FX Incremental Ingestion Pipeline.
Targets:
- Futures: HG=F (Copper), PL=F (Platinum), SI=F (Silver), GC=F (Gold)
- Leading Miners: FCX, PAAS, SBSW, SIL
- Macro Currency: USDCNY=X

Features:
- Checkpoint Watermark: Only downloads dates newer than latest stored bar.
- Automatic Deduplication: Prevents double-counting in SQLite & Parquet.
- Resumable: Each ticker commits its state independently.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import yfinance as yf
import pandas as pd

from config.settings import BENCHMARK_TARGETS, LAKE_BENCHMARKS_DIR
from core.models import MarketBar
from core.checkpoint import CheckpointManager
from database.storage import StorageSink

logger = logging.getLogger(__name__)

PIPELINE_ID = "pipeline_benchmark_metals"

def run_benchmark_pipeline(force_full: bool = False) -> Dict[str, Any]:
    """Execute incremental benchmark ingestion."""
    print("\n-------------------------------------------------------")
    print("[2/3] INGESTING BENCHMARK FUTURES, MINERS & FX (INCREMENTAL)")
    print("-------------------------------------------------------")

    chk_mgr = CheckpointManager()
    storage = StorageSink()
    today = datetime.utcnow().date()
    results = {}

    for ticker, meta in BENCHMARK_TARGETS.items():
        watermark = chk_mgr.get_watermark(PIPELINE_ID, ticker)

        # Determine start date
        if force_full or watermark is None:
            start_date = (today - timedelta(days=5 * 365)).strftime('%Y-%m-%d')
            print(f"\n[-] {ticker:<10} | {meta['name']} -> Initial full load (5 years)...")
        else:
            watermark_date = watermark.date()
            if watermark_date >= today - timedelta(days=1):
                print(f"[-] {ticker:<10} | [SKIP] Already up to date (Watermark: {watermark_date}).")
                results[ticker] = {'status': 'SKIPPED', 'bars': 0, 'watermark': str(watermark_date)}
                continue
            start_date = (watermark_date + timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"\n[-] {ticker:<10} | Incremental sync from {start_date} to today...")

        try:
            df = yf.download(ticker, start=start_date, progress=False, auto_adjust=False)
            if df.empty:
                print(f"  [OK] No new trading sessions for {ticker}.")
                chk_mgr.update_checkpoint(PIPELINE_ID, ticker, watermark or datetime.utcnow(), records_synced=0, status="SUCCESS")
                results[ticker] = {'status': 'NO_NEW_DATA', 'bars': 0}
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.columns = [c.lower() for c in df.columns]
            df = df.reset_index()
            date_col = [c for c in df.columns if 'date' in c.lower()][0]
            df['datetime'] = pd.to_datetime(df[date_col])
            df = df.dropna(subset=['close']).sort_values('datetime')

            bars = []
            parquet_rows = []

            for _, r in df.iterrows():
                dt = r['datetime'].to_pydatetime()
                dt_str = dt.strftime('%Y-%m-%d')
                bar_id = f"BAR_{ticker.replace('=', '_')}_{dt_str}"

                bars.append(MarketBar(
                    bar_id=bar_id,
                    commodity_id=meta['commodity_id'],
                    ticker=ticker,
                    time_bar=dt,
                    open=float(r['open']),
                    high=float(r['high']),
                    low=float(r['low']),
                    close=float(r['close']),
                    volume=float(r.get('volume', 0.0)),
                    open_interest=0.0,
                    frequency="1d",
                    source_id="YFINANCE"
                ))

                parquet_rows.append({
                    'bar_id': bar_id,
                    'ticker': ticker,
                    'time_bar': dt,
                    'open': float(r['open']),
                    'high': float(r['high']),
                    'low': float(r['low']),
                    'close': float(r['close']),
                    'volume': float(r.get('volume', 0.0))
                })

            if bars:
                # 1. SQL Save
                storage.save_market_bars(bars)

                # 2. Parquet Save
                clean_sym = ticker.replace('=', '_').replace('^', '').lower()
                parquet_file = LAKE_BENCHMARKS_DIR / f"{clean_sym}.parquet"
                storage.update_parquet_dataset(parquet_file, pd.DataFrame(parquet_rows), dedup_keys=['ticker', 'time_bar'])

                # 3. Checkpoint Save
                latest_dt = df['datetime'].iloc[-1].to_pydatetime()
                chk_mgr.update_checkpoint(PIPELINE_ID, ticker, latest_dt, records_synced=len(bars), status="SUCCESS")
                print(f"  [+] Ingested {len(bars)} bars. New Watermark: {latest_dt.strftime('%Y-%m-%d')}")
                results[ticker] = {'status': 'SUCCESS', 'bars': len(bars), 'watermark': latest_dt.strftime('%Y-%m-%d')}

        except Exception as e:
            logger.error(f"Error fetching {ticker}: {e}")
            chk_mgr.update_checkpoint(PIPELINE_ID, ticker, watermark, status="FAILED", error_message=str(e))
            print(f"  [!] Error syncing {ticker}: {e}. State preserved for retry.")
            results[ticker] = {'status': 'FAILED', 'error': str(e)}

    return results
