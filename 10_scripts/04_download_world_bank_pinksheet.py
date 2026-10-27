import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from download_utils import download_file, BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "world_bank"

WB_FILES = [
    {
        "file_id": "RAW_WORLD_BANK_CMO_HISTORICAL_MONTHLY",
        "url": "https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx",
        "local_name": "common__world_bank__cmo_historical_data_monthly__original.xlsx",
        "metal": "Common / Multi-metal",
        "source_id": "SRC_WORLD_BANK_PINKSHEET"
    }
]

def main():
    print("=== Downloading World Bank Commodity Pink Sheet ===")
    for item in WB_FILES:
        target = RAW_DIR / item["local_name"]
        download_file(item["url"], target, item["file_id"], item["metal"], item["source_id"])
    print("World Bank Pink Sheet download finished.\n")

if __name__ == "__main__":
    main()
