# This module explains the project's question, data, findings and limitations.
# Findings describe the full 2023–2025 dataset, not the user's current filters.
# The section also explains how NYC planners could use the analysis responsibly.

from dash import dcc, html


def build_story():
    return html.Section(
        [
            html.H2("Do building and street permit activities move together?"),

            html.P(
                "Building projects and work affecting streets share the same "
                "urban space. We investigate whether their recorded permit "
                "activity concentrates in the same boroughs and months."
            ),

            html.H3("The data"),
            html.P(
                "We combined DOB NOW building permits with NYC DOT street "
                "construction permits issued during 2023–2025. After cleaning "
                "and scope exclusions, the analysis includes 408,566 building "
                "issuances and 1,951,371 street permits, aggregated into "
                "180 matched borough-month observations."
            ),

            html.H3("What we found"),
            html.Ul(
                [
                    html.Li(
                        "Across all borough-months, the pooled correlation "
                        "is 0.823. Within individual boroughs, associations "
                        "are much smaller: approximately 0.448 in Queens "
                        "and Brooklyn, 0.347 in Manhattan, 0.182 in the Bronx "
                        "and −0.047 in Staten Island."
                    ),
                    html.Li(
                        "Average calendar-month peaks coincide in March "
                        "for the Bronx and Queens. Building and street "
                        "activity peak in different months in the other "
                        "three boroughs."
                    ),
                    html.Li(
                        "Staten Island shows the largest annual growth "
                        "divergence: in 2024 building issuances rose by "
                        "36.93%, while street permits fell by 2.88%."
                    ),
                    html.Li(
                        "Street categories show different relationships. "
                        "Among the ten highest-volume categories, Staten "
                        "Island sidewalk repair has a correlation of "
                        "−0.623 with building activity, while commercial "
                        "refuse container critical-street permits have "
                        "a correlation of 0.611."
                    ),
                ]
            ),

            html.P(
                "These findings use the full dataset and all categories. "
                "The charts below recalculate for your selected filters.",
                className="story-note",
            ),

            html.H3("What the data cannot tell us"),
            html.P(
                "Permit activity does not measure completed construction, "
                "new homes, congestion or infrastructure capacity. Renewals "
                "and administrative practices affect counts. We match "
                "boroughs and months, not individual permits belonging "
                "to the same project. Shared seasonality, trends and "
                "differences between boroughs may influence correlations. "
                "The analysis does not establish causation or statistical "
                "significance."
            ),

            html.H3("Why this matters for NYC"),
            html.P(
                "City planners and transport agencies could use these "
                "comparisons to identify boroughs, periods and work "
                "categories for closer investigation. Diverging permit "
                "patterns can prompt questions about timing and project "
                "mix; they do not by themselves demonstrate insufficient "
                "infrastructure or poor coordination."
            ),

            html.Details(
                [
                    html.Summary("Data sources and counting rules"),
                    dcc.Markdown(
                        """
- [DOB NOW: Build – Approved Permits](https://data.cityofnewyork.us/dataset/rbx6-tga4)
- [Street Construction Permits](https://data.cityofnewyork.us/d/tqtj-sjs8)

Building issuances use the analytical key: work permit, sequence number,
issuance date and borough. An issuance can cover multiple work types,
so overall building totals are not calculated by summing categories.

Street counts use distinct eligible permit numbers. Cash receipts,
vault licences and ambiguous review/submission statuses were excluded.
Expired records and records voided after issuance remain historical
issuance activity.

Categories filter each domain independently. Ratios compare recorded
counts and are not measures of infrastructure adequacy.
                        """,
                        link_target="_blank",
                    ),
                ]
            ),
        ],
        className="story-section",
        style={
            "background": "white",
            "padding": "24px",
            "borderRadius": "12px",
            "marginBottom": "24px",
            "lineHeight": "1.7",
        },
    )