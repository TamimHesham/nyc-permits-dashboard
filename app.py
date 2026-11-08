# This dashboard explores real building and street permit data for 2023–2025.
# Search applies borough/year filters; Generate Report updates all ten charts.
# Category filters affect each domain independently without duplicating counts.

from pathlib import Path
import re

from story import build_story
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html, no_update

from research_charts import (
    make_q1_chart,
    make_q2_chart,
    make_q5_indexed_trends,
    make_q6_growth_comparison,
)

from additional_charts import (
    make_q7_share_chart,
    make_q8_ratio_chart,
    make_q9_year_comparison,
    make_q10_lag_comparison,
)

from category_charts import (
    make_q3_seasonal_chart,
    make_q4_category_chart,
)


# Load the validated overall and category-level monthly summaries.
BASE_DIR = Path(__file__).resolve().parent
ALL_CATEGORIES = "__ALL__"

data = pd.read_csv(
    BASE_DIR / "data" / "integrated_monthly_permits.csv"
)

street_categories = pd.read_csv(
    BASE_DIR / "data" / "street_monthly_by_category.csv"
)

building_work_types = pd.read_csv(
    BASE_DIR / "data" / "building_monthly_by_work_type.csv"
)

JOIN_KEYS = ["borough", "year", "month"]

assert not data.duplicated(JOIN_KEYS).any()
assert not street_categories.duplicated(
    JOIN_KEYS + ["permit_category"]
).any()
assert not building_work_types.duplicated(
    JOIN_KEYS + ["work_type"]
).any()

boroughs = sorted(data["borough"].unique())
years = sorted(int(year) for year in data["year"].unique())

work_type_options = sorted(
    building_work_types["work_type"].dropna().unique()
)

street_category_options = sorted(
    street_categories["permit_category"].dropna().unique()
)


# Create the Dash application and expose its server for later deployment.
app = Dash(__name__)
server = app.server
app.title = "NYC Permit Activity"

CARD_STYLE = {
    "background": "white",
    "padding": "20px",
    "borderRadius": "12px",
    "marginBottom": "20px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.05)",
}

LABEL_STYLE = {
    "display": "block",
    "marginTop": "16px",
    "marginBottom": "8px",
}

BUTTON_STYLE = {
    "padding": "12px 24px",
    "background": "#173b70",
    "color": "white",
    "border": "none",
    "borderRadius": "8px",
    "cursor": "pointer",
}


# Build the controls and one display container for each research chart.
app.layout = html.Div(
    [
        html.H1("NYC Building & Street Permit Activity"),
        html.P(
            "Explore how recorded permit activity varies across "
            "New York City's boroughs during 2023–2025."
        ),

        html.Div(
            [
                html.Label("Search", htmlFor="search-input"),
                dcc.Input(
                    id="search-input",
                    type="text",
                    placeholder="Example: Brooklyn 2023 2024",
                    debounce=True,
                    style={
                        "width": "70%",
                        "padding": "10px",
                        "margin": "8px 8px 8px 0",
                    },
                ),
                html.Button(
                    "Apply Search",
                    id="apply-search",
                    n_clicks=0,
                    style={"padding": "10px"},
                ),
                html.Div(
                    id="search-feedback",
                    role="status",
                    style={"marginBottom": "16px"},
                ),

                html.Label("Boroughs", style=LABEL_STYLE),
                dcc.Dropdown(
                    id="borough-filter",
                    options=[
                        {"label": borough.title(), "value": borough}
                        for borough in boroughs
                    ],
                    value=boroughs,
                    multi=True,
                ),

                html.Label("Years", style=LABEL_STYLE),
                dcc.Dropdown(
                    id="year-filter",
                    options=[
                        {"label": str(year), "value": year}
                        for year in years
                    ],
                    value=years,
                    multi=True,
                ),

                html.Label("Building work type", style=LABEL_STYLE),
                dcc.Dropdown(
                    id="work-type-filter",
                    options=[
                        {
                            "label": "All building work types",
                            "value": ALL_CATEGORIES,
                        }
                    ] + [
                        {"label": name, "value": name}
                        for name in work_type_options
                    ],
                    value=ALL_CATEGORIES,
                    clearable=False,
                ),

                html.Label("Street permit category", style=LABEL_STYLE),
                dcc.Dropdown(
                    id="street-category-filter",
                    options=[
                        {
                            "label": "All street categories",
                            "value": ALL_CATEGORIES,
                        }
                    ] + [
                        {"label": name, "value": name}
                        for name in street_category_options
                    ],
                    value=ALL_CATEGORIES,
                    clearable=False,
                ),

                html.Button(
                    "Generate Report",
                    id="generate-report",
                    n_clicks=0,
                    style={
                        **BUTTON_STYLE,
                        "marginTop": "20px",
                    },
                ),
            ],
            style=CARD_STYLE,
        ),

        build_story(),

        dcc.Loading(
            children=[
                html.Div(id="report-summary", style=CARD_STYLE),
                *[
                    html.Div(
                        dcc.Graph(id=f"q{number}-chart"),
                        style=CARD_STYLE,
                    )
                    for number in range(1, 11)
                ],
            ]
        ),

        html.P(
            "Counts describe recorded permit issuance activity, including "
            "renewals. They do not measure completed construction or prove "
            "that building activity causes street work."
        ),
    ],
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "32px 20px",
        "fontFamily": "Arial, sans-serif",
        "color": "#172b4d",
        "background": "#f4f6fa",
    },
)


# Display an explanation when a selection cannot support a chart.
def empty_figure(message):
    figure = go.Figure()
    figure.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
    )
    figure.update_layout(
        template="plotly_white",
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    return figure


# Search recognizes boroughs, years and full category names.
# Unspecified filters remain unchanged; "all" phrases reset individual filters.
# Ambiguous category matches are rejected rather than selected arbitrarily.
# Generate Report applies the resulting dropdown selections to the charts.

@app.callback(
    Output("borough-filter", "value"),
    Output("year-filter", "value"),
    Output("work-type-filter", "value"),
    Output("street-category-filter", "value"),
    Output("search-feedback", "children"),
    Input("apply-search", "n_clicks"),
    Input("search-input", "n_submit"),
    State("search-input", "value"),
    State("borough-filter", "value"),
    State("year-filter", "value"),
    State("work-type-filter", "value"),
    State("street-category-filter", "value"),
    prevent_initial_call=True,
)
def apply_search(
    n_clicks,
    n_submit,
    query,
    current_boroughs,
    current_years,
    current_work_type,
    current_street_category,
):
    text = re.sub(r"\s+", " ", (query or "").strip().casefold())

    def reject(message):
        return (
            no_update, no_update, no_update, no_update, message
        )

    if not text:
        return reject(
            "Enter a borough, year or full category name."
        )

    def contains_phrase(phrase):
        normalized = re.sub(
            r"\s+", " ", str(phrase).strip().casefold()
        )
        return bool(
            re.search(
                rf"(?<!\w){re.escape(normalized)}(?!\w)",
                text,
            )
        )

    def category_matches(options):
        matches = [
            option for option in options
            if contains_phrase(option)
        ]

        # Prefer a complete longer name over a shorter name inside it.
        return [
            option for option in matches
            if not any(
                option.casefold() in other.casefold()
                and option != other
                for other in matches
            )
        ]

    found_boroughs = [
        borough for borough in boroughs
        if contains_phrase(borough)
    ]

    found_years = sorted({
        int(value) for value in re.findall(r"\b\d{4}\b", text)
    })

    if set(found_years) - set(years):
        return reject("Available years are 2023, 2024 and 2025.")

    all_boroughs = any(
        contains_phrase(phrase)
        for phrase in ["all boroughs", "citywide", "nyc"]
    )
    all_years = contains_phrase("all years")

    all_work_types = any(
        contains_phrase(phrase)
        for phrase in ["all work types", "all building work types"]
    )
    all_street_categories = contains_phrase("all street categories")

    found_work_types = (
        [] if all_work_types
        else category_matches(work_type_options)
    )
    found_street_categories = (
        [] if all_street_categories
        else category_matches(street_category_options)
    )

    if len(found_work_types) > 1:
        return reject(
            "More than one building work type matched. "
            "Use one full name or the dropdown."
        )

    if len(found_street_categories) > 1:
        return reject(
            "More than one street category matched. "
            "Use one full name or the dropdown."
        )

    recognized = any([
        found_boroughs,
        found_years,
        found_work_types,
        found_street_categories,
        all_boroughs,
        all_years,
        all_work_types,
        all_street_categories,
    ])

    if not recognized:
        return reject(
            "No supported filters found. Try: "
            "Brooklyn 2024 General Construction Repair Sidewalk."
        )

    selected_boroughs = (
        boroughs if all_boroughs
        else found_boroughs if found_boroughs
        else current_boroughs
    )

    selected_years = (
        years if all_years
        else found_years if found_years
        else current_years
    )

    selected_work_type = (
        ALL_CATEGORIES if all_work_types
        else found_work_types[0] if found_work_types
        else current_work_type
    )

    selected_street_category = (
        ALL_CATEGORIES if all_street_categories
        else found_street_categories[0] if found_street_categories
        else current_street_category
    )

    return (
        selected_boroughs,
        selected_years,
        selected_work_type,
        selected_street_category,
        "Recognized filters applied. Unspecified filters are unchanged. "
        "Click Generate Report. Search supports boroughs, years and "
        "full category names; other wording is ignored.",
    )

def apply_search(n_clicks, n_submit, query, current_boroughs, current_years):
    text = re.sub(r"\s+", " ", (query or "").strip().lower())

    if not text:
        return no_update, no_update, "Enter a borough and/or year."

    aliases = {
        "BRONX": ["bronx", "the bronx"],
        "BROOKLYN": ["brooklyn"],
        "MANHATTAN": ["manhattan"],
        "QUEENS": ["queens"],
        "STATEN ISLAND": ["staten island"],
    }

    found_boroughs = [
        borough
        for borough, names in aliases.items()
        if any(
            re.search(rf"\b{re.escape(name)}\b", text)
            for name in names
        )
    ]

    found_years = sorted({
        int(value) for value in re.findall(r"\b\d{4}\b", text)
    })

    if set(found_years) - set(years):
        return (
            no_update,
            no_update,
            "Available years are 2023, 2024 and 2025.",
        )

    all_boroughs = bool(
        re.search(r"\b(all boroughs|citywide|nyc)\b", text)
    )
    all_years = "all years" in text

    if not (found_boroughs or found_years or all_boroughs or all_years):
        return (
            no_update,
            no_update,
            "No supported filters found. Try: Brooklyn 2024.",
        )

    selected_boroughs = (
        boroughs if all_boroughs
        else found_boroughs if found_boroughs
        else current_boroughs
    )

    selected_years = (
        years if all_years
        else found_years if found_years
        else current_years
    )

    return (
        selected_boroughs,
        selected_years,
        "Borough/year filters applied. Click Generate Report. "
        "Use the dropdowns for category selections.",
    )


# Generate all ten charts from the same report selections.
# Single-category summaries are joined onto validated covered months.
# Overall building totals are never reconstructed from overlapping work types.
@app.callback(
    Output("report-summary", "children"),
    Output("q1-chart", "figure"),
    Output("q2-chart", "figure"),
    Output("q3-chart", "figure"),
    Output("q4-chart", "figure"),
    Output("q5-chart", "figure"),
    Output("q6-chart", "figure"),
    Output("q7-chart", "figure"),
    Output("q8-chart", "figure"),
    Output("q9-chart", "figure"),
    Output("q10-chart", "figure"),
    Input("generate-report", "n_clicks"),
    State("borough-filter", "value"),
    State("year-filter", "value"),
    State("work-type-filter", "value"),
    State("street-category-filter", "value"),
)
def generate_report(
    n_clicks,
    selected_boroughs,
    selected_years,
    selected_work_type,
    selected_street_category,
):
    filtered = data.loc[
        data["borough"].isin(selected_boroughs or [])
        & data["year"].isin(selected_years or [])
    ].copy()

    if filtered.empty:
        message = "Select at least one borough and one year."
        return (
            html.P(message),
            *[empty_figure(message) for _ in range(10)],
        )

    if selected_work_type != ALL_CATEGORIES:
        selected_building = building_work_types.loc[
            building_work_types["work_type"].eq(selected_work_type),
            JOIN_KEYS + ["building_permit_count"],
        ]

        filtered = filtered.drop(
            columns="building_permit_count"
        ).merge(
            selected_building,
            on=JOIN_KEYS,
            how="left",
            validate="one_to_one",
        )

        filtered["building_permit_count"] = (
            filtered["building_permit_count"].fillna(0).astype("int64")
        )

    if selected_street_category != ALL_CATEGORIES:
        selected_street = street_categories.loc[
            street_categories["permit_category"].eq(
                selected_street_category
            ),
            JOIN_KEYS + ["street_permit_count"],
        ]

        filtered = filtered.drop(
            columns="street_permit_count"
        ).merge(
            selected_street,
            on=JOIN_KEYS,
            how="left",
            validate="one_to_one",
        )

        filtered["street_permit_count"] = (
            filtered["street_permit_count"].fillna(0).astype("int64")
        )

    fig_q1, q1_summary = make_q1_chart(filtered)
    fig_q2, _ = make_q2_chart(filtered)
    fig_q3 = make_q3_seasonal_chart(filtered)

    q4_categories = (
        None
        if selected_street_category == ALL_CATEGORIES
        else [selected_street_category]
    )

    fig_q4 = make_q4_category_chart(
        filtered,
        street_categories,
        selected_categories=q4_categories,
    )

    fig_q5, _, _ = make_q5_indexed_trends(filtered)

    years_present = set(filtered["year"])
    consecutive = any(
        year + 1 in years_present for year in years_present
    )

    if consecutive:
        try:
            fig_q6, _, _ = make_q6_growth_comparison(filtered)
        except ValueError as error:
            if "No valid consecutive full-year comparisons" not in str(error):
                raise
            fig_q6 = empty_figure(
                "Annual growth is undefined because previous-year "
                "counts are zero."
            )
    else:
        fig_q6 = empty_figure(
            "Select consecutive years to compare annual growth."
        )

    fig_q7 = make_q7_share_chart(filtered)
    fig_q8 = make_q8_ratio_chart(filtered)
    fig_q9 = make_q9_year_comparison(filtered)
    fig_q10 = make_q10_lag_comparison(filtered)

    correlation = q1_summary.iloc[0]["pearson_r"]
    correlation_text = (
        f"{correlation:.3f}"
        if pd.notna(correlation)
        else "Undefined — insufficient observations or variation"
    )

    building_label = (
        "All building work types"
        if selected_work_type == ALL_CATEGORIES
        else selected_work_type
    )
    street_label = (
        "All street categories"
        if selected_street_category == ALL_CATEGORIES
        else selected_street_category
    )

    building_total = int(filtered["building_permit_count"].sum())
    street_total = int(filtered["street_permit_count"].sum())

    summary = [
        html.H3("Selected report"),
        html.P(f"Building scope: {building_label}"),
        html.P(f"Street scope: {street_label}"),
        html.P(f"Borough-month observations: {len(filtered):,}"),
        html.P(f"Building issuances: {building_total:,}"),
        html.P(f"Street permits: {street_total:,}"),
        html.P(f"Pooled Pearson correlation: {correlation_text}"),
        html.P(
            "Categories filter the domains independently. Individual "
            "building and street permits are not linked."
        ),
    ]

    if building_total == 0 or street_total == 0:
        summary.append(
            html.P(
                "One domain has no recorded eligible activity in this "
                "selection. Some correlations, ratios or indices are undefined."
            )
        )

    return (
        summary,
        fig_q1, fig_q2, fig_q3, fig_q4, fig_q5,
        fig_q6, fig_q7, fig_q8, fig_q9, fig_q10,
    )


if __name__ == "__main__":
    app.run(debug=True)