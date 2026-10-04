import json
import sys
from pathlib import Path

EXPECTED_COLUMNS = [
    "NAME",
    "B01003_001E",
    "B11001_001E",
    "state",
    "county",
    "tract",
]


def validate_file(path):
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list) or len(data) < 2:
        raise ValueError("Expected a header and at least one tract row")

    if data[0] != EXPECTED_COLUMNS:
        raise ValueError(f"Unexpected columns: {data[0]}")

    seen_geoids = set()

    for row_number, row in enumerate(data[1:], start=2):
        if not isinstance(row, list) or len(row) != len(EXPECTED_COLUMNS):
            raise ValueError(f"Row {row_number}: invalid row structure")

        state, county, tract = row[3:6]

        for name, value, width in [
            ("state", state, 2),
            ("county", county, 3),
            ("tract", tract, 6),
        ]:
            if (
                not isinstance(value, str)
                or len(value) != width
                or not value.isascii()
                or not value.isdigit()
            ):
                raise ValueError(f"Row {row_number}: invalid {name} code")

        if state != "51" or county != "760":
            raise ValueError(f"Row {row_number}: tract outside Richmond city")

        geoid = state + county + tract

        if geoid in seen_geoids:
            raise ValueError(f"Row {row_number}: duplicate GEOID {geoid}")

        for name, value in [
            ("population", row[1]),
            ("households", row[2]),
        ]:
            if (
                not isinstance(value, str)
                or not value.isascii()
                or not value.isdigit()
            ):
                raise ValueError(
                    f"Row {row_number}: invalid {name} estimate {value!r}"
                )
            
        seen_geoids.add(geoid)

    print(f"Validation passed: {len(seen_geoids)} unique Richmond tracts")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python scripts/validate_census.py <raw_json_path>"
        )

    validate_file(Path(sys.argv[1]))