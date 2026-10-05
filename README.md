# GridWatch City

GridWatch City is a data engineering portfolio project focused on
Richmond, Virginia.

The goal is to build an estimated Power Demand Index for Census tracts
using demographic, building, weather, and regional grid data.

The index will represent relative estimated demand, not measured
electricity consumption.

## Current Status

The project currently produces an interactive population map for
75 Richmond Census tracts.

The pipeline:

1. Ingests Census population, household, and margin-of-error data.
2. Saves raw responses and retrieval metadata locally.
3. Validates the Census data.
4. Transforms estimates into cleaned records.
5. Ingests Virginia Census tract boundaries.
6. Filters and transforms Richmond boundaries.
7. Joins estimates to polygons using GEOID.
8. Generates an HTML map with estimates and margins of error on hover.

The Power Demand Index has not yet been calculated.

## Data Sources

| Source | Dataset | Purpose |
|---|---|---|
| U.S. Census Bureau | 2024 ACS 5-year estimates | Population, households, and sampling uncertainty |
| U.S. Census Bureau | 2024 TIGER/Line Virginia Census tracts | Geographic boundaries |

The ACS estimates cover **2020–2024**, rather than a single-year snapshot.

### Census Variables

| Variable | Meaning |
|---|---|
| `B01003_001E` | Estimated population |
| `B01003_001M` | Population margin of error |
| `B11001_001E` | Estimated households |
| `B11001_001M` | Household margin of error |

ACS margins of error use a **90% confidence level** and are expressed
in the same units as the corresponding estimates.

The margins describe sampling uncertainty; they do not account for
all possible sources of error.

### Geographic Scope

The project covers Richmond city limits, not the broader metropolitan area.

Richmond is an independent city represented as a county equivalent:

- Virginia state code: `51`
- Richmond city county-equivalent code: `760`

Tract GEOIDs combine state, county, and tract codes. They remain strings
to preserve leading zeros.

## Architecture

```text
Census API
    → Bronze JSON + metadata
    → Validation
    → Silver Census records
                              \
                               → GEOID join → Joined Silver GeoJSON
                              /                         ↓
TIGER/Line ZIP                                         HTML map
    → Bronze archive
    → Richmond filtering and coordinate transformation
    → Silver boundaries
```

Development currently runs locally using Python, pandas, GeoPandas,
and Folium.

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
│   └── map_population.py
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

Credentials, local datasets, generated maps, and the virtual environment
are excluded from Git.

## Setup

Run commands from the project root in PowerShell.

### Create a Virtual Environment

```powershell
python -m venv .venv
```

### Install Dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Configure the Census API Key

For initial setup, copy the template:

```powershell
Copy-Item .env.example .env
```

If `.env` already exists, edit it instead of overwriting it.

Set your key:

```dotenv
CENSUS_API_KEY=your_key_here
```

Do not commit `.env` or include the key in logs or saved metadata.

Boundary downloads do not require an API key.

## Run the Pipeline

Replace placeholder filenames with the actual filenames printed by
each script. Do not type the angle brackets.

### 1. Ingest Census Data

```powershell
.\.venv\Scripts\python.exe scripts\ingest_census.py
```

Creates two files under `data/bronze/census/`:

- A timestamped raw JSON response
- A matching `.metadata.json` file

Metadata includes the endpoint, request parameters without the API key,
retrieval timestamp, raw filename, and tract count.

Each ingestion run creates a new snapshot.

### 2. Validate Census Data

Use the raw JSON file, not its metadata companion.

```powershell
.\.venv\Scripts\python.exe scripts\validate_census.py "data/bronze/census/<raw_file>.json"
```

Validation checks:

- A header and at least one data row
- Supported columns with no duplicate column names
- Consistent row structure
- Geographic code format and Richmond scope
- Unique tract GEOIDs
- Nonnegative whole-number estimates and margins of error

The validator supports both the original estimate-only schema and
the newer schema containing both margin-of-error fields.

Missing or negative numeric values are flagged for investigation.

### 3. Transform Census Data

```powershell
.\.venv\Scripts\python.exe scripts\transform_census.py "data/bronze/census/<raw_file>.json"
```

Validates the source and saves cleaned JSON under `data/silver/census/`.

Current records contain:

```json
{
  "geoid": "51760010201",
  "tract_name": "Census Tract 102.01; Richmond city; Virginia",
  "population": 2061,
  "households": 989,
  "population_moe": 375,
  "households_moe": 143
}
```

Older source snapshots produce records without the MOE fields.

### 4. Ingest Boundaries

```powershell
.\.venv\Scripts\python.exe scripts\ingest_boundaries.py
```

Downloads the 2024 Virginia tract ZIP to `data/bronze/boundaries/`
and checks that it is a valid ZIP archive.

Each run downloads a new snapshot.

### 5. Inspect an Existing Archive

```powershell
.\.venv\Scripts\python.exe scripts\inspect_boundaries.py "data/bronze/boundaries/<archive>.zip"
```

Lists archive contents without downloading or extracting another file.

### 6. Transform Boundaries

```powershell
.\.venv\Scripts\python.exe scripts\transform_boundaries.py "data/bronze/boundaries/<archive>.zip"
```

Reads the archive directly, filters Richmond tracts, and checks for
empty results and duplicate GEOIDs.

Coordinates are transformed from EPSG:4269 to EPSG:4326.

Output is saved under `data/silver/boundaries/` as GeoJSON containing:

- `geoid`
- `tract_name`
- `geometry`

### 7. Join Census Data and Boundaries

```powershell
.\.venv\Scripts\python.exe scripts\join_census_boundaries.py "data/silver/census/<cleaned_file>.json" "data/silver/boundaries/<boundary_file>.geojson"
```

The script checks for missing and duplicate GEOIDs, confirms that
both datasets contain the same GEOID set, and performs a one-to-one
attribute join.

Population, households, and available MOE fields are retained.

Output is saved under `data/silver/joined/`.

### 8. Generate the Population Map

Use a joined dataset containing both MOE fields for the current map script.

```powershell
.\.venv\Scripts\python.exe scripts\map_population.py "data/silver/joined/<joined_file>.geojson"
```

Saves an interactive HTML map under `data/maps/`.

Open the HTML file in a browser. Hover details show:

- Tract GEOID
- Estimated population
- Population MOE at the 90% confidence level
- Estimated households
- Household MOE at the 90% confidence level

Colors represent **total population per tract**, not population density
or electricity demand.

The map currently uses no background tiles. Internet access is still
needed for hosted JavaScript and CSS resources.

## Data Layers and Reproducibility

### Bronze

Preserves original source responses and archives before transformation.

### Silver

Contains cleaned Census records, Richmond boundaries, and joined
geographic data.

### Gold — Planned

Will contain analytical outputs, including the estimated Power Demand Index.

Output filenames identify their source snapshots. Running a transformation
again with the same inputs replaces its corresponding output.

If local datasets are deleted, the scripts can regenerate them by running
the pipeline in order. New downloads receive new timestamps and may differ
from earlier source snapshots.

## Limitations

- Demographic estimates do not directly measure electricity consumption.
- The current map shows population only.
- ACS estimates contain sampling and nonsampling uncertainty.
- Tract differences should not be assumed statistically significant.
- Weather, buildings, commercial activity, and grid demand are not yet included.
- Pipeline steps currently require manually passing filenames.
- Dependencies are currently listed without pinned versions.

## Planned Improvements

- Add a pipeline runner that passes output paths between steps
- Add building or commercial activity data
- Ingest weather and regional grid demand
- Define and document the initial Power Demand Index
- Introduce PySpark and SQL analytics
- Explore PostgreSQL/PostGIS and AWS S3
- Add incremental loading, retention rules, and anomaly detection

## Source Documentation

- [ACS 5-year data](https://www.census.gov/data/developers/data-sets/acs-5year.html)
- [ACS sampling uncertainty and margins of error](https://www.census.gov/programs-surveys/acs/methodology/sample-size-and-data-quality/sample-size-definitions.html)
- [2024 TIGER/Line files](https://www.census.gov/geographies/mapping-files/2024/geo/tiger-line-file.html)