# NYC Building and Street Permit Activity

An interactive data visualization project exploring the relationship between building permit issuances and street construction permits across New York City's five boroughs during 2023–2025.

## Live Website

https://tameemhesham.pythonanywhere.com/

## GitHub Repository

https://github.com/TamimHesham/nyc-permits-dashboard

## Project Overview

The project combines two official NYC Open Data datasets to investigate whether building permit activity and street permit activity move together.

The validated integrated dataset contains:

- **408,566** eligible building permit issuances.
- **1,951,371** eligible street permits.
- **180** matched borough-month observations.
- Five boroughs and 36 months covering January 2023 through December 2025.

The website includes ten interactive research visualizations, four dropdown filters, text search, a Generate Report button, and a story section explaining findings and limitations.

## Official Data Sources

### Building Permits

**DOB NOW: Build – Approved Permits**

- Dataset ID: `rbx6-tga4`
- Link: https://data.cityofnewyork.us/dataset/rbx6-tga4
- Source columns: 46.
- Selected columns: 20.
- Downloaded records issued during 2023–2025: 484,414.
- Eligible detail rows after cleaning: 481,189.
- Distinct eligible issuances: 408,566.

### Street Permits

**Street Construction Permits (2022 – Present)**

- Dataset ID: `tqtj-sjs8`
- Link: https://data.cityofnewyork.us/d/tqtj-sjs8
- Source columns: 39.
- Selected columns: 20.
- Downloaded records issued during 2023–2025: 1,965,229.
- Eligible permits after cleaning: 1,951,371.

The analysis uses issuance dates to define the study period.

## Research Questions

1. Are building and street permit counts associated across borough-months?
2. Does the relationship differ between boroughs?
3. Do average peak calendar months coincide?
4. Does the relationship vary across street permit categories?
5. Which boroughs have the most similar relative monthly patterns?
6. Where do annual growth rates diverge most?
7. Do borough shares differ between the two domains?
8. How do street-permit-to-building-issuance ratios vary by borough and year?
9. Does the relationship differ across years?
10. How do same-month and following-month associations compare?

## Cleaning and Integration

Cleaning includes text standardization, date and numeric conversion, duplicate checks, missing-value assessment, eligibility screening, and checks for unusual measurements and date sequences.

Unusual values are reviewed or flagged rather than automatically removed. Cleaning decisions and audit outputs are documented in the notebooks and supporting CSV files.

### Building Counting Method

A building issuance is identified using:

`work_permit + sequence_number + issued_date + borough`

One issuance can cover multiple work types. Therefore, work-type counts overlap and must not be summed to reconstruct the overall building total.

### Street Counting Method

Street activity is counted using distinct eligible permit numbers. Eligibility rules and exclusions are documented in the street permits notebook.

### Integration Method

The two sources are aggregated independently and joined one-to-one using:

`borough + year + month`

This supports comparison at a shared geographic and temporal level without attempting to match individual permits.

Validation confirmed:

- All 180 borough-month groups matched.
- No duplicate join keys.
- No missing building or street counts.
- Both source totals were preserved.

Category filters affect their respective domains independently. Missing category counts are treated as zero recorded eligible activity only within validated covered borough-months.

## Repository Contents

- `app.py`: Dashboard layout, filtering, search, and callbacks.
- `research_charts.py`: Q1, Q2, Q5, and Q6 visualizations.
- `category_charts.py`: Q3 and Q4 visualizations.
- `additional_charts.py`: Q7–Q10 visualizations.
- `story.py`: Research story, findings, limitations, and NYC relevance.
- `permit_data_utils.py`: Supporting data utilities.
- `check_setup.py`: Data and setup validation.
- `export_findings.py`: Exports Q7–Q10 result tables.
- `original_api_extraction.py`: Original extraction code retained for provenance.
- `notebooks/`: Building cleaning, street cleaning, and integration notebooks.
- `data/`: Prepared summaries, validation results, and cleaning audit tables.
- `results/`: Exported research result tables.
- `assets/style.css`: Dashboard styling.
- `requirements.txt`: Dependency snapshot from the local development environment.
- `FINDINGS.md`: Additional research interpretations.
- `CONTRIBUTIONS.md`: Detailed contribution record.
- `AI_PROMPTS.md`: AI assistance and prompts.
- `render.yaml`: Optional Render configuration; the live website uses PythonAnywhere.

## Local Setup

The original Windows development environment used Python 3.14.3. The deployed app also passed setup and import checks using Python 3.13.1 on PythonAnywhere.

### Windows PowerShell

```powershell
# Create an environment, install dependencies, and run the dashboard.
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

### Linux or macOS

```bash
# Create an environment, install dependencies, and run the dashboard.
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Open:

http://127.0.0.1:8050/

The requirements file records the original development versions. If those versions are unavailable for your Python version, the PythonAnywhere deployment used a separate environment with:

```bash
# Install the dashboard's direct dependencies for the available Python version.
python -m pip install dash plotly pandas
```

## Setup Validation

Run these commands inside the activated environment:

```bash
# Validate the prepared data and confirm that the dashboard imports.
python check_setup.py
python -c "from app import app; print('App import passed'); print('Registered callbacks:', len(app.callback_map))"
```

Expected results include:

- Setup passed with 180 monthly groups and correct permit totals.
- App import passed.
- Two registered callbacks.

## Using the Dashboard

1. Select one or more boroughs.
2. Select one or more years.
3. Select a building work type or All.
4. Select a street permit category or All.
5. Click **Generate Report** to update all ten charts.

Text search applies recognized terms to the dropdown filters. Click **Generate Report** afterward to update the charts.

Example search:

`Brooklyn 2024`

More detailed example:

`Brooklyn 2023 2024 General Construction Repair Sidewalk`

Reset search:

`all boroughs all years all work types all street categories`

Search supports recognized boroughs, years, and full category names. Unsupported years preserve the existing selection.

Some analyses require specific conditions. Annual growth requires consecutive years, and correlations require sufficient observations and variation. The dashboard displays explanatory messages when a calculation is undefined.

## PythonAnywhere Deployment

The live application is hosted on PythonAnywhere using Python 3.13 and a virtual environment.

### 1. Download the Repository

```bash
# Clone the project and enter its directory.
git clone https://github.com/TamimHesham/nyc-permits-dashboard.git
cd nyc-permits-dashboard
```

### 2. Create the Environment

```bash
# Create the deployment environment and install dashboard dependencies.
python3.13 -m venv ~/.virtualenvs/nyc-permits
source ~/.virtualenvs/nyc-permits/bin/activate
python -m pip install --no-cache-dir dash plotly pandas
python check_setup.py
```

### 3. Configure the Web App

In PythonAnywhere's Web tab:

1. Add a web app using **Manual configuration**.
2. Select **Python 3.13**.
3. Set the virtualenv path to:

`/home/TameemHesham/.virtualenvs/nyc-permits`

Replace `TameemHesham` with your own username if deploying another copy.

### 4. Configure WSGI

Use the following WSGI configuration:

```python
# Expose the Dash application's Flask server to PythonAnywhere.
import sys

project_path = "/home/TameemHesham/nyc-permits-dashboard"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

from app import server as application
```

Save the configuration, reload the web app, and open its public URL.

The website reads prepared CSV summaries included in the repository. It does not download the original datasets during startup.

### 5. Publish Updates

```bash
# Retrieve committed updates on PythonAnywhere.
cd ~/nyc-permits-dashboard
git pull
```

Reload the web app from PythonAnywhere's Web tab after updating application files.

## Reproducing the Analysis

The notebooks document source inspection, EDA, cleaning, aggregation, integration, and research analysis.

The full raw-data backups are separate from this repository. Obtain the saved building and street raw-data backups from the team before running notebook cells that require them. Follow the input-loading instructions in each notebook.

The dashboard itself runs using the included summaries and does not require the raw backups.

To regenerate Q7–Q10 result tables inside an activated environment:

```bash
# Recalculate and save the additional research findings.
python export_findings.py
```

Generated tables are saved in `results/`. Interpretations are documented in `FINDINGS.md`.

## Findings and Limitations

The pooled relationship is positive, while within-borough relationships are weaker and vary between boroughs. This distinction matters because pooled results can reflect differences in borough activity levels.

Permit counts do not directly measure completed construction, new housing supply, congestion, or infrastructure capacity. Renewals, project mix, and administrative processes influence the counts.

Correlations may reflect borough differences, shared trends, seasonality, and serial dependence. They do not establish causation. No statistical significance or forecasting performance is claimed.

Street-permit-to-building-issuance ratios describe relative permit activity, not infrastructure adequacy. Individual building and street permits are not linked.

## Team and Work Allocation

| Member | Student ID | Tutorial | Assigned responsibility |
|---|---|---|---|
| Tameem Hesham | 16008303 | P08 | Task 1: Building permits preparation |
| Mariam El Hosseiny | 13003657 | P008 | Task 2: Street permits preparation |
| Mohamed Nasser | 2005280 | P03 | Task 3: Integration and analysis |
| Marwan Mohamed | 16004994 | P001 | Task 4: Interactive dashboard |
| Mohamed Mahmoud | 16008438 | P006 | Task 5: Storytelling and final delivery |

This table records the task allocation. The detailed record of completed contributions, including Tameem's AI-assisted corrections and final implementation work, is provided in `CONTRIBUTIONS.md`.

## AI Assistance

AI assistance was used during development, debugging, documentation, and interpretation. Prompts and usage details are recorded in `AI_PROMPTS.md`.