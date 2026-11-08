# This checks that the dashboard files and integrated dataset are available.
# It validates the saved data before we build the website.
# No data is downloaded or modified.

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

required_files = [
    "research_charts.py",
    "permit_data_utils.py",
    "data/integrated_monthly_permits.csv",
    "data/building_monthly_counts.csv",
    "data/building_monthly_by_work_type.csv",
    "data/street_monthly_counts.csv",
    "data/street_monthly_by_category.csv",
]

for filename in required_files:
    path = BASE_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing: {path}")
    print(f"Found: {filename}")

data = pd.read_csv(
    BASE_DIR / "data/integrated_monthly_permits.csv"
)

assert len(data) == 180
assert not data.duplicated(["borough", "year", "month"]).any()
assert data["building_permit_count"].sum() == 408_566
assert data["street_permit_count"].sum() == 1_951_371

print("\nSetup passed: 180 monthly groups and correct permit totals.")