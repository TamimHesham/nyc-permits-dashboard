# This module adds borough-share and street-to-building ratio comparisons.
# Shares use the selected geographic scope; ratios are not measures of adequacy.
# Zero building counts produce an undefined ratio instead of infinity.

import pandas as pd
import plotly.express as px


def make_q7_share_chart(data):
    totals = data.groupby("borough", as_index=False)[
        ["building_permit_count", "street_permit_count"]
    ].sum()

    for column in ["building_permit_count", "street_permit_count"]:
        total = totals[column].sum()
        totals[f"{column}_share"] = (
            totals[column] / total * 100
            if total > 0
            else float("nan")
        )

    chart_data = totals.melt(
        id_vars="borough",
        value_vars=[
            "building_permit_count_share",
            "street_permit_count_share",
        ],
        var_name="series",
        value_name="share_percent",
    )

    chart_data["series"] = chart_data["series"].replace({
        "building_permit_count_share": "Building issuances",
        "street_permit_count_share": "Street permits",
    })

    return px.bar(
        chart_data,
        x="borough",
        y="share_percent",
        color="series",
        barmode="group",
        title="Q7: Borough Shares Within the Selected Scope",
        labels={
            "borough": "Borough",
            "share_percent": "Share of selected-domain total (%)",
            "series": "Permit series",
        },
        template="plotly_white",
    )


def make_q8_ratio_chart(data):
    annual = data.groupby(["borough", "year"], as_index=False)[
        ["building_permit_count", "street_permit_count"]
    ].sum()

    denominator = annual["building_permit_count"].where(
        annual["building_permit_count"] > 0
    )

    annual["street_per_building"] = (
        annual["street_permit_count"] / denominator
    )

    matrix = annual.pivot(
        index="borough",
        columns="year",
        values="street_per_building",
    )

    matrix.columns = matrix.columns.astype(str)

    return px.imshow(
        matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Blues",
        title="Q8: Street Permits per Building Issuance",
        labels={
            "x": "Year",
            "y": "Borough",
            "color": "Ratio",
        },
        template="plotly_white",
    )
# Q9 compares building and street permit activity separately for each year.
# Each point represents one borough-month, with borough shown by color.
# Splitting by year supports comparison but does not control for borough effects.

def make_q9_year_comparison(data):
    chart_data = data.copy()
    chart_data["year"] = chart_data["year"].astype(str)

    return px.scatter(
        chart_data,
        x="building_permit_count",
        y="street_permit_count",
        color="borough",
        facet_col="year",
        facet_col_wrap=3,
        hover_data=["month"],
        title="Q9: Building–Street Permit Relationship by Year",
        labels={
            "building_permit_count": "Building permit issuances",
            "street_permit_count": "Street permit count",
            "borough": "Borough",
            "year": "Year",
        },
        template="plotly_white",
        height=500,
    )
# Q10 compares building activity in month t with street activity in month t
# and month t+1, separately by borough. Exact calendar-month joins prevent
# gaps in selected years from being treated as consecutive months.
# Correlations require at least 3 pairs and variation in both series.
# A stronger lagged association does not establish causation or prediction.

def make_q10_lag_comparison(data):
    monthly = data[
        [
            "borough", "year", "month",
            "building_permit_count", "street_permit_count",
        ]
    ].copy()

    if monthly.duplicated(["borough", "year", "month"]).any():
        raise ValueError("Q10 requires unique borough-month records.")

    monthly["date"] = pd.to_datetime({
        "year": monthly["year"],
        "month": monthly["month"],
        "day": 1,
    })

    results = []

    for borough, group in monthly.groupby("borough"):
        building = group[
            ["date", "building_permit_count"]
        ].copy()

        street = group[
            ["date", "street_permit_count"]
        ].copy()

        for offset, label in [
            (0, "Same month"),
            (1, "Following month"),
        ]:
            pairs = building.copy()
            pairs["street_date"] = (
                pairs["date"] + pd.DateOffset(months=offset)
            )

            pairs = pairs.merge(
                street.rename(columns={"date": "street_date"}),
                on="street_date",
                how="inner",
                validate="one_to_one",
            ).dropna(
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

            results.append({
                "borough": borough,
                "comparison": label,
                "pearson_r": correlation,
                "matched_pairs": len(pairs),
            })

    summary = pd.DataFrame(results)

    figure = px.bar(
        summary,
        x="borough",
        y="pearson_r",
        color="comparison",
        barmode="group",
        hover_data=["matched_pairs"],
        title="Q10: Same-Month versus Following-Month Association",
        labels={
            "borough": "Borough",
            "pearson_r": "Pearson correlation",
            "comparison": "Street permit timing",
            "matched_pairs": "Matched month pairs",
        },
        template="plotly_white",
    )

    figure.update_yaxes(range=[-1, 1])
    figure.add_hline(y=0, line_color="gray", line_width=1)

    if summary["pearson_r"].notna().sum() == 0:
        figure.add_annotation(
            text="Insufficient observations or variation for correlation.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )

    return figure