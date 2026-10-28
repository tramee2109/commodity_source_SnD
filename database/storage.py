"""
Unified Storage Sink for SQLite and Parquet Lakehouse.
Provides idempotent persistence with primary key de-duplication.
"""

import sqlite3
import logging
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from config.settings import DB_PATH
from core.models import MarketBar, PositioningRecord

logger = logging.getLogger(__name__)

class StorageSink:
    """Manages relational SQLite tables and Parquet columnar files."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self):
        """Create tables and performance indexes."""
        conn = self._get_connection()
        cur = conn.cursor()
        
        # 1. Market Bars (OHLCV + Volume + OI)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fact_market_bar (
                bar_id TEXT PRIMARY KEY,
                commodity_id TEXT NOT NULL,
                ticker TEXT NOT NULL,
                time_bar TIMESTAMP NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL DEFAULT 0,
                open_interest REAL DEFAULT 0,
                frequency TEXT DEFAULT '1d',
                source_id TEXT NOT NULL,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_bar_ticker_time ON fact_market_bar(ticker, time_bar);")

        # 2. Institutional Money Flow (CFTC COT)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fact_positioning (
                record_id TEXT PRIMARY KEY,
                market_code TEXT NOT NULL,
                commodity_id TEXT NOT NULL,
                report_date TIMESTAMP NOT NULL,
                publication_time TIMESTAMP NOT NULL,
                managed_money_long REAL NOT NULL,
                managed_money_short REAL NOT NULL,
                managed_money_net REAL NOT NULL,
                managed_money_pct_oi REAL NOT NULL,
                total_open_interest REAL NOT NULL,
                source_id TEXT DEFAULT 'SRC_CFTC',
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pos_market_date ON fact_positioning(market_code, report_date);")

        conn.commit()
        conn.close()

    def save_market_bars(self, bars: List[MarketBar]) -> int:
        """
        Idempotent insertion into SQLite fact_market_bar.
        Uses INSERT OR REPLACE to prevent duplicate bars.
        """
        if not bars:
            return 0
        conn = self._get_connection()
        cur = conn.cursor()
        rows = [
            (
                b.bar_id, b.commodity_id, b.ticker, b.time_bar.isoformat(),
                b.open, b.high, b.low, b.close, b.volume, b.open_interest,
                b.frequency, b.source_id
            )
            for b in bars
        ]
        cur.executemany("""
            INSERT OR REPLACE INTO fact_market_bar (
                bar_id, commodity_id, ticker, time_bar, open, high, low, close,
                volume, open_interest, frequency, source_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()
        conn.close()
        return len(rows)

    def save_positioning(self, records: List[PositioningRecord]) -> int:
        """
        Idempotent insertion into SQLite fact_positioning.
        Uses INSERT OR REPLACE.
        """
        if not records:
            return 0
        conn = self._get_connection()
        cur = conn.cursor()
        rows = [
            (
                r.record_id, r.market_code, r.commodity_id, r.report_date.isoformat(),
                r.publication_time.isoformat(), r.managed_money_long, r.managed_money_short,
                r.managed_money_net, r.managed_money_pct_oi, r.total_open_interest,
                r.source_id
            )
            for r in records
        ]
        cur.executemany("""
            INSERT OR REPLACE INTO fact_positioning (
                record_id, market_code, commodity_id, report_date, publication_time,
                managed_money_long, managed_money_short, managed_money_net,
                managed_money_pct_oi, total_open_interest, source_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()
        conn.close()
        return len(rows)

    @staticmethod
    def update_parquet_dataset(parquet_path: Path, new_df: pd.DataFrame, dedup_keys: List[str]):
        """
        Append new records into Parquet and de-duplicate keeping latest vintage.
        """
        if new_df.empty:
            return
        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        if parquet_path.exists():
            try:
                existing_df = pd.read_parquet(parquet_path)
                combined = pd.concat([existing_df, new_df], ignore_index=True)
                combined = combined.drop_duplicates(subset=dedup_keys, keep='last')
                # sort by primary date column if present
                for d_col in ['time_bar', 'report_date', 'date']:
                    if d_col in combined.columns:
                        combined = combined.sort_values(d_col)
                        break
                pq.write_table(pa.Table.from_pandas(combined), parquet_path, compression="snappy")
                return
            except Exception as e:
                logger.warning(f"Error merging parquet {parquet_path}: {e}. Overwriting with fresh batch.")
        pq.write_table(pa.Table.from_pandas(new_df), parquet_path, compression="snappy")
