# AI assistance and prompt log

Project: NYC Building and Street Permit Activity, Milestone 1.
Tool: ChatGPT. Period covered: 5–8 November 2026.

## Use of AI

ChatGPT assisted with project interpretation, dataset selection, task planning, Python and Dash code, debugging, cleaning-rule discussion, research-chart implementation, interpretation of real outputs, notebook review, website text, styling and deployment preparation.

The following is a consolidated record of substantive prompts and follow-up requests visible in the project conversation. Excerpts retain the user's wording, including typographical errors. It is not a complete verbatim transcript. Repeated short progress messages and pasted outputs are summarized separately. Notebook-specific prompt records provide additional context.

## Substantive prompt excerpts

| Stage | User prompt excerpt | Assistance provided |
|---|---|---|
| Requirements and planning | “analyse it very thoroughly, then explain everything, distrubute the work over 4 prople” | Analysis of the brief, deliverables, work allocation and effort estimates; allocation subsequently revised to five members. |
| Topic selection | “what do you think is the fastest topic we could go for, choose for us” | Selection of building and street construction permits, 2023–2025 scope and borough-month integration. |
| Team size | “im sorry we are 5 memebers, can you redistribute over 5 people?” | Five-person allocation with ten research questions and ten charts. |
| Task 1 guidance | “im handling tsdk 1, i need you to walk me through step by step” | Colab loading, metadata inspection, extraction, EDA, cleaning, counting, validation and exports. |
| Explanatory comments | “after every code block can you send me a small comment to add at the top?” | Comments explaining notebook and application code for evaluation. |
| Cross-task review | “analyse the 3 things with the project description along with the task list” | Review of submitted notebooks and identification of incomplete real-data integration and synthetic fallback results. |
| Parallel preparation | “is there anything in the meantime to do in the other 2 tasks?” | Reusable chart functions, integration validation and research documentation while extraction continued. |
| Interrupted extraction | “runtime disconnected in the lab 2”; “i get server error 503” | Inspection of saved progress and resumable download code with retries. |
| Final notebook review | Uploaded the three updated notebooks for review | Removal of reset/test/debug code, correction of cell ordering, saved-snapshot loading, syntax checks and local execution checks. |
| Dashboard implementation | “i still didnt receive task 4 or 5 from my friends so i want to start on them” | Step-by-step Dash application development using existing real-data summaries. |
| Code delivery | “can you start sending ful code blocks to copy paste?”; “sned the whole code so i copy paste” | Complete replacement code and callback consolidation. |
| Callback debugging | “Duplicate callback outputs” followed by the application code | Diagnosis of repeated function definitions and replacement with one report callback. |
| Remaining work | “give me the updated list of todos” | Requirement-based completion tracking and verification checklists. |
| Completion and documentation | “we need to finish the project now” | Dependency recording, Git exclusions, research-result export, findings, README and deployment configuration. |
| Team records | “create the files you and ill paste them in the nyc permits file then compress” | Consolidated prompt log and contribution record using supplied member details. |

## Execution-output follow-ups

The user supplied metadata tables, download counts, missing-value summaries, duplicate-key diagnostics, outlier and date checks, cleaning logs, integration coverage, correlation tables, annual growth results, category comparisons and application errors. ChatGPT used these outputs to recommend subsequent steps and draft interpretations rather than treating generated suggestions as observed findings.

## Data integrity and analytical decisions

- Final analytical results use real NYC Open Data records. Synthetic fallback data and hard-coded example correlations in an earlier Task 2 draft were excluded from the final workflow.
- Raw records were inspected before cleaning. Building work-type overlaps were preserved in detail tables while overall counts used distinct analytical issuance keys.
- Missing measurements were not automatically replaced with zero. Missing category counts were assigned zero only within validated covered borough-months.
- Large measurement values and date inconsistencies were flagged and documented; they were not automatically treated as proof of bad permit counts.
- The analytical outputs preserve the distinction between pooled and within-borough associations. No causal effects, statistical significance or forecasting performance are claimed.
- Charts and filters were executed locally. An application import check reported two registered callbacks. Public deployment and live-site verification were not yet established when this log was prepared.

## Verification responsibility

AI-generated code and interpretations require review by the submitting team. The notebooks, source code, saved tables, findings and contribution record document the implemented workflow. This log is an AI-use disclosure, not proof of independent member authorship or completed publication.
