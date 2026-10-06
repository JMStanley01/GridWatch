import sys
from pathlib import Path

from transform_census import transform_file as transform_census
from transform_boundaries import transform_file as transform_boundaries
from join_census_boundaries import join_files
from map_population import build_map

from ingest_census import ingest_census
from ingest_boundaries import ingest_boundaries

import json
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_pipeline(census_path, boundaries_path):
    started_at = datetime.now(timezone.utc)
    run_id = started_at.strftime("%Y%m%dT%H%M%S%fZ")

    manifest_dir = PROJECT_ROOT / "data" / "runs"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / f"{run_id}.json"

    manifest = {
        "run_id": run_id,
        "status": "running",
        "started_at_utc": started_at.isoformat(),
        "inputs": {
            "census": str(census_path.resolve()),
            "boundaries": str(boundaries_path.resolve()),
        },
        "outputs": {},
    }

    stage = "input_check"

    try:
        for path in [census_path, boundaries_path]:
            if not path.is_file():
                raise FileNotFoundError(f"Input file not found: {path}")

        stage = "transform_census"
        census_silver = transform_census(census_path)
        manifest["outputs"]["census_silver"] = str(census_silver.resolve())

        stage = "transform_boundaries"
        boundaries_silver = transform_boundaries(boundaries_path)
        manifest["outputs"]["boundaries_silver"] = str(
            boundaries_silver.resolve()
        )

        stage = "join"
        joined_path = join_files(census_silver, boundaries_silver)
        manifest["outputs"]["joined"] = str(joined_path.resolve())

        stage = "map"
        map_path = build_map(joined_path)
        manifest["outputs"]["map"] = str(map_path.resolve())

        manifest["status"] = "success"

    except Exception as error:
        manifest["status"] = "failed"
        manifest["failed_stage"] = stage
        manifest["error_type"] = type(error).__name__
        raise

    finally:
        manifest["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        manifest_path.write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        print(f"Run manifest saved to: {manifest_path}")

    print(f"\nPipeline complete. Map: {map_path}")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--ingest":
        census_path = ingest_census()
        boundaries_path = ingest_boundaries()
        run_pipeline(census_path, boundaries_path)

    elif len(sys.argv) == 3:
        run_pipeline(Path(sys.argv[1]), Path(sys.argv[2]))

    else:
        raise SystemExit(
            "Usage:\n"
            "  python scripts/run_pipeline.py --ingest\n"
            "  python scripts/run_pipeline.py "
            "<raw_census_json> <boundary_zip>"
        )