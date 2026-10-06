import os
from pathlib import Path
import json

from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
def ingest_census():
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("CENSUS_API_KEY")
    if not api_key:
        raise RuntimeError("Set CENSUS_API_KEY in your .env file")

    url = "https://api.census.gov/data/2024/acs/acs5"
    params = {
        "get": (
            "NAME,B01003_001E,B11001_001E,"
            "B01003_001M,B11001_001M"
        ),
        "for": "tract:*",
        "in": "state:51 county:760",
        "key": api_key,
    }

    response = requests.get(url, params=params, timeout=30)

    # Avoid printing the request URL, which contains the API key.
    if response.status_code != 200:
        raise RuntimeError(f"Census request failed: HTTP {response.status_code}")

    data = response.json()
    output_dir = PROJECT_ROOT / "data" / "bronze" / "census"
    output_dir.mkdir(parents=True, exist_ok=True)

    retrieved_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_path = output_dir / f"richmond_acs5_2024_{retrieved_at}.json"

    output_path.write_bytes(response.content)

    print(f"Raw data saved to: {output_path}")

    metadata = {
        "source": "U.S. Census Bureau",
        "dataset": "ACS 5-year",
        "dataset_year": 2024,
        "coverage_period": "2020-2024",
        "geography": "Richmond city, Virginia census tracts",
        "endpoint": url,
        "parameters": {
            name: value
            for name, value in params.items()
            if name != "key"
        },
        "retrieved_at_utc": retrieved_at,
        "raw_file": output_path.name,
        "tract_count": len(data) - 1,
        "http_status": response.status_code,
    }

    metadata_path = output_path.with_suffix(".metadata.json")
    metadata_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"Metadata saved to: {metadata_path}")


    print("Columns:", data[0])
    print("First tract:", data[1])
    print("Tracts returned:", len(data) - 1)
    return output_path

if __name__ == "__main__":
    ingest_census()