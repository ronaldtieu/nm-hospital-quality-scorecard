"""Download raw CMS hospital data and USDA RUCA codes into data/raw/.

Reproducible fetch for the NM Hospital Quality Scorecard. CMS rebuilds its CSV
download URLs every annual release, so we never hardcode a CSV link. Instead we
resolve the current download URL from the Provider Data Catalog metastore using
each dataset's *stable* ID, then stamp exactly what we got (URL, release date,
row counts) into data/raw/SOURCES.md.

Raw files are read-only once downloaded. All cleaning happens downstream in code
so the whole pipeline can be rerun from scratch.

Run:  uv run python src/fetch_data.py
"""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
META_ITEM = "https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items/{id}"

# Stable CMS Provider Data Catalog dataset IDs (confirmed 2026-10-05).
# These IDs do not change between releases; the CSV download URL does, which is
# why we resolve it at runtime from the metastore.
CMS_DATASETS = {
    "hospital_general_information": "xubh-q36u",
    "unplanned_hospital_visits": "632h-zaca",  # 30-day readmission measures
    "complications_and_deaths": "ynj2-r877",
    "hcahps_patient_survey": "dgck-syfz",
    "footnote_crosswalk": "y9us-9xdf",
}

# USDA ERS Rural-Urban Commuting Area codes, ZIP-code version (2010 vintage).
RUCA_URL = (
    "https://www.ers.usda.gov/media/5440/"
    "2010-rural-urban-commuting-area-codes-zip-code-file.csv"
)
RUCA_PAGE = "https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes"

HEADERS = {"User-Agent": "nm-hospital-quality-scorecard/1.0 (portfolio project)"}


def resolve_cms_csv(session: requests.Session, dataset_id: str) -> tuple[str, str, str]:
    """Return (title, release_date, csv_download_url) for a CMS dataset."""
    r = session.get(
        META_ITEM.format(id=dataset_id),
        params={"show-reference-ids": "false"},
        timeout=60,
    )
    r.raise_for_status()
    item = r.json()
    title = item.get("title", dataset_id)
    release = item.get("modified", "unknown")
    for dist in item.get("distribution", []):
        # distribution entries may be inline or wrapped in a "data" object
        data = dist.get("data", dist) if isinstance(dist, dict) else {}
        url = data.get("downloadURL", "") or ""
        media = data.get("mediaType", "") or ""
        if url.lower().endswith(".csv") or media == "text/csv":
            return title, release, url
    raise RuntimeError(f"No CSV distribution found for dataset {dataset_id}")


def download(session: requests.Session, url: str, dest: Path) -> int:
    """Download url to dest, return bytes written."""
    r = session.get(url, timeout=600)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return len(r.content)


def summarize(path: Path) -> tuple[int, int | None]:
    """Return (data_row_count, nm_row_count or None if no State column)."""
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        state_col = next((c for c in fields if c.strip().lower() == "state"), None)
        total = 0
        nm = 0 if state_col else None
        for row in reader:
            total += 1
            if state_col and (row.get(state_col) or "").strip().upper() == "NM":
                nm += 1
    return total, nm


def write_sources(records: list[dict], downloaded_on: str) -> None:
    """Rewrite data/raw/SOURCES.md from the records we actually downloaded."""
    lines = [
        "# Data sources",
        "",
        f"All files downloaded on **{downloaded_on}** by `src/fetch_data.py`.",
        "National files; filtered to New Mexico downstream in the pipeline.",
        "Raw files are read-only. Do not edit them by hand.",
        "",
        "| Local file | Dataset | Source URL | Release / vintage | Rows | NM rows |",
        "|---|---|---|---|---|---|",
    ]
    for rec in records:
        nm = "n/a" if rec["nm"] is None else f"{rec['nm']:,}"
        lines.append(
            f"| `{rec['file']}` | {rec['title']} | {rec['url']} | "
            f"{rec['release']} | {rec['rows']:,} | {nm} |"
        )
    lines += [
        "",
        f"RUCA overview page: {RUCA_PAGE}",
        "",
        "## How to reproduce",
        "",
        "```",
        "uv run python src/fetch_data.py",
        "```",
        "",
    ]
    (RAW / "SOURCES.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    downloaded_on = dt.date.today().isoformat()
    session = requests.Session()
    session.headers.update(HEADERS)
    records: list[dict] = []

    for name, dataset_id in CMS_DATASETS.items():
        title, release, url = resolve_cms_csv(session, dataset_id)
        dest = RAW / f"{name}.csv"
        size = download(session, url, dest)
        rows, nm = summarize(dest)
        records.append(
            {"file": dest.name, "title": title, "url": url, "release": release,
             "rows": rows, "nm": nm}
        )
        nm_str = "n/a" if nm is None else f"{nm} NM"
        print(f"  {dest.name:38s} {rows:>7,} rows ({nm_str})  {size/1e6:5.1f} MB")

    # RUCA (direct CSV, no metastore)
    dest = RAW / "ruca_zip_2010.csv"
    size = download(session, RUCA_URL, dest)
    rows, nm = summarize(dest)
    records.append(
        {"file": dest.name, "title": "USDA ERS RUCA codes (ZIP, 2010)",
         "url": RUCA_URL, "release": "2010 (rev. 2019)", "rows": rows, "nm": nm}
    )
    nm_str = "n/a" if nm is None else f"{nm} NM"
    print(f"  {dest.name:38s} {rows:>7,} rows ({nm_str})  {size/1e6:5.1f} MB")

    write_sources(records, downloaded_on)
    print(f"\nWrote {len(records)} files to {RAW} and updated SOURCES.md")


if __name__ == "__main__":
    main()
