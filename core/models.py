"""
Canonical Data Models for ACM Nano Metals Platform.
Point-in-Time compliant with explicit timestamps.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class MarketBar:
    """Canonical market OHLCV bar with Open Interest."""
    bar_id: str
    commodity_id: str
    ticker: str
    time_bar: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    open_interest: float = 0.0
    frequency: str = "1d"
    source_id: str = "ACM"

@dataclass
class PositioningRecord:
    """CFTC Commitments of Traders (COT) institutional money flow observation."""
    record_id: str
    market_code: str
    commodity_id: str
    report_date: datetime
    publication_time: datetime
    managed_money_long: float
    managed_money_short: float
    managed_money_net: float
    managed_money_pct_oi: float
    total_open_interest: float
    source_id: str = "SRC_CFTC"
