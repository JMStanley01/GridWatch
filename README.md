- Purpose: See relative energy consumption around Richmond Virginia.
- Current source: 2024 ACS 5-year population and household estimates, covering 2020–2024.
- Setup: create .venv, install requests and python-dotenv, and copy .env.example to .env with your own Census key.
- Run command: .\.venv\Scripts\python.exe scripts\ingest_census.py
- Output: timestamped raw JSON in data/bronze/census/, excluded from Git.
- Validation: Bronze data is validated by confirming columns and then transformation logic is applied to better read the data




- Roadmap Plans: Create heatmap, create cloud resources, create databricks(or equivalant) notebooks to allow for cron jobs.