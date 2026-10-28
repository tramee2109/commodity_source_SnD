"""
ACM (Asia Commodity Marketplace) Ingestion Pipeline.
Scrapes and parses official daily settlement data for:
- NCP: Nano Copper Derivatives (1,000 lbs)
- NPT: Nano Platinum Derivatives (5 oz)
- NSI: Nano Silver Derivatives (100 oz)

Features:
- Idempotent: Skips fetch if today's trade date is already processed.
- Deduplication: Unique primary key BAR_{ticker}_{trade_date}.
- Dual Persistence: Embedded SQLite + Partitioned Parquet Lakehouse.
"""

import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

import requests
from bs4 import BeautifulSoup
import pandas as pd

from config.settings import ACM_METALS, LAKE_ACM_DIR
from core.models import MarketBar
from core.checkpoint import CheckpointManager
from database.storage import StorageSink

logger = logging.getLogger(__name__)

PIPELINE_ID = "pipeline_acm_metals"

def parse_date_string(date_text: str) -> Optional[datetime]:
    """Parse text like 'October 15, 2026' to datetime."""
    try:
        return datetime.strptime(date_text.strip(), "%B %d, %Y")
    except Exception:
        return None

def scrape_acm_contract(url: str) -> Optional[Dict[str, Any]]:
    """Fetch and parse live HTML from ACM contract settlement tab."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            logger.warning(f"Failed to fetch ACM URL {url}: HTTP {resp.status_code}")
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Detect Trade Date
        date_elem = soup.find(string=re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'))
        trade_date = parse_date_string(date_elem.strip()) if date_elem else None

        rows = []
        settle_tab = soup.find('div', {'data-w-tab': 'Settlements'})
        if settle_tab:
            for grid in settle_tab.find_all('div', class_='grid-contract_data'):
                cells = [c.get_text(strip=True) for c in grid.find_all('div')]
                for i in range(0, len(cells), 9):
                    chunk = cells[i:i+9]
                    if len(chunk) == 9 and 'F-XACM' in chunk[0]:
                        rows.append(chunk)

        return {'trade_date': trade_date, 'rows': rows}
    except Exception as e:
        logger.error(f"Scraping error on {url}: {e}")
        return None

def run_acm_pipeline(force: bool = False) -> Dict[str, Any]:
    """Execute ACM ingestion with watermark skipping and deduplication."""
    print("\n-------------------------------------------------------")
    print("[1/3] INGESTING ACM NANO METALS (COPPER, PLATINUM, SILVER)")
    print("-------------------------------------------------------")

    chk_mgr = CheckpointManager()
    storage = StorageSink()
    results = {}

    for comm_id, cfg in ACM_METALS.items():
        code = cfg['code']
        name = cfg['name']
        print(f"\n[-] Checking ACM {name} ({code})...")

        watermark = chk_mgr.get_watermark(PIPELINE_ID, code)
        scraped = scrape_acm_contract(cfg['url'])

        if not scraped or not scraped['trade_date']:
            print(f"  [!] Failed to extract trade date for {code}. Skipping.")
            chk_mgr.update_checkpoint(PIPELINE_ID, code, watermark, status="FAILED", error_message="Trade date parsing failure")
            results[code] = {'status': 'FAILED', 'bars': 0}
            continue

        trade_date = scraped['trade_date']
        trade_date_str = trade_date.strftime('%Y-%m-%d')

        # Checkpoint check: Skip if already up to date
        if not force and watermark and watermark >= trade_date:
            print(f"  [SKIP] Already up to date (Watermark: {watermark.strftime('%Y-%m-%d')}). No duplicate fetch.")
            results[code] = {'status': 'SKIPPED', 'bars': 0, 'watermark': trade_date_str}
            continue

        rows = scraped['rows']
        if not rows:
            print(f"  [!] No contract rows found for {code} on {trade_date_str}.")
            results[code] = {'status': 'NO_DATA', 'bars': 0}
            continue

        bars = []
        parquet_rows = []

        for r in rows:
            ticker = r[0]
            try:
                open_p = float(r[1]) if r[1] not in ['-', ''] else float(r[6])
                high_p = float(r[2]) if r[2] not in ['-', ''] else float(r[6])
                low_p = float(r[3]) if r[3] not in ['-', ''] else float(r[6])
                last_p = float(r[4]) if r[4] not in ['-', ''] else float(r[6])
                settle_p = float(r[6]) if r[6] not in ['-', ''] else last_p
                volume = float(r[7]) if r[7] not in ['-', ''] else 0.0
                oi = float(r[8]) if r[8] not in ['-', ''] else 0.0
            except ValueError:
                continue

            bar_id = f"BAR_{ticker}_{trade_date_str}"
            bars.append(MarketBar(
                bar_id=bar_id,
                commodity_id=comm_id,
                ticker=ticker,
                time_bar=trade_date,
                open=open_p,
                high=high_p,
                low=low_p,
                close=settle_p,
                volume=volume,
                open_interest=oi,
                frequency="1d",
                source_id="ACM"
            ))

            parquet_rows.append({
                'bar_id': bar_id,
                'ticker': ticker,
                'time_bar': trade_date,
                'open': open_p,
                'high': high_p,
                'low': low_p,
                'close': settle_p,
                'volume': volume,
                'open_interest': oi
            })

        # Persist to SQLite
        storage.save_market_bars(bars)

        # Persist to Parquet
        parquet_file = LAKE_ACM_DIR / f"acm_{code.lower()}.parquet"
        storage.update_parquet_dataset(parquet_file, pd.DataFrame(parquet_rows), dedup_keys=['ticker', 'time_bar'])

        # Update Checkpoint
        chk_mgr.update_checkpoint(PIPELINE_ID, code, trade_date, records_synced=len(bars), status="SUCCESS")
        print(f"  [+] Ingested {len(bars)} contract months as of {trade_date_str}. Checkpoint saved.")
        results[code] = {'status': 'SUCCESS', 'bars': len(bars), 'watermark': trade_date_str}

    return results
