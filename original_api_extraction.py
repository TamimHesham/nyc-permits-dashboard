# Original API extraction code retained for provenance.
# Run only deliberately; prefer the saved raw snapshots for reproduction.

# This cell imports the libraries for data analysis, downloading data,
# and creating interactive charts. It also sets the NYC dataset API URL
# and creates a folder for our cleaned data and output files.

import pandas as pd
import numpy as np
import requests
import time

import plotly.express as px

from pathlib import Path
from IPython.display import display

pd.set_option("display.max_columns", None)

DATASET_ID = "rbx6-tga4"
API_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json"

OUTPUT_DIR = Path("/content/task1_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Setup complete.")

# This cell reads the dataset's metadata to identify its columns and data types.
# API field names can differ from the names shown on the website.
# We check these names before choosing fields and filtering by issue date.

METADATA_URL = (
    f"https://data.cityofnewyork.us/api/views/{DATASET_ID}.json"
)

response = requests.get(METADATA_URL, timeout=60)
response.raise_for_status()
metadata = response.json()

columns_info = pd.DataFrame([
    {
        "Column name": column["name"],
        "API field": column["fieldName"],
        "Data type": column["dataTypeName"]
    }
    for column in metadata["columns"]
    if not column["fieldName"].startswith(":")
])

print("Dataset:", metadata["name"])
print("Number of columns:", len(columns_info))
display(columns_info)

# This cell counts permits issued from January 2023 through December 2025.
# We use an exclusive January 2026 boundary to include all of December 2025.
# The count will help us verify that our later download contains every matching row.

DATE_FILTER = (
    "issued_date >= '2023-01-01T00:00:00' "
    "AND issued_date < '2026-01-01T00:00:00'"
)

count_response = requests.get(
    API_URL,
    params={
        "$select": "count(*) AS total",
        "$where": DATE_FILTER
    },
    timeout=60
)
count_response.raise_for_status()

expected_rows = int(count_response.json()[0]["total"])

print(f"Records issued during 2023–2025: {expected_rows:,}")

# This cell downloads the selected records in batches to avoid the API's default
# row limit. We retain 20 relevant columns and preserve identifiers as text.
# A stable row order supports pagination, and we check the downloaded row count
# against the API count to detect an incomplete download.

SELECTED_COLUMNS = [
    "job_filing_number",
    "work_permit",
    "sequence_number",
    "filing_reason",
    "house_no",
    "street_name",
    "borough",
    "bin",
    "block",
    "lot",
    "work_type",
    "approved_date",
    "issued_date",
    "expired_date",
    "estimated_job_costs",
    "permit_status",
    "tracking_number",
    "zip_code",
    "latitude",
    "longitude"
]

BATCH_SIZE = 25000
batches = []

with requests.Session() as session:
    for offset in range(0, expected_rows, BATCH_SIZE):
        params = {
            "$select": ",".join(SELECTED_COLUMNS),
            "$where": DATE_FILTER,
            "$order": ":id",
            "$limit": BATCH_SIZE,
            "$offset": offset
        }

        for attempt in range(4):
            try:
                response = session.get(
                    API_URL,
                    params=params,
                    timeout=120
                )
                response.raise_for_status()
                records = response.json()

                if not isinstance(records, list):
                    raise ValueError("The API did not return a list of records.")

                break

            except (requests.RequestException, ValueError):
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))

        if not records:
            raise RuntimeError(
                f"The API returned an empty batch at offset {offset:,}."
            )

        batches.append(
            pd.DataFrame(records).reindex(columns=SELECTED_COLUMNS)
        )

        downloaded = sum(len(batch) for batch in batches)
        print(f"Downloaded {downloaded:,} / {expected_rows:,} rows")

        time.sleep(0.2)

df_raw = pd.concat(batches, ignore_index=True)

if len(df_raw) != expected_rows:
    raise RuntimeError(
        f"Expected {expected_rows:,} rows, but downloaded {len(df_raw):,}. "
        "Check whether the source changed during the download."
    )

raw_path = OUTPUT_DIR / "building_permits_raw_2023_2025.csv"
df_raw.to_csv(raw_path, index=False)

print(f"\nDownload complete: {df_raw.shape[0]:,} rows")
print(f"Columns retained: {df_raw.shape[1]}")
print(f"Raw copy saved to: {raw_path}")

display(df_raw.head())

# STREET EXTRACTION
# This cell checks the official street dataset's column names and data types.
# We must explicitly identify issuance dates, boroughs, identifiers and categories
# before downloading. Failed requests are retried; synthetic data is never used.

import pandas as pd
import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from IPython.display import display

STREET_DATASET_ID = "tqtj-sjs8"
STREET_API_URL = (
    f"https://data.cityofnewyork.us/resource/{STREET_DATASET_ID}.json"
)
STREET_METADATA_URL = (
    f"https://data.cityofnewyork.us/api/views/{STREET_DATASET_ID}.json"
)

retry_policy = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=True
)

street_session = requests.Session()
street_session.mount(
    "https://",
    HTTPAdapter(max_retries=retry_policy)
)

response = street_session.get(STREET_METADATA_URL, timeout=60)
response.raise_for_status()
street_metadata = response.json()

street_columns = pd.DataFrame([
    {
        "Column name": column["name"],
        "API field": column["fieldName"],
        "Data type": column["dataTypeName"]
    }
    for column in street_metadata["columns"]
    if not column["fieldName"].startswith(":")
])

print("Dataset:", street_metadata["name"])
print("Genuine source columns:", len(street_columns))
print(street_columns.to_string(index=False))

# This cell counts real street permits issued during 2023–2025.
# We filter by the permit issuance date, rather than record creation date,
# to align with the building dataset. The count will verify download completeness.

STREET_DATE_FILTER = (
    "permitissuedate >= '2023-01-01T00:00:00' "
    "AND permitissuedate < '2026-01-01T00:00:00'"
)

count_response = street_session.get(
    STREET_API_URL,
    params={
        "$select": "count(*) AS total",
        "$where": STREET_DATE_FILTER
    },
    timeout=120
)
count_response.raise_for_status()

street_expected_rows = int(count_response.json()[0]["total"])

print(f"Real street permit records in 2023–2025: {street_expected_rows:,}")

if street_expected_rows == 0:
    raise ValueError("No matching records returned. Check before proceeding.")

# This cell downloads all street-permit records issued during 2023–2025.
# It retains genuine source fields and writes batches directly to a raw CSV
# to limit memory use. Stable pagination and a final row-count check help
# detect incomplete downloads. No synthetic fallback is used.

from pathlib import Path
import time

STREET_OUTPUT_DIR = Path("/content/task2_outputs")
STREET_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STREET_COLUMNS = [
    "permitnumber",
    "applicationtrackingid",
    "sequencenumber",
    "applicationtypeshortdesc",
    "permitstatusid",
    "permitstatusshortdesc",
    "permitseriesshortdesc",
    "permittypeid",
    "permittypedesc",
    "permitlinearfeet",
    "permittotalsqfeet",
    "permitestimatednumberofcuts",
    "previouspermitnumber",
    "nextpermitnumber",
    "permitissuedate",
    "issuedworkstartdate",
    "issuedworkenddate",
    "boroughname",
    "onstreetname",
    "permitteename"
]

STREET_BATCH_SIZE = 25000
street_raw_path = (
    STREET_OUTPUT_DIR / "street_permits_raw_2023_2025.csv"
)
street_partial_path = street_raw_path.with_suffix(".partial.csv")

# Restart this download cleanly if the cell is rerun.
street_partial_path.unlink(missing_ok=True)
street_downloaded = 0

for offset in range(0, street_expected_rows, STREET_BATCH_SIZE):
    response = street_session.get(
        STREET_API_URL,
        params={
            "$select": ",".join(STREET_COLUMNS),
            "$where": STREET_DATE_FILTER,
            "$order": ":id",
            "$limit": STREET_BATCH_SIZE,
            "$offset": offset
        },
        timeout=180
    )
    response.raise_for_status()
    records = response.json()

    if not isinstance(records, list) or not records:
        raise RuntimeError(
            f"Unexpected or empty API response at offset {offset:,}."
        )

    batch = pd.DataFrame(records).reindex(columns=STREET_COLUMNS)

    batch.to_csv(
        street_partial_path,
        mode="w" if offset == 0 else "a",
        header=(offset == 0),
        index=False
    )

    street_downloaded += len(batch)
    print(
        f"Downloaded {street_downloaded:,} / "
        f"{street_expected_rows:,} rows",
        flush=True
    )

    del records, batch
    time.sleep(0.2)

if street_downloaded != street_expected_rows:
    raise RuntimeError(
        f"Expected {street_expected_rows:,} rows, "
        f"but downloaded {street_downloaded:,}."
    )

street_partial_path.replace(street_raw_path)

print("\nDownload complete.")
print(f"Rows: {street_downloaded:,}")
print(f"Columns: {len(STREET_COLUMNS)}")
print(f"Raw file: {street_raw_path}")
print(f"File size: {street_raw_path.stat().st_size / 1024**2:.1f} MB")

# This cell resumes the download from the existing partial CSV without deleting it.
# It counts saved rows, reads the original column names and requests remaining batches.
# Failed requests are retried; progress stays saved if the API fails again.
# The source is live, so later duplicate and coverage checks remain necessary.

from pathlib import Path
import pandas as pd
import requests
import time

output_dir = Path("/content/task2_outputs")
partial_path = output_dir / "street_permits_raw_2023_2025.partial.csv"
final_path = output_dir / "street_permits_raw_2023_2025.csv"

expected_rows = 1_965_229
batch_size = 25_000

if final_path.exists():
    print("The completed CSV already exists. No download restarted.")

elif not partial_path.exists():
    raise FileNotFoundError(
        "Partial CSV not found. Stop here and send me this output."
    )

else:
    columns = pd.read_csv(partial_path, nrows=0).columns.tolist()

    saved_rows = sum(
        len(chunk)
        for chunk in pd.read_csv(
            partial_path,
            dtype="string",
            chunksize=50_000
        )
    )

    print(f"Saved rows found: {saved_rows:,}", flush=True)

    if saved_rows > expected_rows:
        raise ValueError("Saved count exceeds the expected total.")

    if saved_rows < expected_rows and saved_rows % batch_size != 0:
        raise ValueError(
            "The saved file ends between batches. "
            "Stop here so we can inspect it safely."
        )

    api_url = (
        "https://data.cityofnewyork.us/resource/tqtj-sjs8.json"
    )
    date_filter = (
        "permitissuedate >= '2023-01-01T00:00:00' "
        "AND permitissuedate < '2026-01-01T00:00:00'"
    )

    with requests.Session() as session:
        while saved_rows < expected_rows:
            params = {
                "$select": ",".join(columns),
                "$where": date_filter,
                "$order": ":id",
                "$limit": min(batch_size, expected_rows - saved_rows),
                "$offset": saved_rows
            }

            for attempt in range(6):
                try:
                    response = session.get(
                        api_url, params=params, timeout=(20, 180)
                    )
                    response.raise_for_status()
                    records = response.json()

                    if not isinstance(records, list) or not records:
                        raise ValueError("Unexpected or empty API response.")

                    break

                except (requests.RequestException, ValueError) as error:
                    print(
                        f"Attempt {attempt + 1}/6 failed "
                        f"at {saved_rows:,}: {error}",
                        flush=True
                    )

                    if attempt == 5:
                        raise RuntimeError(
                            "API still unavailable. Saved progress is intact; "
                            "this resume cell can be rerun later."
                        ) from error

                    time.sleep(min(10 * (attempt + 1), 60))

            batch = pd.DataFrame(records).reindex(columns=columns)

            if len(batch) != params["$limit"]:
                raise RuntimeError(
                    "Unexpected batch size. No rows from this batch "
                    "were appended; inspect before continuing."
                )

            # Roll back this batch if writing is interrupted by an exception.
            previous_size = partial_path.stat().st_size
            try:
                batch.to_csv(
                    partial_path, mode="a", header=False, index=False
                )
            except BaseException:
                with partial_path.open("r+b") as handle:
                    handle.truncate(previous_size)
                raise

            saved_rows += len(batch)

            print(
                f"Downloaded {saved_rows:,} / {expected_rows:,}",
                flush=True
            )
            time.sleep(0.5)

    partial_path.replace(final_path)
    print(f"\nDownload complete: {saved_rows:,} rows")
    print(f"Saved to: {final_path}")