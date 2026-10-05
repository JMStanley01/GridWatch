import sys
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def transform_file(path):
    tracts = gpd.read_file(f"zip://{path.resolve().as_posix()}")

    richmond = tracts.loc[
        (tracts["STATEFP"] == "51")
        & (tracts["COUNTYFP"] == "760")
    ].copy()

    if richmond.empty:
        raise ValueError("No Richmond tracts found")

    if richmond["GEOID"].duplicated().any():
        raise ValueError("Duplicate tract GEOIDs found")

    richmond = richmond[["GEOID", "NAME", "geometry"]].copy()
    richmond = richmond.rename(
        columns={"GEOID": "geoid", "NAME": "tract_name"}
    )

    richmond = richmond.to_crs("EPSG:4326")

    output_dir = PROJECT_ROOT / "data" / "silver" / "boundaries"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{path.stem}_richmond.geojson"
    richmond.to_file(output_path, driver="GeoJSON", index=False)

    print(f"Silver boundaries saved to: {output_path}")


    print(f"Virginia tracts: {len(tracts)}")
    print(f"Richmond tracts: {len(richmond)}")
    print(f"Coordinate reference system: {richmond.crs}")
    print(richmond[["geoid", "tract_name"]].head())

    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python scripts/transform_boundaries.py <zip_path>"
        )

    transform_file(Path(sys.argv[1]))