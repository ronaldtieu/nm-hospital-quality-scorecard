# NM Hospital Quality Scorecard — and who it leaves out

A reproducible data pipeline and analysis of hospital quality in New Mexico, built
entirely from free, public CMS, Census, and USDA data. Portfolio project by Ronald Tieu.

The project asks three questions:

1. **Scorecard** — how do NM hospitals perform on readmissions, complications/deaths, and
   patient experience?
2. **Coverage** — how much of New Mexico does the scorecard actually cover? Which
   hospitals, counties, and people have no reportable data, and is that gap concentrated
   in rural NM?
3. **Fair outliers** — which hospitals are true outliers once patient volume is accounted
   for (funnel plots), versus small hospitals that only look extreme by chance?

The answer isn't decided in advance; whatever the data shows is the finding.

## Data

All sources are free and require no login. Raw files are **not** committed (some are
100 MB+ and re-downloadable). Every source URL, release date, and row count is recorded
in [`data/raw/SOURCES.md`](data/raw/SOURCES.md).

| Dataset | Source |
|---|---|
| Hospital General Information | CMS Provider Data Catalog |
| Unplanned Hospital Visits (readmissions) | CMS Provider Data Catalog |
| Complications and Deaths | CMS Provider Data Catalog |
| Patient Survey (HCAHPS) | CMS Provider Data Catalog |
| Footnote Crosswalk | CMS Provider Data Catalog |
| Rural-Urban Commuting Area (RUCA) codes | USDA ERS |
| County population | U.S. Census (Population Estimates) |

## Reproduce

```bash
uv sync                               # create the environment
uv run python src/fetch_data.py       # download raw CMS/USDA files into data/raw/
# then run the notebooks in order (see notebooks/)
```

Running the notebooks regenerates everything under `data/interim/` and
`data/processed/` from the raw files, so none of those tables are committed.

## Pipeline

- **`notebooks/01_explore.ipynb`** — inspect each raw file: grain, columns, missingness,
  and quirks, with a written takeaway per dataset.
- **`notebooks/02_clean.ipynb`** — filter to New Mexico, type every column (Facility ID
  and ZIP kept as text), decode "Not Available" / "Too Few to Report" to missing values
  **with a recorded reason**, join RUCA rural/urban codes, validate with assertions, and
  write analysis-ready tables.
- **`docs/cleaning_log.md`** — every cleaning decision (what, why, rows affected).
- **`docs/data_dictionary.md`** — every column and all 34 CMS measures, in plain language.

Validated outputs: a hospital table (one row per hospital) and a tidy hospital-measure
table (one row per hospital-measure across all sources).

## Repo structure

```
data/raw/         original downloads (git-ignored) + SOURCES.md
data/interim/     NM-filtered, typed tables (regenerated)
data/processed/   analysis-ready tables (regenerated)
notebooks/        numbered pipeline: 01_explore, 02_clean, ...
src/              reusable code (fetch_data.py, ...)
docs/             cleaning_log.md, data_dictionary.md
reports/          figures and findings
```

## Status

- [x] Download data and document every source
- [x] **01 · Explore** — profile all datasets, document missingness
- [x] **02 · Clean** — reproducible NM pipeline → interim + processed tables
- [ ] 03 · Coverage, 04 · Scorecard, 05 · Funnel plots (analysis)
- [ ] One-page findings memo + dashboard

## Principles

- Raw data is read-only; every transformation lives in code so the pipeline re-runs.
- Missingness is never silently dropped — it's decoded to a reason, because *who the
  scorecard leaves out* is a core question.
- Every number in a takeaway is produced by a cell in the same notebook.

## Tools

Python (pandas), `uv` for the environment, Jupyter, matplotlib/seaborn for figures.
