import sys
from pathlib import Path
from urllib.parse import quote

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))
from download_utils import download_file, BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "platinum"

WPIC_FILES = [
    {
        "file_id": "RAW_PLATINUM_WPIC_PQ_2026_Q2",
        "url": "https://platinuminvestment.com/files/354715/WPIC_PQ_tables_Q2_2026.xlsx",
        "local_name": "platinum__wpic__platinum_quarterly_tables__2026_q2__original.xlsx",
        "metal": "Platinum",
        "source_id": "SRC_WPIC_PLATINUM_HISTORIC"
    },
    {
        "file_id": "RAW_PLATINUM_JM_2004_2012",
        "url": "https://platinuminvestment.com/files/" + quote("Johnson Matthey xls-2004-to-2012.xls"),
        "local_name": "platinum__johnson_matthey__historical_tables__2004_2012__original.xls",
        "metal": "Platinum",
        "source_id": "SRC_WPIC_PLATINUM_HISTORIC"
    },
    {
        "file_id": "RAW_PLATINUM_JM_2000_2004",
        "url": "https://platinuminvestment.com/files/" + quote("Johnson Matthey xls-2000-to-2004.xls"),
        "local_name": "platinum__johnson_matthey__historical_tables__2000_2004__original.xls",
        "metal": "Platinum",
        "source_id": "SRC_WPIC_PLATINUM_HISTORIC"
    },
    {
        "file_id": "RAW_PLATINUM_JM_1975_1999",
        "url": "https://platinuminvestment.com/files/" + quote("Johnson Matthey xls-1975-to-1999-(note-shows-net-demand).xls"),
        "local_name": "platinum__johnson_matthey__historical_tables__1975_1999__original.xls",
        "metal": "Platinum",
        "source_id": "SRC_WPIC_PLATINUM_HISTORIC"
    }
]

def main():
    print("=== Downloading WPIC & Johnson Matthey Platinum Datasets ===")
    for item in WPIC_FILES:
        target = RAW_DIR / item["local_name"]
        download_file(item["url"], target, item["file_id"], item["metal"], item["source_id"])
    print("WPIC Platinum download finished.\n")

if __name__ == "__main__":
    main()
