# Data sources

All files downloaded on **2026-10-05** by `src/fetch_data.py`.
National files; filtered to New Mexico downstream in the pipeline.
Raw files are read-only. Do not edit them by hand.

| Local file | Dataset | Source URL | Release / vintage | Rows | NM rows |
|---|---|---|---|---|---|
| `hospital_general_information.csv` | Hospital General Information | https://data.cms.gov/provider-data/sites/default/files/resources/893c372430d9d71a1c52737d01239d47_1785189955/Hospital_General_Information.csv | 2026-07-22 | 5,419 | 45 |
| `unplanned_hospital_visits.csv` | Unplanned Hospital Visits - Hospital | https://data.cms.gov/provider-data/sites/default/files/resources/30edc1d0417a34b58affcc2495a02b0a_1790013959/Unplanned_Hospital_Visits-Hospital.csv | 2026-09-10 | 67,060 | 574 |
| `complications_and_deaths.csv` | Complications and Deaths - Hospital | https://data.cms.gov/provider-data/sites/default/files/resources/6af7c44d77436e5a1caac3ce39a83fe9_1790013956/Complications_and_Deaths-Hospital.csv | 2026-09-10 | 95,800 | 820 |
| `hcahps_patient_survey.csv` | Patient survey (HCAHPS) - Hospital | https://data.cms.gov/provider-data/sites/default/files/resources/78a50346fbe828ea0ce2837847af6a7c_1785189950/HCAHPS-Hospital.csv | 2026-07-22 | 325,720 | 2,788 |
| `footnote_crosswalk.csv` | Footnote Crosswalk | https://data.cms.gov/provider-data/sites/default/files/resources/f29bb7c812e242f6edfef0a4b7d0eaca_1760630713/Footnote_Crosswalk.csv | 2025-09-18 | 32 | n/a |
| `ruca_zip_2010.csv` | USDA ERS RUCA codes (ZIP, 2010) | https://www.ers.usda.gov/media/5440/2010-rural-urban-commuting-area-codes-zip-code-file.csv | 2010 (rev. 2019) | 41,164 | 429 |
| `census_county_population.csv` | Census Population Estimates (county totals) | https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv | 2024 estimate (downloaded 2026-10-17) | 3,195 | 33 NM counties |

RUCA overview page: https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes

## How to reproduce

```
uv run python src/fetch_data.py
```
