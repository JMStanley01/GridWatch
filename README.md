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