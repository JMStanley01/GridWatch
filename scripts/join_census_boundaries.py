import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def join_files(census_path, boundaries_path):
    with census_path.open(encoding="utf-8") as file:
        census = pd.DataFrame(json.load(file))

    boundaries = gpd.read_file(boundaries_path)

    for name, frame in [
        ("Census", census),
        ("Boundaries", boundaries),
    ]:
        if frame["geoid"].isna().any():
            raise ValueError(f"{name}: missing GEOIDs")

        if frame["geoid"].duplicated().any():
            raise ValueError(f"{name}: duplicate GEOIDs")

    census_ids = set(census["geoid"])
    boundary_ids = set(boundaries["geoid"])

    if census_ids != boundary_ids:
        raise ValueError(
            f"Missing boundaries: {sorted(census_ids - boundary_ids)}; "
            f"Missing estimates: {sorted(boundary_ids - census_ids)}"
        )

    census_columns = ["geoid", "population", "households"]

    moe_columns = ["population_moe", "households_moe"]
    if all(column in census.columns for column in moe_columns):
        census_columns.extend(moe_columns)

    joined = boundaries.merge(
        census[census_columns],
        on="geoid",
        how="left",
        validate="one_to_one",
    )

    output_dir = PROJECT_ROOT / "data" / "silver" / "joined"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / (
        f"{census_path.stem}__{boundaries_path.stem}_joined.geojson"
    )

    joined.to_file(output_path, driver="GeoJSON", index=False)

    print(f"Joined data saved to: {output_path}")

    print(f"Joined {len(joined)} tracts with matching GEOIDs")
    print(joined[["geoid", "population", "households"]].head())

    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python scripts/join_census_boundaries.py "
            "<census_json_path> <boundaries_geojson_path>"
        )

    join_files(Path(sys.argv[1]), Path(sys.argv[2]))