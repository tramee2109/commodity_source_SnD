"""
Checkpoint & Watermark State Manager for ACM Nano Metals Platform.
Tracks last successful ingestion timestamp per pipeline and entity.
Enables fault-tolerance, resumability, and avoids redundant network calls.
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from pathlib import Path

from config.settings import DB_PATH

logger = logging.getLogger(__name__)

class CheckpointManager:
    """Manages ingestion state and watermarks in embedded SQLite database."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_checkpoint_table()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_checkpoint_table(self):
        """Create checkpoint table if missing."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sync_checkpoint (
                pipeline_id TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                last_sync_time TIMESTAMP NOT NULL,
                last_data_timestamp TIMESTAMP,
                records_synced INTEGER DEFAULT 0,
                status TEXT DEFAULT 'SUCCESS',
                error_message TEXT,
                PRIMARY KEY (pipeline_id, entity_id)
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chk_pipe ON sync_checkpoint(pipeline_id);")
        conn.commit()
        conn.close()

    def get_watermark(self, pipeline_id: str, entity_id: str) -> Optional[datetime]:
        """
        Fetch the latest data timestamp successfully synced.
        Returns None if this is an initial sync.
        """
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT last_data_timestamp 
            FROM sync_checkpoint 
            WHERE pipeline_id = ? AND entity_id = ? AND status = 'SUCCESS'
        """, (pipeline_id, entity_id))
        row = cur.fetchone()
        conn.close()

        if row and row[0]:
            try:
                ts_str = str(row[0]).replace('Z', '')
                if 'T' in ts_str:
                    return datetime.fromisoformat(ts_str.split('+')[0])
                else:
                    return datetime.strptime(ts_str.split()[0], '%Y-%m-%d')
            except Exception as e:
                logger.warning(f"Error parsing watermark '{row[0]}': {e}")
                return None
        return None

    def update_checkpoint(
        self,
        pipeline_id: str,
        entity_id: str,
        last_data_timestamp: Optional[datetime],
        records_synced: int = 0,
        status: str = "SUCCESS",
        error_message: Optional[str] = None
    ):
        """Record or update a checkpoint for a given entity."""
        conn = self._get_connection()
        cur = conn.cursor()
        now_str = datetime.utcnow().isoformat()
        data_ts_str = last_data_timestamp.isoformat() if last_data_timestamp else None

        cur.execute("""
            INSERT INTO sync_checkpoint (
                pipeline_id, entity_id, last_sync_time, last_data_timestamp,
                records_synced, status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(pipeline_id, entity_id) DO UPDATE SET
                last_sync_time = excluded.last_sync_time,
                last_data_timestamp = COALESCE(excluded.last_data_timestamp, sync_checkpoint.last_data_timestamp),
                records_synced = excluded.records_synced,
                status = excluded.status,
                error_message = excluded.error_message
        """, (pipeline_id, entity_id, now_str, data_ts_str, records_synced, status, error_message))

        conn.commit()
        conn.close()

    def get_all_checkpoints(self, pipeline_id: Optional[str] = None) -> List[Tuple]:
        """Retrieve full checkpoint report for summary dashboard."""
        conn = self._get_connection()
        cur = conn.cursor()
        if pipeline_id:
            cur.execute("""
                SELECT pipeline_id, entity_id, last_sync_time, last_data_timestamp, records_synced, status, error_message
                FROM sync_checkpoint WHERE pipeline_id = ? ORDER BY entity_id
            """, (pipeline_id,))
        else:
            cur.execute("""
                SELECT pipeline_id, entity_id, last_sync_time, last_data_timestamp, records_synced, status, error_message
                FROM sync_checkpoint ORDER BY pipeline_id, entity_id
            """)
        rows = cur.fetchall()
        conn.close()
        return rows
