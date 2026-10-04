import os
from pathlib import Path


from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("CENSUS_API_KEY")
if not api_key:
    raise RuntimeError("Set CENSUS_API_KEY in your .env file")

url = "https://api.census.gov/data/2024/acs/acs5"
params = {
    "get": "NAME,B01003_001E,B11001_001E",
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

print("Columns:", data[0])
print("First tract:", data[1])
print("Tracts returned:", len(data) - 1)