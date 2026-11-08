# This script exports full-dataset results for research questions 7–10.
# Q7 compares borough shares; Q8 calculates street permits per building issuance.
# Q9 compares annual associations; Q10 compares same-month and next-month timing.
# These are descriptive results, not causal or significance-tested conclusions.

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

data = pd.read_csv(
    BASE_DIR / "data" / "integrated_monthly_permits.csv"
)

keys = ["borough", "year", "month"]
metrics = ["building_permit_count", "street_permit_count"]

assert len(data) == 180
assert not data.duplicated(keys).any()
assert data["_merge"].eq("both").all()
assert data[metrics].notna().all().all()
assert data["building_permit_count"].sum() == 408_566
assert data["street_permit_count"].sum() == 1_951_371

data["date"] = pd.to_datetime({
    "year": data["year"],
    "month": data["month"],
    "day": 1,
})


def pearson_result(group):
    x = group["building_permit_count"].astype(float)
    y = group["street_permit_count"].astype(float)

    return (
        x.corr(y)
        if len(group) >= 3
        and x.nunique() > 1
        and y.nunique() > 1
        else float("nan")
    )


# Q7: shares across all five boroughs and all three years.
q7 = data.groupby("borough", as_index=False)[metrics].sum()

q7["building_share_pct"] = (
    q7["building_permit_count"]
    / q7["building_permit_count"].sum()
    * 100
)

q7["street_share_pct"] = (
    q7["street_permit_count"]
    / q7["street_permit_count"].sum()
    * 100
)

q7["share_gap_pp"] = (
    q7["building_share_pct"] - q7["street_share_pct"]
)

q7.to_csv(OUTPUT_DIR / "q7_borough_shares.csv", index=False)


# Q8: annual ratios using complete borough-years.
coverage = data.groupby(["borough", "year"])["month"].nunique()
assert len(coverage) == 15 and coverage.eq(12).all()

q8 = data.groupby(
    ["borough", "year"], as_index=False
)[metrics].sum()

q8["street_per_building"] = (
    q8["street_permit_count"]
    / q8["building_permit_count"].where(
        q8["building_permit_count"] > 0
    )
)

q8.to_csv(OUTPUT_DIR / "q8_annual_ratios.csv", index=False)


# Q9: pooled annual correlations plus within-borough comparisons.
annual_rows = []
borough_year_rows = []

for year, group in data.groupby("year"):
    annual_rows.append({
        "year": year,
        "matched_borough_months": len(group),
        "pearson_r": pearson_result(group),
    })

for (borough, year), group in data.groupby(["borough", "year"]):
    borough_year_rows.append({
        "borough": borough,
        "year": year,
        "matched_months": len(group),
        "pearson_r": pearson_result(group),
    })

q9 = pd.DataFrame(annual_rows)
q9_within = pd.DataFrame(borough_year_rows)

q9.to_csv(OUTPUT_DIR / "q9_year_correlations.csv", index=False)
q9_within.to_csv(
    OUTPUT_DIR / "q9_borough_year_correlations.csv",
    index=False,
)


# Q10: match exact calendar months, including December-to-January pairs.
lag_rows = []

for borough, group in data.groupby("borough"):
    for offset, label in [(0, "Same month"), (1, "Following month")]:
        building = group[["date", "building_permit_count"]].copy()
        building["street_date"] = (
            building["date"] + pd.DateOffset(months=offset)
        )

        street = group[["date", "street_permit_count"]].rename(
            columns={"date": "street_date"}
        )

        pairs = building.merge(
            street,
            on="street_date",
            how="inner",
            validate="one_to_one",
        ).dropna(subset=metrics)

        lag_rows.append({
            "borough": borough,
            "comparison": label,
            "matched_pairs": len(pairs),
            "pearson_r": pearson_result(pairs),
        })

q10 = pd.DataFrame(lag_rows)
q10.to_csv(OUTPUT_DIR / "q10_lag_correlations.csv", index=False)


for title, table in [
    ("Q7 — BOROUGH SHARES", q7),
    ("Q8 — ANNUAL RATIOS", q8),
    ("Q9 — POOLED CORRELATION BY YEAR", q9),
    ("Q10 — SAME-MONTH AND FOLLOWING-MONTH CORRELATIONS", q10),
]:
    print(f"\n{title}")
    print(table.round(4).to_string(index=False))

print(f"\nResults saved to: {OUTPUT_DIR}")