import sys
import zipfile
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python scripts/inspect_boundaries.py <zip_path>"
    )

path = Path(sys.argv[1])

with zipfile.ZipFile(path) as archive:
    print("Archive contents:")
    for name in archive.namelist():
        print(f"  {name}")