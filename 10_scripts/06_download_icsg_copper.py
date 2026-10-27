import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from download_utils import download_file, BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "copper"

ICSG_FILES = [
    {
        "file_id": "RAW_COPPER_ICSG_TABLE1",
        "url": "https://icsg.org/wp-content/uploads/Table1.pdf",
        "local_name": "copper__icsg__world_refined_copper_production_and_usage_trends__original.pdf",
        "metal": "Copper",
        "source_id": "SRC_ICSG_COPPER_STATS"
    },
    {
        "file_id": "RAW_COPPER_ICSG_TABLE2",
        "url": "https://icsg.org/wp-content/uploads/Table2.pdf",
        "local_name": "copper__icsg__mine_smelter_refinery_production_and_usage_by_geography__original.pdf",
        "metal": "Copper",
        "source_id": "SRC_ICSG_COPPER_STATS"
    },
    {
        "file_id": "RAW_COPPER_ICSG_CHART1",
        "url": "https://icsg.org/wp-content/uploads/Chart1.pdf",
        "local_name": "copper__icsg__trends_in_world_refined_stocks_and_prices__original.pdf",
        "metal": "Copper",
        "source_id": "SRC_ICSG_COPPER_STATS"
    },
    {
        "file_id": "RAW_COPPER_ICSG_FORECAST_2026_2027",
        "url": "https://icsg.org/download/2026-04-23-press-release-icsg-copper-market-forecast-2026-2027/?wpdmdl=9245&ind=69ea529460d24&refresh=9a8e40d5&filename=2026-04-23-ICSG-Forecast-Press-Release.pdf",
        "local_name": "copper__icsg__market_forecast_2026_2027_press_release__original.pdf",
        "metal": "Copper",
        "source_id": "SRC_ICSG_COPPER_STATS"
    }
]

def main():
    print("=== Downloading ICSG Copper Statistical Tables ===")
    for item in ICSG_FILES:
        target = RAW_DIR / item["local_name"]
        download_file(item["url"], target, item["file_id"], item["metal"], item["source_id"])
    print("ICSG Copper download finished.\n")

if __name__ == "__main__":
    main()
