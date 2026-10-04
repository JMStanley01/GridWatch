# GridWatch

GridWatch City is a data engineering portfolio project that will estimate
relative electricity demand across Census tracts in Richmond, Virginia.

The planned Power Demand Index will combine demographic, building,
weather, and regional grid data. It will represent estimated relative
demand—not measured electricity consumption.

## Current Progress

The local pipeline currently:

1. Fetches Richmond population and household estimates from the Census API.
2. Saves the original response and retrieval metadata in Bronze.
3. Validates row structure, geographic identifiers, and estimates.
4. Transforms Census records into Silver.
5. Downloads Virginia Census tract boundaries.
6. Filters Richmond boundaries and converts them to GeoJSON.
7. Joins estimates to boundaries using GEOID.

The joined dataset contains 75 Richmond Census tracts.
A Power Demand Index has not yet been calculated.

## Data Sources

| Source | Dataset | Purpose |
|---|---|---|
| U.S. Census Bureau | 2024 ACS 5-year estimates | Population and households |
| U.S. Census Bureau | 2024 TIGER/Line Virginia tract boundaries | Tract polygons and geographic identifiers |

The ACS estimates cover 2020–2024; they are not a single-year snapshot.

Census variables:
- `B01003_001E`: estimated total population
- `B11001_001E`: estimated total households

Richmond city is selected using state code `51` and county-equivalent
code `760`.

## Architecture

```text
Census API ──→ Raw JSON + metadata ──→ Validation ──→ Cleaned JSON
                                                              │
                                                              ▼
                                                        GEOID join
                                                              ▲
                                                              │
TIGER/Line ──→ Raw ZIP ──→ Richmond boundaries in GeoJSON ──────┘
                                                              │
                                                              ▼
                                                     Joined GeoJSON
```

Processing currently uses Python, pandas, and GeoPandas.

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
│   └── join_census_boundaries.py
├── data/
│   ├── bronze/
│   │   ├── census/
│   │   └── boundaries/
│   └── silver/
│       ├── census/
│       ├── boundaries/
│       └── joined/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Local datasets, credentials, and the virtual environment are excluded
from Git.

## Setup

Run these commands from the project root in PowerShell.

### Create the Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Configure the Census API key

Copy the configuration template:

```powershell
Copy-Item .env.example .env
```

Set your key in `.env`:

```dotenv
CENSUS_API_KEY=your_key_here
```

Do not commit `.env`. Boundary downloads do not require an API key.

## Run the Pipeline

Replace filenames in angle brackets with your actual filenames.
Do not type the angle brackets.

### 1. Ingest Census estimates

```powershell
.\.venv\Scripts\python.exe scripts\ingest_census.py
```

Creates timestamped raw JSON and metadata files under
`data/bronze/census/`.

### 2. Validate a Census snapshot

```powershell
.\.venv\Scripts\python.exe scripts\validate_census.py "data/bronze/census/<raw_file>.json"
```

Checks:
- Expected columns and at least one data row
- Row structure
- Geographic code format and Richmond city scope
- Unique GEOIDs
- Nonnegative integer population and household estimates

### 3. Transform Census estimates

```powershell
.\.venv\Scripts\python.exe scripts\transform_census.py "data/bronze/census/<raw_file>.json"
```

Validates the input and saves cleaned records under `data/silver/census/`.

### 4. Ingest tract boundaries

```powershell
.\.venv\Scripts\python.exe scripts\ingest_boundaries.py
```

Downloads a timestamped Virginia tract ZIP under
`data/bronze/boundaries/`. Each run downloads a new snapshot.

### 5. Inspect an existing archive

```powershell
.\.venv\Scripts\python.exe scripts\inspect_boundaries.py "data/bronze/boundaries/<archive>.zip"
```

Lists archive contents without downloading another file.

### 6. Transform boundaries

```powershell
.\.venv\Scripts\python.exe scripts\transform_boundaries.py "data/bronze/boundaries/<archive>.zip"
```

Filters Richmond tracts, checks for empty results and duplicate GEOIDs,
and transforms coordinates from EPSG:4269 to EPSG:4326.
Saves GeoJSON under `data/silver/boundaries/`.

### 7. Join estimates and boundaries

```powershell
.\.venv\Scripts\python.exe scripts\join_census_boundaries.py "data/silver/census/<cleaned_file>.json" "data/silver/boundaries/<boundary_file>.geojson"
```

Checks for missing and duplicate GEOIDs, verifies that both datasets
contain the same GEOIDs, and performs a one-to-one attribute join.

Saves the joined GeoJSON under `data/silver/joined/`.

## Data Layers

### Bronze

Preserves source responses and archives before transformation.
Census metadata records the request parameters, retrieval time, and
tract count without storing the API key.

### Silver

Contains cleaned Census records, Richmond tract boundaries, and their
joined GeoJSON.

GEOIDs remain strings to preserve leading zeros.
Population and household estimates are converted to integers.

Transformation filenames identify their source snapshots. Rerunning
a transformation with the same inputs replaces the corresponding output.

### Gold — Planned

Will contain analytical outputs, including the estimated Power Demand
Index.

## Limitations

- Population and households alone do not measure electricity demand.
- ACS values are survey estimates with uncertainty; margins of error
  are not currently ingested.
- The study covers Richmond city limits, not the wider metropolitan area.
- Weather, building activity, and regional grid demand are not yet included.

## Next Steps

- Create a population map to inspect the joined dataset
- Add additional demand-related data sources
- Document and calculate an initial Power Demand Index
- Add PySpark and SQL analytics as the pipeline develops
- Explore PostgreSQL/PostGIS, AWS storage, and anomaly detection

## Source Documentation

- [ACS 5-year data](https://www.census.gov/data/developers/data-sets/acs-5year.html)
- [2024 TIGER/Line files](https://www.census.gov/geographies/mapping-files/2024/geo/tiger-line-file.html)