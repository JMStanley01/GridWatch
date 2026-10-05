import sys
from pathlib import Path

from transform_census import transform_file as transform_census
from transform_boundaries import transform_file as transform_boundaries
from join_census_boundaries import join_files
from map_population import build_map


def run_pipeline(census_path, boundaries_path):
    for path in [census_path, boundaries_path]:
        if not path.is_file():
            raise FileNotFoundError(f"Input file not found: {path}")

    census_silver = transform_census(census_path)
    boundaries_silver = transform_boundaries(boundaries_path)
    joined_path = join_files(census_silver, boundaries_silver)
    map_path = build_map(joined_path)

    print(f"\nPipeline complete. Map: {map_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python scripts/run_pipeline.py "
            "<raw_census_json> <boundary_zip>"
        )

    run_pipeline(Path(sys.argv[1]), Path(sys.argv[2]))