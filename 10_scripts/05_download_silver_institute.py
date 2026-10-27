import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from download_utils import download_file, BASE_DIR

RAW_DIR = BASE_DIR / "02_raw" / "silver"

SILVER_SURVEYS = [
    {
        "year": 2024,
        "url": "https://silverinstitute.org/wp-content/uploads/2024/07/World-Silver-Survey-2024.pdf",
        "file_id": "RAW_SILVER_WSS_2024",
        "local_name": "silver__silver_institute__world_silver_survey__2024__original.pdf"
    },
    {
        "year": 2023,
        "url": "https://silverinstitute.org/wp-content/uploads/2023/04/World-Silver-Survey-2023.pdf",
        "file_id": "RAW_SILVER_WSS_2023",
        "local_name": "silver__silver_institute__world_silver_survey__2023__original.pdf"
    },
    {
        "year": 2022,
        "url": "https://silverinstitute.org/wp-content/uploads/2022/04/World-Silver-Survey-2022.pdf",
        "file_id": "RAW_SILVER_WSS_2022",
        "local_name": "silver__silver_institute__world_silver_survey__2022__original.pdf"
    },
    {
        "year": 2021,
        "url": "https://silverinstitute.org/wp-content/uploads/2021/04/World-Silver-Survey-2021.pdf",
        "file_id": "RAW_SILVER_WSS_2021",
        "local_name": "silver__silver_institute__world_silver_survey__2021__original.pdf"
    },
    {
        "year": 2020,
        "url": "https://silverinstitute.org/wp-content/uploads/2020/04/World-Silver-Survey-2020.pdf",
        "file_id": "RAW_SILVER_WSS_2020",
        "local_name": "silver__silver_institute__world_silver_survey__2020__original.pdf"
    },
    {
        "year": 2018,
        "url": "https://silverinstitute.org/wp-content/uploads/2018/04/2018WorldSilverSurvey.pdf",
        "file_id": "RAW_SILVER_WSS_2018",
        "local_name": "silver__silver_institute__world_silver_survey__2018__original.pdf"
    },
    {
        "year": 2015,
        "url": "https://silverinstitute.org/wp-content/uploads/2017/10/2015WorldSilverSurvey.pdf",
        "file_id": "RAW_SILVER_WSS_2015",
        "local_name": "silver__silver_institute__world_silver_survey__2015__original.pdf"
    }
]

def main():
    print("=== Downloading Silver Institute World Silver Surveys ===")
    for item in SILVER_SURVEYS:
        target = RAW_DIR / item["local_name"]
        download_file(item["url"], target, item["file_id"], "Silver", "SRC_SILVER_INSTITUTE_WSS", timeout=45)
    print("Silver Institute download finished.\n")

if __name__ == "__main__":
    main()
