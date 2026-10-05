import json
import sys
from pathlib import Path

from validate_census import validate_file
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def transform_file(path):
    validate_file(path)

    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    records = []

    for row in data[1:]:
        source = dict(zip(data[0], row))

        record = {
            "geoid": (
                source["state"]
                + source["county"]
                + source["tract"]
            ),
            "tract_name": source["NAME"],
            "population": int(source["B01003_001E"]),
            "households": int(source["B11001_001E"]),
        }

        if "B01003_001M" in source:
            record["population_moe"] = int(source["B01003_001M"])
            record["households_moe"] = int(source["B11001_001M"])

        records.append(record)
    output_dir = PROJECT_ROOT / "data" / "silver" / "census"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{path.stem}_cleaned.json"
    output_path.write_text(
        json.dumps(records, indent=2),
        encoding="utf-8",
    )

    print(f"Silver data saved to: {output_path}")

    print(f"Transformed {len(records)} tracts")
    print("First record:", records[0])

    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python scripts/transform_census.py <raw_json_path>"
        )

    transform_file(Path(sys.argv[1]))