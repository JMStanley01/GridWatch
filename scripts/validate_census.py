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

MOE_COLUMNS = [
    "B01003_001M",
    "B11001_001M",
]


def validate_file(path):
    with path.open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list) or len(data) < 2:
        raise ValueError("Expected a header and at least one tract row")

    header = data[0]
    if not isinstance(header, list) or not all(
        isinstance(column, str) for column in header
    ):
        raise ValueError("Invalid column header")

    if len(header) != len(set(header)):
        raise ValueError("Duplicate column names")

    columns = set(header)
    base_columns = set(EXPECTED_COLUMNS)

    if columns not in (base_columns, base_columns | set(MOE_COLUMNS)):
        raise ValueError(f"Unexpected columns: {header}")
    
    seen_geoids = set()

    for row_number, row in enumerate(data[1:], start=2):
        if not isinstance(row, list) or len(row) != len(header):
            raise ValueError(f"Row {row_number}: invalid row structure")

        record = dict(zip(data[0], row))
        state = record["state"]
        county = record["county"]
        tract = record["tract"]

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

        numeric_fields = [
            ("population", "B01003_001E"),
            ("households", "B11001_001E"),
        ]

        if set(MOE_COLUMNS).issubset(columns):
            numeric_fields.extend([
                ("population margin of error", "B01003_001M"),
                ("household margin of error", "B11001_001M"),
            ])

        for name, column in numeric_fields:
            value = record[column]

            if (
                not isinstance(value, str)
                or not value.isascii()
                or not value.isdigit()
            ):
                raise ValueError(
                    f"Row {row_number}: invalid {name} value {value!r}"
                )
            
        seen_geoids.add(geoid)

    print(f"Validation passed: {len(seen_geoids)} unique Richmond tracts")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python scripts/validate_census.py <raw_json_path>"
        )

    validate_file(Path(sys.argv[1]))