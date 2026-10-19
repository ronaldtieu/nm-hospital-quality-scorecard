# Data dictionary

Covers the cleaned NM tables built in `02_clean.ipynb`. "Source" = `CMS` for an
original column kept as-is, or `derived` for a column this pipeline created. Raw CMS
columns are kept alongside the derived ones; derived columns use `snake_case`.

## Tables

| Table (in `data/interim/`) | Grain | Rows (NM) |
|---|---|---|
| `hospital_information_nm.csv` | one row per hospital | 45 |
| `unplanned_visits_nm.csv` | one row per hospital × measure | 574 (41 × 14) |
| `complications_death_nm.csv` | one row per hospital × measure | 820 (41 × 20) |
| `hcahps_nm.csv` | one row per hospital × survey item | 2,788 (41 × 68) |

Analysis-ready outputs in `data/processed/` (built in the Save step):

| Table (in `data/processed/`) | Grain | Rows |
|---|---|---|
| `hospitals.csv` | one row per hospital | 45 |
| `hospital_measures.csv` | one row per hospital × measure, all 3 sources | 4,182 |
| `scorecard.csv` | one row per hospital (04 scorecard: stars + CMS domain Better/No-Different/Worse counts) | 45 |
| `targets.csv` | one row per hospital (06 targeting: excess readmissions vs national/NM, $ impact, experience exposure) | 42 |

Four of the 45 hospitals (324010, 324012, 324013, 324014 — all Psychiatric) have no
rows in the two measure files.

## Columns

### Identifiers and location (shared across all tables)

| Column | Type | Meaning | Source |
|---|---|---|---|
| `Facility ID` | text (6-digit) | Hospital identifier. **Join key** across every file. Kept as text so leading zeros survive. | CMS |
| `Facility Name` | text | Hospital name. | CMS |
| `State` | text | Always `NM` after filtering. | CMS |
| `ZIP Code` | text (5-digit) | Hospital ZIP. Join key to RUCA (rural/urban). | CMS |
| `County/Parish` | text | County, uppercase. | CMS |
| `Hospital Type` | text | Incl. `Critical Access Hospitals`, often excluded from national programs. | CMS |
| `is_critical_access` | boolean | `True` when `Hospital Type == "Critical Access Hospitals"` (13 of 45). Flagged because these are often excluded from CMS programs. | derived |
| `Hospital Ownership` | text | Government / non-profit / proprietary / VA. | CMS |

### Measure result columns (`unplanned_visits_nm`, `complications_death_nm`)

| Column | Type | Meaning | Source |
|---|---|---|---|
| `Measure ID` | text | Measure code. See **Measures glossary** below. | CMS |
| `Measure Name` | text | Human-readable measure name. | CMS |
| `score` | numeric | The measure value. Meaning differs by measure (rate, ratio, days) — **compare only within the same `Measure ID`**. `NaN` when CMS suppressed it. | derived from `Score` |
| `denominator` | numeric | Cases/patients the measure is based on (volume). `NaN` when suppressed; also `NaN` for `PSI_90` (a composite with no single denominator). | derived from `Denominator` |
| `lower_estimate`, `higher_estimate` | numeric | CMS 95% interval bounds around the score. `NaN` when suppressed. | derived from `Lower/Higher Estimate` |
| `number_of_patients`, `number_of_patients_returned` | numeric | Readmission patient counts (**`unplanned_visits_nm` only**). `NaN` on EDAC rows, where they don't apply. | derived |
| `comparison_to_national` | category | CMS "compared to national" verdict with `"Not Available"` set to `NA`. Keeps two vocabularies: "…National **Rate**" (rate measures) and "…National **Value**"/"…**expected**" (mortality / EDAC). Unified later in the scorecard. | derived from `Compared to National` |
| `missing_reason` | text | Plain-language reason a value is missing, decoded from `Footnote` via the crosswalk. Present on exactly the rows where `score` is `NaN`. | derived from `Footnote` |
| `start_date`, `end_date` | datetime | Reporting period for that measure. Differs by measure, so stays attached per row. | derived from `Start/End Date` |

Raw `Score`, `Denominator`, `Lower Estimate`, `Higher Estimate`, `Compared to National`,
`Footnote`, `Start Date`, `End Date` are kept unchanged beside their derived versions.

### Hospital table columns (`hospital_information_nm`)

| Column | Type | Meaning | Source |
|---|---|---|---|
| `Hospital overall rating` | text | Raw CMS star rating, incl. `"Not Available"`. | CMS |
| `overall_rating` | numeric (1–5) | Star rating; `NaN` when not rated (22 of 45 NM hospitals). | derived |
| `overall_rating_missing_reason` | text | Why the rating is missing, decoded from the rating footnote. | derived |
| `ruca1` | text | USDA RUCA code (1–10) for the hospital's ZIP, from the RUCA file. | derived (RUCA join) |
| `rural_urban` | category | `ruca1` grouped: metropolitan (1–3), micropolitan (4–6), small town (7–9), rural (10). NM hospitals: 18 metro, 16 micro, 9 small town, 2 rural. | derived (RUCA join) |

### HCAHPS table columns (`hcahps_nm`)

HCAHPS (the patient-experience survey) is stored long: each row is one survey item for
one hospital. Each item is one of three kinds, and only one raw value column applies.

| Column | Type | Meaning | Source |
|---|---|---|---|
| `HCAHPS Measure ID` | text | Survey item code (68 of them), e.g. `H_STAR_RATING`, `H_COMP_1_STAR_RATING`. | CMS |
| `measure_kind` | category | `star` / `linear` / `answer_pct`, from the Measure ID suffix. Says which column holds the real value. | derived |
| `value` | numeric | The item's primary value by kind (1–5 star, linear mean, or 0–100 percent). `NaN` when suppressed. Compare only within the same `HCAHPS Measure ID`. | derived |
| `completed_surveys` | numeric | Number of surveys the hospital completed (volume). Same for all of a hospital's rows. | derived from `Number of Completed Surveys` |
| `response_rate` | numeric | Survey response rate percent. | derived from `Survey Response Rate Percent` |
| `missing_reason` | text | Why `value` is suppressed, decoded from the footnote of that row's primary column. **Linear rows have no CMS footnote column**, so a suppressed linear value has no reason (known exception). | derived |
| `start_date`, `end_date` | datetime | Reporting period; one shared window (2024-10-01 → 2025-09-30). | derived |

The headline patient-experience number for the scorecard is the summary star
(`H_STAR_RATING`, one row per hospital); 26 of 45 NM hospitals have a usable value.

### Processed tables (`data/processed/`)

**`hospitals.csv`** — the hospital spine, one row per hospital (45). Clean `snake_case`
versions of the identifier/attribute columns above, plus `is_critical_access`,
`overall_rating`, `ruca1`, `rural_urban`, and three coverage flags:

| Column | Type | Meaning |
|---|---|---|
| `in_readmission` | boolean | Hospital appears in the readmission file. |
| `in_complications` | boolean | Hospital appears in the complications/deaths file. |
| `in_hcahps` | boolean | Hospital appears in the HCAHPS file. |

(The 4 Psychiatric hospitals are `False` on all three.)

**`hospital_measures.csv`** — one tidy row per hospital-measure across all three
sources (4,182 = 574 + 820 + 2,788):

| Column | Type | Meaning |
|---|---|---|
| `facility_id` | text | Join key to `hospitals.csv`. |
| `source` | category | `readmission` / `complications` / `patient_experience`. |
| `measure_id`, `measure_name` | text | The measure (see glossary; HCAHPS uses its question text). |
| `value` | numeric | The comparable-within-measure number (`score` for readm/comp, `value` for HCAHPS). `NaN` when missing. Compare only within the same `measure_id`. |
| `reported` | boolean | `True` when `value` is present — the backbone of the coverage analysis. |
| `denominator` | numeric | Volume (readmission/complications only; blank for patient experience). |
| `comparison_to_national` | category | CMS verdict (readmission/complications only). |
| `missing_reason` | text | Why `value` is missing (decoded footnote). |
| `start_date`, `end_date` | datetime | Measure reporting period. |
| `hospital_type`, `is_critical_access`, `rural_urban` | — | Joined from `hospitals.csv` for coverage/funnel grouping. |

## Measures glossary

All 34 measures are **adverse-outcome** measures, so **lower is better** for every one
(fewer deaths, readmissions, complications, or safety events). `score` is not comparable
across different `Measure ID`s.

### Unplanned Hospital Visits — `unplanned_visits_nm` (14)

Different ways of asking "did patients come back to the hospital unexpectedly?"

| Measure ID | Meaning | Group |
|---|---|---|
| `READM_30_AMI` | 30-day readmission after a heart attack (AMI) | Readmission rate |
| `READM_30_HF` | 30-day readmission for heart failure | Readmission rate |
| `READM_30_PN` | 30-day readmission for pneumonia | Readmission rate |
| `READM_30_COPD` | 30-day readmission for COPD (chronic lung disease) | Readmission rate |
| `READM_30_CABG` | 30-day readmission after heart bypass surgery (CABG) | Readmission rate |
| `READM_30_HIP_KNEE` | 30-day readmission after hip/knee replacement | Readmission rate |
| `Hybrid_HWR` | Hospital-wide, all-cause 30-day readmission (one overall number) | Readmission rate |
| `EDAC_30_AMI` | Excess days in acute care after a heart attack | EDAC (excess days) |
| `EDAC_30_HF` | Excess days in acute care for heart failure | EDAC (excess days) |
| `EDAC_30_PN` | Excess days in acute care for pneumonia | EDAC (excess days) |
| `OP_32` | Unplanned visits after colonoscopy (per 1,000) | Outpatient |
| `OP_36` | Unplanned visits after outpatient surgery | Outpatient |
| `OP_35_ADM` | Outpatient-chemo patients later admitted to hospital | Outpatient |
| `OP_35_ED` | Outpatient-chemo patients later in the ED | Outpatient |

EDAC counts *extra days* back in acute care vs. expected, not a yes/no readmission.
Negative EDAC = fewer days than expected (good); positive = more (worse).

### Complications and Deaths — `complications_death_nm` (20)

| Measure ID | Meaning | Group |
|---|---|---|
| `MORT_30_AMI` | 30-day death rate, heart attack | Mortality |
| `MORT_30_HF` | 30-day death rate, heart failure | Mortality |
| `MORT_30_PN` | 30-day death rate, pneumonia | Mortality |
| `MORT_30_COPD` | 30-day death rate, COPD | Mortality |
| `MORT_30_STK` | 30-day death rate, stroke | Mortality |
| `MORT_30_CABG` | 30-day death rate, heart bypass surgery (CABG) | Mortality |
| `Hybrid_HWM` | Hospital-wide, all-cause risk-standardized death rate | Mortality |
| `COMP_HIP_KNEE` | Complication rate after hip/knee replacement | Complication |
| `PSI_03` | Pressure ulcer (bedsore) rate | Patient safety (PSI) |
| `PSI_04` | Death rate in surgical patients with treatable complications | Patient safety (PSI) |
| `PSI_06` | Collapsed lung caused by treatment (iatrogenic pneumothorax) | Patient safety (PSI) |
| `PSI_08` | In-hospital fall causing a fracture | Patient safety (PSI) |
| `PSI_09` | Bleeding/hematoma after surgery | Patient safety (PSI) |
| `PSI_10` | Acute kidney injury needing dialysis after surgery | Patient safety (PSI) |
| `PSI_11` | Respiratory failure after surgery | Patient safety (PSI) |
| `PSI_12` | Blood clot (pulmonary embolism / DVT) after surgery | Patient safety (PSI) |
| `PSI_13` | Bloodstream infection (sepsis) after surgery | Patient safety (PSI) |
| `PSI_14` | Surgical wound reopening (dehiscence) | Patient safety (PSI) |
| `PSI_15` | Accidental cut or puncture during a procedure | Patient safety (PSI) |
| `PSI_90` | Composite index combining the PSI safety measures | Patient safety (PSI) |

`PSI_*` are Patient Safety Indicators — avoidable harms that happen *in* the hospital.
`PSI_90` is a weighted composite of the others, so it has no single `denominator`.
