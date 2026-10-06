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

Ingestion currently runs separately. The processing runner connects
the steps from existing Bronze inputs through the final map.

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

### 1. Download Both Sources

```powershell
.\.venv\Scripts\python.exe scripts\ingest_census.py
.\.venv\Scripts\python.exe scripts\ingest_boundaries.py
```

Each command prints its output path. Census ingestion creates a raw JSON
file and a matching metadata file. Boundary ingestion creates a ZIP archive.

### 2. Run Processing

Replace the placeholder filenames with the actual output filenames.
Do not include the angle brackets.

```powershell
.\.venv\Scripts\python.exe scripts\run_pipeline.py "data/bronze/census/<raw_census_file>.json" "data/bronze/boundaries/<boundary_archive>.zip"
```

Use the raw Census JSON, not the `.metadata.json` file.
Use a Census snapshot containing both margin-of-error fields.

The runner:
1. Checks that both input files exist.
2. Validates and transforms Census data.
3. Transforms Richmond tract boundaries.
4. Checks GEOID coverage and joins the datasets.
5. Generates the population map.

Output paths are passed directly between functions.
If a step fails, execution stops; outputs from completed steps remain.

The runner does not download new data.

### 3. View the Map

Open the generated HTML file under `data/maps/` in a browser.

Hover details show:
- Tract GEOID
- Population estimate and margin of error
- Household estimate and margin of error

Colors represent **total population per tract**, not population density
or electricity demand.

The map uses no background tiles. Hosted JavaScript and CSS still
require internet access.

## Run Individual Steps

Individual scripts remain available for inspection and troubleshooting.

### Validate Census Data

```powershell
.\.venv\Scripts\python.exe scripts\validate_census.py "data/bronze/census/<raw_file>.json"
```

### Transform Census Data

```powershell
.\.venv\Scripts\python.exe scripts\transform_census.py "data/bronze/census/<raw_file>.json"
```

### Inspect a Boundary Archive

```powershell
.\.venv\Scripts\python.exe scripts\inspect_boundaries.py "data/bronze/boundaries/<archive>.zip"
```

### Transform Boundaries

```powershell
.\.venv\Scripts\python.exe scripts\transform_boundaries.py "data/bronze/boundaries/<archive>.zip"
```

### Join Silver Datasets

```powershell
.\.venv\Scripts\python.exe scripts\join_census_boundaries.py "data/silver/census/<cleaned_file>.json" "data/silver/boundaries/<boundary_file>.geojson"
```

### Generate a Map

```powershell
.\.venv\Scripts\python.exe scripts\map_population.py "data/silver/joined/<joined_file>.geojson"
```

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