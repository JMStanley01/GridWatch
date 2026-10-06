from datetime import datetime, timezone
from pathlib import Path
import zipfile

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
def ingest_boundaries():
    url = (
        "https://www2.census.gov/geo/tiger/"
        "TIGER2024/TRACT/tl_2024_51_tract.zip"
    )

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    output_dir = PROJECT_ROOT / "data" / "bronze" / "boundaries"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_path = output_dir / f"tl_2024_51_tract_{timestamp}.zip"

    output_path.write_bytes(response.content)

    if not zipfile.is_zipfile(output_path):
        raise ValueError("Downloaded file is not a valid ZIP archive")

    print(f"Boundary archive saved to: {output_path}")


    with zipfile.ZipFile(output_path) as archive:
        print("Archive contents:")
        for name in archive.namelist():
            print(f"  {name}")

    return output_path

if __name__ == "__main__":
    ingest_boundaries()