# NM Hospital Quality Scorecard — and who it leaves out

Portfolio project for Ronald Tieu (UC Berkeley MIDS student, B.S. Computer Science from SFSU, former USMC supply/fiscal Sergeant). Read this file first in every session.

## Why this project exists

Built to show fit for **clinical quality / population health analyst** roles, starting with:
**UnitedHealth Group – Senior Clinical Quality Analyst, New Mexico**
https://careers.unitedhealthgroup.com/job/albuquerque/senior-clinical-quality-analyst-new-mexico/34088/100951045040

What that job asks for, and what this project should demonstrate:
- Analyze clinical quality, utilization and population health data
- Build reports, dashboards, **scorecards** and presentations
- **Validate data, investigate trends and outliers**
- Turn findings into **actionable recommendations** for clinical and operational leaders
- Use **AI tools** to speed up analysis and reporting (a required qualification, so document how AI was used)
- Tools named: SAS, Python, R, Tableau, Power BI, Microsoft Access/VBA

Ronald has no healthcare work experience yet. This project is how he shows he can do the work.

## The question

1. **Scorecard:** how do New Mexico hospitals perform on readmissions, complications/deaths and patient experience?
2. **The question most people miss:** how much of New Mexico does the scorecard actually cover? Which hospitals, counties and people have no reportable data (too few cases, not participating, critical access hospitals excluded), and is that gap concentrated in rural NM?
3. **Fair outliers:** which hospitals are true outliers once patient volume is accounted for (funnel plot), versus small hospitals that only look extreme by chance?

Do not decide the answer in advance. Whatever the data shows is the finding.

## Data (all free, public, no login)

Put downloads in `data/raw/` and never edit them. Record the download date and source URL for each file in `data/raw/SOURCES.md`.

CMS Provider Data Catalog, https://data.cms.gov/provider-data/topics/hospitals (CSV downloads):
| File | Use |
|---|---|
| Hospital General Information | Facility ID, name, ZIP, county, hospital type (incl. Critical Access), ownership, overall star rating |
| Unplanned Hospital Visits – Hospital | 30-day readmission measures (AMI, heart failure, pneumonia, COPD, hip/knee, hospital-wide) with denominators, interval estimates and "compared to national" |
| Complications and Deaths – Hospital | 30-day mortality and complication / patient-safety measures |
| Patient Survey (HCAHPS) – Hospital | Patient experience, star ratings |
| Footnote Crosswalk | Meaning of CMS footnote codes (why a value is missing) |

USDA ERS Rural-Urban Commuting Area (RUCA) codes, ZIP code version:
https://ers.usda.gov/data-products/rural-urban-commuting-area-codes/overview
(ZIP-level copy also at https://familymedicine.uw.edu/rhrc/ruca/)
Grouping: 1–3 metropolitan, 4–6 micropolitan, 7–9 small town, 10 rural.

Optional: Census county population for New Mexico (to say how many people live in counties with no reportable data).

Verify the exact column names after downloading. CMS renames columns between releases.

## Folder layout

```
data/raw/         original downloads (read-only) + SOURCES.md
data/interim/     filtered to NM, typed, not yet joined
data/processed/   analysis-ready tables (one row per hospital, one row per hospital-measure)
notebooks/        exploration, numbered: 01_explore.ipynb, 02_clean.ipynb, ...
src/              reusable cleaning / analysis code
reports/figures/  charts (PNG) used in the memo and dashboard
reports/          memo.md (1-page findings + recommendations)
dashboard/        Tableau Public workbook / exported data for it
docs/             cleaning_log.md, data_dictionary.md, ai_use_log.md
```

## Cleaning checklist (this is a big part of what the project shows)

- Filter every file to `State == "NM"`. Count NM hospitals per file and explain any differences.
- **Facility ID is text.** Keep leading zeros; never let pandas read it as a number. Join all files on it.
- Turn "Not Available", "Too Few to Report" and similar into missing values, **but keep a `missing_reason` column** (decode with the Footnote Crosswalk). Missingness is the core of question 2, so never just drop it.
- Convert scores, denominators and interval estimates from text to numbers. Log anything that fails to parse.
- Make sure measure periods (start/end dates) line up across files. Note any that don't.
- Flag `Hospital Type == "Critical Access Hospitals"`; many are excluded from national programs.
- Join RUCA codes by 5-digit ZIP (also stored as text). Log hospitals whose ZIP has no RUCA match.
- Check: no duplicate hospital-measure rows; one row per hospital in the hospital table.
- Write every decision into `docs/cleaning_log.md` (what, why, how many rows affected).

## Analysis plan

1. **Coverage map (question 2):** for each measure, the share of NM hospitals with a reportable value, broken out by hospital type and RUCA group. Then by county, and by county population if added.
2. **Scorecard (question 1):** one row per hospital with readmission, mortality/complication and HCAHPS results plus CMS's "compared to national" category.
3. **Funnel plots (question 3):** x = volume (denominator), y = rate, with 95% and 99.8% control limits around the state or national rate. Note that CMS readmission rates are risk-standardized model estimates, so the funnel is an approximation. Also use CMS's own interval estimates and compare.
4. **Recommendations:** where a health plan should focus first, and what to use for hospitals CMS can't measure (for example, the plan's own claims data).

## Deliverables

- [ ] Clean, reproducible pipeline (`src/` + notebooks) that rebuilds `data/processed/` from `data/raw/`
- [ ] Coverage chart + scorecard table + funnel plots in `reports/figures/`
- [ ] Tableau Public dashboard (Ronald builds it himself, so he can honestly list Tableau)
- [ ] `reports/memo.md`: 1-page finding, why it matters, 3 recommendations
- [ ] `docs/ai_use_log.md`: how AI tools were used (supports the job's AI requirement)
- [ ] Resume bullets, written only after results exist

## Rules for Claude in this repo

- **Never invent numbers or findings.** Every number in the memo, dashboard or resume bullets must come from a file in `data/processed/` or `reports/`. If something hasn't been run yet, say so.
- Explain things to Ronald in plain language; define technical terms in a few words.
- Raw data is read-only. All changes happen in code, so the pipeline can be rerun.
- Python with pandas (DuckDB for SQL-style queries is fine), matplotlib/seaborn for charts. Use `uv` for the environment.
- Log meaningful AI help in `docs/ai_use_log.md` (date, what was asked, what was kept or changed).
- Don't add tools to the resume that Ronald hasn't actually used here. He has not used Tableau, Power BI, SAS or Snowflake before this project.

## Status

- [ ] Download data and fill in `data/raw/SOURCES.md`
- [ ] 01 explore → 02 clean → 03 coverage → 04 scorecard → 05 funnel plots → memo → dashboard

Note: the target UHG job requires living in New Mexico. That decision is Ronald's; the project is still useful for any health-plan or hospital quality analyst role.
