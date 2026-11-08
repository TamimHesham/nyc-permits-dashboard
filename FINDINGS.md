# Research findings: Q7–Q10

Scope: all five NYC boroughs, 2023–2025, all eligible categories.
These findings describe the full dataset; dashboard filters may produce
different results.

## Q7 — Do boroughs have different shares of building and street activity?

Manhattan accounts for 39.38% of building issuances but 26.63% of street
permits: a difference of 12.75 percentage points. It is the only borough
whose building share exceeds its street share.

Brooklyn has the largest street-permit share, at 29.83%, compared with
26.78% of building issuances.

The other boroughs also have larger street shares than building shares.
This shows that the geographic distributions differ. It does not establish
whether street work is sufficient for building development.

The default dashboard compares citywide shares. When boroughs are filtered,
shares are recalculated within the selected scope.

## Q8 — How do street-permit-to-building-issuance ratios vary?

Staten Island has the highest ratio in 2023, at 9.20 street permits per
building issuance. Its ratio falls to 6.52 in 2024 and 5.39 in 2025.

Manhattan has the lowest ratio in each year, remaining near 3.22–3.24.
By 2025, the Bronx has the highest ratio, at 5.95.

Ratios decline from 2023 to 2025 in every borough, although Queens shows
a small increase between 2024 and 2025.

These are ratios of aggregate counts from different permit systems.
They do not mean that a building project receives that number of street
permits, and they do not measure infrastructure adequacy.

## Q9 — Does the relationship differ across years?

The pooled Pearson correlations are:

| Year | Borough-month observations | Pearson r |
|---|---:|---:|
| 2023 | 60 | 0.8068 |
| 2024 | 60 | 0.8240 |
| 2025 | 60 | 0.8413 |

The pooled association is positive in all three years, with a modest
numerical increase over the period.

These correlations combine differences between boroughs with monthly
variation within boroughs. They do not establish that within-borough
alignment improved, or that the differences between years are statistically
meaningful. Separate borough/year correlations are provided in the
supporting export.

## Q10 — Is the association stronger with following-month street activity?

| Borough | Same month, n = 36 | Following month, n = 35 |
|---|---:|---:|
| Bronx | 0.1815 | -0.1369 |
| Brooklyn | 0.4470 | -0.1294 |
| Manhattan | 0.3467 | -0.1220 |
| Queens | 0.4477 | 0.0525 |
| Staten Island | -0.0468 | -0.3859 |

Following-month correlations are numerically lower in all five boroughs.
The results do not support a consistent positive one-month-later
relationship in this dataset.

Staten Island has a larger absolute negative association at the one-month
lag. This is not evidence that building activity causes street permits
to decrease.

The lagged comparison pairs building activity in month t with street
activity in month t+1 using exact calendar months. It has 35 pairs because
January 2026 is outside the analysis period.

The two comparisons use different sample sizes. Seasonality, trends,
serial dependence and administrative timing may influence results.
No forecasting performance or causal effect has been established.

## Shared limitations

- Permit activity does not measure completed construction or new homes.
- Renewals and administrative practices influence counts.
- Individual permits are not linked across the datasets.
- Borough size, project mix and exposure are not controlled for.
- No significance testing or causal identification was performed.
- Findings should guide further investigation rather than automatic policy decisions.

## Supporting files

The results folder contains:
- q7_borough_shares.csv
- q8_annual_ratios.csv
- q9_year_correlations.csv
- q9_borough_year_correlations.csv
- q10_lag_correlations.csv