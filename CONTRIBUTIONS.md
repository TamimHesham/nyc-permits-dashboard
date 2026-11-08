# Team contributions

Project: NYC Building and Street Permit Activity, Milestone 1.

## Team and original allocation

Names, student IDs and practical groups are recorded as supplied by the team leader. The allocation below identifies responsibility and research-question ownership; it is not a claim that all final code was written independently by the assigned member.

| Task | Member | Student ID | Practical group | Assigned responsibility | Research questions |
|---|---|---|---|---|---|
| 1 | Tameem Hesham | 16008303 | P08 | Building permit extraction, EDA, cleaning, counting rules, exports and analysis | Q1: Overall building/street association; Q2: Association by borough |
| 2 | Mariam El Hosseiny | 13003657 | P008 | Street permit extraction, EDA, cleaning, counting rules, exports and analysis | Q3: Calendar-month peak comparison; Q4: Relationships across street permit categories |
| 3 | Mohamed Nasser | 2005280 | P03 | Monthly integration, post-integration validation, notebook assembly and analysis | Q5: Indexed monthly patterns by borough; Q6: Annual growth divergence |
| 4 | Marwan Mohamed | 16004994 | P001 | Dashboard functionality, dropdowns, search, Generate Report and chart integration | Q7: Borough shares; Q8: Street permits per building issuance |
| 5 | Mohamed Mahmoud | 16008438 | P006 | Website presentation, storytelling, deployment preparation and documentation | Q9: Relationships by year; Q10: Same-month versus following-month associations |

## Final implementation and review record

- Tameem Hesham executed and reviewed the building-data workflow, diagnostic checks, cleaning decisions, monthly summaries and Q1/Q2 results with ChatGPT assistance.
- Draft Task 2 and Task 3 notebooks were supplied for review. The Task 2 draft used synthetic fallback records after an API failure; those data and results were discarded. Its final workflow uses the downloaded real street records.
- Tameem carried out the final street-download recovery, real-data cleaning, integration, chart execution and documentation steps with ChatGPT assistance. The final integrated table contains 180 matched borough-months, preserving 408,566 building issuances and 1,951,371 eligible street permits.
- Tameem implemented and locally tested the final Dash dashboard with ChatGPT assistance, including the ten charts, category and geographic filters, search, Generate Report, story section, styling, and Q7–Q10 result exports. This final implementation extends beyond his original Task 1 allocation; the table above must not be interpreted as exclusive code authorship.
- ChatGPT assisted with code generation, debugging, analytical explanations, notebook reorganization, reusable chart/filter functions and documentation. Real execution outputs were used to support the reported findings.

## Scope of this record

This record reflects the supplied task allocation and implementation activity documented during project preparation. It does not assert unreported independent contributions, teammate approval, successful public deployment or completed submission. GitHub publication, live-site verification and final notebook verification must be recorded after they occur.
