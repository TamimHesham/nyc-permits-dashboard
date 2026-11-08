# NYC Building and Street Permit Activity

An interactive Dash dashboard exploring relationships between building
permit issuances and street permit activity across NYC's five boroughs
during 2023–2025.

## Research scope

The analysis integrates:
- 408,566 eligible building permit issuances.
- 1,951,371 eligible street permits.
- 180 matched borough-month observations.

The website provides ten research visualizations, borough/year/category
filters, search-driven filter selection and a Generate Report button.

## Data sources

- Building permits:
  https://data.cityofnewyork.us/dataset/rbx6-tga4
- Street construction permits:
  https://data.cityofnewyork.us/d/tqtj-sjs8

## Local setup

Requires Python and the packages listed in requirements.txt.
The development environment used Python 3.14.3.

### Windows PowerShell

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe app.py

Open http://127.0.0.1:8050.

### Linux/macOS

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python app.py

## Using the dashboard

1. Select boroughs and years.
2. Select one building work type or All.
3. Select one street permit category or All.
4. Click Generate Report.

Search recognizes full category names, boroughs and years. Apply Search
updates the dropdowns; Generate Report updates the visualizations.

Example:

    Brooklyn 2023 2024 General Construction Repair Sidewalk

Reset search:

    all boroughs all years all work types all street categories

Unsupported years preserve the existing filters.

## Research questions

1. Are building and street permit counts associated across borough-months?
2. Does that relationship differ between boroughs?
3. Do average peak calendar months coincide?
4. Does the relationship vary across street permit categories?
5. Which boroughs have the most similar relative monthly patterns?
6. Where do annual growth rates diverge most?
7. Do borough shares differ between the two domains?
8. How do street-permit-to-building-issuance ratios vary?
9. Does the relationship differ across years?
10. How do same-month and following-month associations compare?

## Counting and integration

Building issuances use the analytical key:
work permit + sequence number + issued date + borough.

An issuance can cover multiple work types. Overall building totals
must not be reconstructed by summing work-type counts.

Street permits are counted by distinct eligible permit number.

Each dataset is aggregated independently before a one-to-one join on:
borough + year + month.

Category filters affect their respective domains independently.
They do not link individual building and street permits.

Missing category observations are treated as zero recorded eligible
activity only within the validated covered borough-months.

## Reproducing the analysis

The reviewed notebooks document raw-data inspection, cleaning,
aggregation, integration and research analysis.

Use the saved raw-data backups as notebook inputs. The dashboard uses
prepared summaries in data/ and makes no live data requests.

To regenerate Q7–Q10 result tables:

    .\.venv\Scripts\python.exe export_findings.py

Interpretations are documented in FINDINGS.md.

## Deployment

The repository includes render.yaml for a Render Python web service.

- Build command: pip install -r requirements.txt
- Start command:
  gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
- Set PYTHON_VERSION to the tested Python version.

The app exposes its Flask server as app:server.
Gunicorn is installed on non-Windows systems through requirements.txt.

The deployment URL will be added after successful deployment.

## Limitations

Permit counts are not completed construction, new housing supply,
congestion or infrastructure capacity. Renewals, project mix and
administrative processes affect the counts.

Correlations may reflect differences between boroughs, shared trends,
seasonality and serial dependence. They do not establish causation.
No statistical significance or forecasting performance is claimed.

Ratios do not measure infrastructure adequacy.

## Contributions and AI assistance

Actual team contributions and AI prompts are documented in
CONTRIBUTIONS.md and AI_PROMPTS.md.