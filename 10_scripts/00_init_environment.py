import os
import json
from pathlib import Path

BASE_DIR = Path(r"e:\My\the20\test_strategy\commodity source\commodity_equilibrium")

DIRS = [
    "00_config",
    "01_source_registry",
    "02_raw/silver",
    "02_raw/copper",
    "02_raw/platinum",
    "02_raw/macro_cross",
    "02_raw/cftc_cot",
    "02_raw/world_bank",
    "02_raw/usgs",
    "02_raw/wpic",
    "02_raw/icsg",
    "02_raw/silver_institute",
    "03_extracted",
    "04_normalized",
    "05_validated",
    "06_canonical",
    "07_daily_features",
    "08_reports",
    "09_logs",
    "10_scripts"
]

def init_directories():
    for d in DIRS:
        p = BASE_DIR / d
        p.mkdir(parents=True, exist_ok=True)
    print(f"Created all directories under {BASE_DIR}")

CONFIG = {
    "project_name": "Commodity Equilibrium Historical Data Engine",
    "version": "1.0.0",
    "target_metals": ["Silver", "Copper", "Platinum"],
    "time_range": {
        "target_start": "2000-01-01",
        "primary_end": "present"
    },
    "units": {
        "silver": {"standard": "Moz", "conversion_from_tonnes": 32.1507, "conversion_from_koz": 0.001},
        "copper": {"standard": "kt", "conversion_from_mt": 0.001, "conversion_from_tonnes": 0.001},
        "platinum": {"standard": "koz", "conversion_from_tonnes": 32.1507, "conversion_from_moz": 1000.0}
    },
    "balance_formula": "market_balance = total_supply - total_demand (positive = surplus, negative = deficit)",
    "paths": {
        "base": str(BASE_DIR),
        "source_registry": str(BASE_DIR / "01_source_registry" / "source_registry.csv"),
        "download_manifest": str(BASE_DIR / "01_source_registry" / "download_manifest.csv"),
        "data_dictionary": str(BASE_DIR / "01_source_registry" / "data_dictionary.csv"),
        "raw": str(BASE_DIR / "02_raw"),
        "extracted": str(BASE_DIR / "03_extracted"),
        "normalized": str(BASE_DIR / "04_normalized"),
        "validated": str(BASE_DIR / "05_validated"),
        "canonical": str(BASE_DIR / "06_canonical"),
        "features": str(BASE_DIR / "07_daily_features"),
        "reports": str(BASE_DIR / "08_reports"),
        "logs": str(BASE_DIR / "09_logs")
    }
}

def init_config():
    cfg_file = BASE_DIR / "00_config" / "config.json"
    with open(cfg_file, "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, indent=4)
    print(f"Config initialized at {cfg_file}")

if __name__ == "__main__":
    init_directories()
    init_config()
