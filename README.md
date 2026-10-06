# GridWatch City

A local data engineering project exploring estimated electricity demand
across Census tracts in Richmond, Virginia.

The planned Power Demand Index will combine demographic, building,
weather, and regional grid data. It will estimate relative demand,
rather than claim measured electricity consumption.

## Current Progress

The project currently produces an interactive population map for
75 Richmond Census tracts.

Implemented:
- Census population and household ingestion, including margins of error
- Raw local storage and Census retrieval metadata
- Data validation
- Census tract boundary ingestion and transformation
- One-to-one joins using tract GEOIDs
- Interactive population mapping
- A processing runner that connects validation, transformations, joins,
  and mapping

The Power Demand Index has not yet been calculated.

## Data Sources

| Source | Dataset | Purpose |
|---|---|---|
| U.S. Census Bureau | 2024 ACS 5-year estimates | Population, households, and margins of error |
| U.S. Census Bureau | 2024 TIGER/Line Virginia tract boundaries | Tract polygons and identifiers |

The ACS estimates cover **2020–2024**.

| Variable | Meaning |
|---|---|
| `B01003_001E` | Population estimate |
| `B01003_001M` | Population margin of error |
| `B11001_001E` | Household estimate |
| `B11001_001M` | Household margin of error |

ACS margins of error describe sampling uncertainty at the **90% confidence
level**. They do not capture every possible source of error.

The study covers Richmond city limits, using state code `51` and
county-equivalent code `760`.

## Architecture

```text
Census API → Bronze JSON + metadata → Validation → Silver estimates
                                                         │
                                                         ▼
                                                    GEOID join → Map
                                                         ▲
                                                         │
TIGER/Line → Bronze ZIP → Richmond filtering → Silver boundaries
```

The pipeline runner connects ingestion, validation, transformations, joins, and mapping.

## Project Structure

```text
GridWatch/
├── scripts/
│   ├── ingest_census.py
│   ├── validate_census.py
│   ├── transform_census.py
│   ├── ingest_boundaries.py
│   ├── inspect_boundaries.py
│   ├── transform_boundaries.py
│   ├── join_census_boundaries.py
│   ├── map_population.py
│   └── run_pipeline.py
├── data/
│   ├── bronze/
│   │   ├── census/
│   │   └── boundaries/
│   ├── silver/
│   │   ├── census/
│   │   ├── boundaries/
│   │   └── joined/
│   └── maps/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The `data/` directory, `.env`, and `.venv/` are excluded from Git.

## Setup

Run commands from the project root in PowerShell.

### Create the Environment

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Configure Credentials

For first-time setup:

```powershell
Copy-Item .env.example .env
```

If `.env` already exists, edit it instead of overwriting it.

Add your Census API key:

```dotenv
CENSUS_API_KEY=your_key_here
```

Never commit the key. Boundary downloads do not require credentials.

## Quick Start

## Run the Pipeline

From the project root in PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\run_pipeline.py --ingest
```

This command:

1. Downloads Census estimates and margins of error.
2. Downloads Virginia Census tract boundaries.
3. Validates the Census records.
4. Creates cleaned Census data and Richmond boundaries.
5. Joins the datasets using GEOID.
6. Saves an interactive population map.

Each download creates a new Bronze snapshot. Output paths are passed
automatically between steps.

If a step fails, execution stops. Files from completed steps remain
available.

### View the Map

The final terminal message shows the HTML output path.

Open that file in your browser to view population estimates and hover
details, including population and household margins of error.

Map colors represent total population per tract—not population density
or electricity demand.

The map has no background tiles. Internet access is still required
for hosted JavaScript and CSS.

### Reprocess Existing Data

To rebuild outputs without downloading new snapshots:

```powershell
.\.venv\Scripts\python.exe scripts\run_pipeline.py "data/bronze/census/<raw_census_file>.json" "data/bronze/boundaries/<boundary_archive>.zip"
```

Replace the placeholders with existing filenames. Use the raw Census
JSON containing both margin-of-error fields, not its metadata companion.

Individual scripts remain available under `scripts/` for troubleshooting.

## Data Quality and Transformations

Census validation checks:
- Supported columns and unique column names
- At least one data row
- Consistent row structure
- Geographic code format and Richmond scope
- Unique GEOIDs
- Nonnegative whole-number estimates and margins of error

The validator and Census transformer support older estimate-only
snapshots as well as snapshots containing both MOE fields.
The current map requires MOE fields.

Boundary processing:
- Selects Richmond tracts from the Virginia archive
- Rejects empty selections and duplicate GEOIDs
- Transforms coordinates from EPSG:4269 to EPSG:4326

Joining:
- Rejects missing or duplicate GEOIDs
- Requires identical GEOID sets in both datasets
- Enforces a one-to-one attribute join

GEOIDs remain strings to preserve leading zeros.
Estimates and MOEs are converted to integers.



### Logging past runs

When running the run_pipeline file as normal without the --ingest flag, records of past runs will be stored in data/runs

## Storage and Reproducibility

### Bronze

Original Census responses, retrieval metadata, and boundary archives.

Census metadata records source details and request parameters without
the API key.

### Silver

Cleaned Census records, Richmond polygons, and joined GeoJSON.

### Maps

Generated HTML visualizations derived from joined Silver data.

### Gold — Planned

Analytical outputs, including the estimated Power Demand Index.

Each ingestion creates a timestamped snapshot.
Transformation filenames identify their inputs. Reprocessing the same
inputs replaces the corresponding outputs.

Deleted local data can be regenerated by downloading the sources and
running the processing pipeline. New downloads have new timestamps
and may differ from previous source snapshots.

## Limitations

- Current outputs show demographics, not electricity demand.
- ACS estimates contain sampling and nonsampling uncertainty.
- Differences between tracts are not automatically statistically significant.
- Weather, buildings, commercial activity, and grid demand are not yet included.
- Ingestion is not yet connected to the runner.
- Dependencies are not yet pinned to specific versions.
- Automated retention and incremental loading are not yet implemented.

## Next Steps

- Make ingestion functions callable from the runner
- Add building or commercial activity data
- Add weather and regional grid demand
- Define and document an initial Power Demand Index
- Introduce PySpark and SQL analytics
- Explore PostgreSQL/PostGIS and AWS S3
- Add incremental loading and anomaly detection

## Documentation

- [ACS 5-year data](https://www.census.gov/data/developers/data-sets/acs-5year.html)
- [ACS margins of error](https://www.census.gov/programs-surveys/acs/methodology/sample-size-and-data-quality/sample-size-definitions.html)
- [2024 TIGER/Line files](https://www.census.gov/geographies/mapping-files/2024/geo/tiger-line-file.html)