# Q3 compares average calendar-month activity in the selected period.
# Each domain is indexed to its own borough mean, with 100 meaning average.
# Selected years must have all 12 matched months for every selected borough.
# One selected year shows its monthly profile, not established seasonality.

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def make_q3_seasonal_chart(data):
    coverage = data.groupby(["borough", "year"])["month"].nunique()

    if coverage.empty or not coverage.eq(12).all():
        raise ValueError("Q3 requires complete years of monthly data.")

    metrics = ["building_permit_count", "street_permit_count"]

    seasonal = (
        data.groupby(["borough", "month"], as_index=False)[metrics]
        .mean()
    )

    boroughs = sorted(seasonal["borough"].unique())
    months = list(range(1, 13))
    labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    figure = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["Building issuances", "Street permits"],
        shared_yaxes=True,
    )

    for position, column in enumerate(metrics, start=1):
        average = seasonal.groupby("borough")[column].transform("mean")

        seasonal["activity_index"] = (
            seasonal[column] / average.where(average > 0) * 100
        )

        matrix = seasonal.pivot(
            index="borough",
            columns="month",
            values="activity_index",
        ).reindex(index=boroughs, columns=months)

        figure.add_trace(
            go.Heatmap(
                z=matrix.to_numpy(),
                x=labels,
                y=boroughs,
                coloraxis="coloraxis",
                hovertemplate=(
                    "%{y}<br>%{x}<br>"
                    "Activity index: %{z:.1f}<extra></extra>"
                ),
            ),
            row=1,
            col=position,
        )

    figure.update_layout(
        title="Q3: Average Calendar-Month Activity in Selected Years",
        coloraxis={
            "colorscale": "RdBu_r",
            "cmid": 100,
            "colorbar": {"title": "Index"},
        },
        template="plotly_white",
        height=450,
        margin={"l": 140},
    )

# Q4 compares building activity with individual street-permit categories.
# Categories are ranked by volume within the selected geographic/time scope.
# Correlations use matched months within each borough, with sample sizes on hover.
# Absent category counts become zero only for months in our validated coverage.
# The function also supports narrowing the comparison to selected categories.

def make_q4_category_chart(data, category_counts, selected_categories=None):
    keys = ["borough", "year", "month"]
    detail_keys = keys + ["permit_category"]

    base = data[keys + ["building_permit_count"]].copy()

    if base.duplicated(keys).any():
        raise ValueError("Q4 requires unique borough-month observations.")

    categories = category_counts.copy()
    categories["borough"] = (
        categories["borough"].astype("string").str.strip().str.upper()
    )
    categories["permit_category"] = (
        categories["permit_category"].astype("string")
    )

    if categories.duplicated(detail_keys).any():
        raise ValueError("Repeated borough-month-category keys.")

    # Restrict category observations to the report's selected months and boroughs.
    categories = categories.merge(
        base[keys],
        on=keys,
        how="inner",
        validate="many_to_one",
    )

    if selected_categories is not None:
        categories = categories.loc[
            categories["permit_category"].isin(selected_categories)
        ]

    top_categories = (
        categories.groupby("permit_category", observed=True)
        ["street_permit_count"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )

    if not top_categories:
        figure = go.Figure()
        figure.add_annotation(
            text="No category activity in the selected scope.",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
        )
        figure.update_layout(template="plotly_white")
        return figure

    grid = base.merge(
        pd.DataFrame({"permit_category": top_categories}),
        how="cross",
    )

    comparison = grid.merge(
        categories.loc[
            categories["permit_category"].isin(top_categories)
        ],
        on=detail_keys,
        how="left",
        validate="one_to_one",
    )

    comparison["street_permit_count"] = (
        comparison["street_permit_count"].fillna(0)
    )

    rows = []

    for (borough, category), group in comparison.groupby(
        ["borough", "permit_category"], observed=True
    ):
        pairs = group.dropna(
            subset=["building_permit_count", "street_permit_count"]
        )

        x = pairs["building_permit_count"].astype(float)
        y = pairs["street_permit_count"].astype(float)

        correlation = (
            x.corr(y)
            if len(pairs) >= 3
            and x.nunique() > 1
            and y.nunique() > 1
            else float("nan")
        )

        rows.append({
            "borough": borough,
            "permit_category": category,
            "pearson_r": correlation,
            "matched_months": len(pairs),
            "active_months": int(y.gt(0).sum()),
        })

    results = pd.DataFrame(rows)
    borough_order = sorted(base["borough"].unique())

    def matrix_for(column):
        return results.pivot(
            index="permit_category",
            columns="borough",
            values=column,
        ).reindex(index=top_categories, columns=borough_order)

    correlations = matrix_for("pearson_r")
    pair_counts = matrix_for("matched_months")
    active_counts = matrix_for("active_months")

    # Each heatmap cell carries its own sample-size information.
    custom_data = [
        [
            [pair_counts.iloc[i, j], active_counts.iloc[i, j]]
            for j in range(len(borough_order))
        ]
        for i in range(len(top_categories))
    ]

    figure = go.Figure(
        go.Heatmap(
            z=correlations.to_numpy(),
            x=borough_order,
            y=top_categories,
            customdata=custom_data,
            colorscale="RdBu_r",
            zmin=-1,
            zmax=1,
            colorbar={"title": "Pearson r"},
            hovertemplate=(
                "%{y}<br>%{x}<br>"
                "Pearson r: %{z:.3f}<br>"
                "Matched months: %{customdata[0]}<br>"
                "Months with category activity: %{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title="Q4: Building–Street Category Correlations Within Boroughs",
        template="plotly_white",
        height=700,
        margin={"l": 340},
    )

    return figure
    