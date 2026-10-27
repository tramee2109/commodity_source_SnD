import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from download_utils import download_file, BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "usgs"

for y in [2025, 2024, 2023]:
    url = f"https://pubs.usgs.gov/periodicals/mcs{y}/mcs{y}-platinum-group.pdf"
    target = RAW_DIR / f"platinum__usgs__mineral_commodity_summaries__{y}__original.pdf"
    download_file(url, target, f"RAW_PLATINUM_USGS_MCS_{y}", "Platinum", "SRC_USGS_PLATINUM_MCS")
print("USGS Platinum 2023-2025 download complete!")
