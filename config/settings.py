"""
Project Configuration and Directory Setup for ACM Nano Metals Platform.
Self-contained, independent of any previous demo folders.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "timeseries.db"

# Lakehouse Storage
LAKEHOUSE_DIR = DATA_DIR / "lakehouse"
LAKE_ACM_DIR = LAKEHOUSE_DIR / "acm"
LAKE_BENCHMARKS_DIR = LAKEHOUSE_DIR / "benchmarks"
LAKE_COT_DIR = LAKEHOUSE_DIR / "cot"

# Ensure all directories exist
for p in [DATA_DIR, LAKEHOUSE_DIR, LAKE_ACM_DIR, LAKE_BENCHMARKS_DIR, LAKE_COT_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# 1. ACM Nano Metals Configurations
ACM_METALS = {
    'COMM_COPPER_NANO': {
        'url': 'https://asiacommodity.market/commodity-contracts/metals/nano-copper-derivatives',
        'code': 'NCP',
        'name': 'Nano Copper Derivatives',
        'contract_size': '1,000 lbs',
        'unit': 'USD/lb'
    },
    'COMM_PLATINUM_NANO': {
        'url': 'https://asiacommodity.market/commodity-contracts/metals/nano-platinum-derivatives',
        'code': 'NPT',
        'name': 'Nano Platinum Derivatives',
        'contract_size': '5 oz',
        'unit': 'USD/oz'
    },
    'COMM_SILVER_NANO': {
        'url': 'https://asiacommodity.market/commodity-contracts/metals/nano-silver-derivatives',
        'code': 'NSI',
        'name': 'Nano Silver Derivatives',
        'contract_size': '100 oz',
        'unit': 'USD/oz'
    }
}

# 2. Benchmark Metals, Mining Equities & FX Proxies
BENCHMARK_TARGETS = {
    # Benchmark Futures
    'HG=F': {'commodity_id': 'COMM_COPPER_COMEX', 'name': 'COMEX Copper Futures', 'unit': 'USD/lb'},
    'PL=F': {'commodity_id': 'COMM_PLATINUM_NYMEX', 'name': 'NYMEX Platinum Futures', 'unit': 'USD/oz'},
    'SI=F': {'commodity_id': 'COMM_SILVER_COMEX', 'name': 'COMEX Silver Futures', 'unit': 'USD/oz'},
    'GC=F': {'commodity_id': 'COMM_GOLD_COMEX', 'name': 'COMEX Gold Futures (GSR)', 'unit': 'USD/oz'},
    
    # Mining Equities & ETFs (Leading Indicators)
    'FCX': {'commodity_id': 'EQUITY_FREEPORT_COPPER', 'name': 'Freeport-McMoRan Inc (Copper)', 'unit': 'USD'},
    'PAAS': {'commodity_id': 'EQUITY_PAN_AMERICAN_SILVER', 'name': 'Pan American Silver Corp', 'unit': 'USD'},
    'SBSW': {'commodity_id': 'EQUITY_SIBANYE_PLATINUM', 'name': 'Sibanye Stillwater (Platinum/PGM)', 'unit': 'USD'},
    'SIL': {'commodity_id': 'ETF_SILVER_MINERS', 'name': 'Global X Silver Miners ETF', 'unit': 'USD'},
    
    # Macro FX Proxy
    'USDCNY=X': {'commodity_id': 'FX_USD_CNY', 'name': 'USD to Chinese Yuan', 'unit': 'CNY'}
}

# 3. CFTC Disaggregated COT Markets
CFTC_METALS = {
    'COPPER- #1 - COMMODITY EXCHANGE INC.': {
        'code': 'COPPER',
        'comm_id': 'COMM_COPPER_COMEX',
        'var_prefix': 'positioning.cot.copper'
    },
    'SILVER - COMMODITY EXCHANGE INC.': {
        'code': 'SILVER',
        'comm_id': 'COMM_SILVER_COMEX',
        'var_prefix': 'positioning.cot.silver'
    },
    'PLATINUM - NEW YORK MERCANTILE EXCHANGE': {
        'code': 'PLATINUM',
        'comm_id': 'COMM_PLATINUM_NYMEX',
        'var_prefix': 'positioning.cot.platinum'
    },
    'GOLD - COMMODITY EXCHANGE INC.': {
        'code': 'GOLD',
        'comm_id': 'COMM_GOLD_COMEX',
        'var_prefix': 'positioning.cot.gold'
    }
}
