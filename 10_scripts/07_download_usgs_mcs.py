import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from download_utils import download_file, BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "usgs"

USGS_DOWNLOADS = []

# Silver
for y in [2025, 2024, 2023, 2022, 2021, 2020]:
    USGS_DOWNLOADS.append({
        "url": f"https://pubs.usgs.gov/periodicals/mcs{y}/mcs{y}-silver.pdf",
        "file_id": f"RAW_SILVER_USGS_MCS_{y}",
        "local_name": f"silver__usgs__mineral_commodity_summaries__{y}__original.pdf",
        "metal": "Silver",
        "source_id": "SRC_USGS_SILVER_MCS"
    })

# Copper
for y in [2025, 2024, 2023, 2022, 2021, 2020]:
    USGS_DOWNLOADS.append({
        "url": f"https://pubs.usgs.gov/periodicals/mcs{y}/mcs{y}-copper.pdf",
        "file_id": f"RAW_COPPER_USGS_MCS_{y}",
        "local_name": f"copper__usgs__mineral_commodity_summaries__{y}__original.pdf",
        "metal": "Copper",
        "source_id": "SRC_USGS_COPPER_MCS"
    })

# Platinum / PGM
for y in [2025, 2024, 2023, 2022, 2021, 2020]:
    USGS_DOWNLOADS.append({
        "url": f"https://pubs.usgs.gov/periodicals/mcs{y}/mcs{y}-platinum.pdf",
        "file_id": f"RAW_PLATINUM_USGS_MCS_{y}",
        "local_name": f"platinum__usgs__mineral_commodity_summaries__{y}__original.pdf",
        "metal": "Platinum",
        "source_id": "SRC_USGS_PLATINUM_MCS"
    })

def main():
    print(f"=== Downloading {len(USGS_DOWNLOADS)} USGS Mineral Commodity Summaries ===")
    success_count = 0
    for item in USGS_DOWNLOADS:
        target = RAW_DIR / item["local_name"]
        ok = download_file(item["url"], target, item["file_id"], item["metal"], item["source_id"])
        if ok:
            success_count += 1
    print(f"USGS downloads complete: {success_count}/{len(USGS_DOWNLOADS)} succeeded.\n")

if __name__ == "__main__":
    main()
