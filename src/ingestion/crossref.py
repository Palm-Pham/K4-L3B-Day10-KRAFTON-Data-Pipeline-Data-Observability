from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any
import requests

from core.config import Settings
from core.utils import normalize_whitespace, read_json, write_json


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _clean_abstract(raw: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", raw)
    return normalize_whitespace(cleaned)


def _format_date(date_parts: list[int] | None) -> str:
    if not date_parts:
        return "2026-01-01"
    year = date_parts[0] if len(date_parts) > 0 else 2026
    month = date_parts[1] if len(date_parts) > 1 else 1
    day = date_parts[2] if len(date_parts) > 2 else 1
    return f"{year:04d}-{month:02d}-{day:02d}"


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref payload to a list of PaperRecord."""
    items = payload.get("message", {}).get("items", [])
    records: list[PaperRecord] = []

    for item in items:
        paper_id = item.get("DOI", "").strip()
        if not paper_id:
            continue

        raw_title = item.get("title", [""])
        title = raw_title[0] if isinstance(raw_title, list) and raw_title else str(raw_title)
        title = normalize_whitespace(title)

        raw_abstract = item.get("abstract", "")
        summary = _clean_abstract(raw_abstract)

        authors: list[str] = []
        for author in item.get("author", []):
            given = author.get("given", "").strip()
            family = author.get("family", "").strip()
            name = normalize_whitespace(f"{given} {family}".strip())
            if not name and "name" in author:
                name = normalize_whitespace(str(author["name"]).strip())
            if name:
                authors.append(name)

        categories = [normalize_whitespace(cat) for cat in item.get("subject", []) if cat]
        primary_category = categories[0] if categories else "Computer Science"

        pub_parts = item.get("published", {}).get("date-parts", [[]])[0]
        published = _format_date(pub_parts) if pub_parts else "2026-01-01"

        created_dt = item.get("created", {}).get("date-time", "")
        updated = created_dt[:10] if created_dt else published

        url = item.get("URL", f"https://doi.org/{paper_id}")
        pdf_url = url
        for link in item.get("link", []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL", url)
                break

        comment = f"Crossref record {paper_id}"

        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=url,
                pdf_url=pdf_url,
                comment=comment,
            )
        )

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Fetch source API records with fallback to local snapshot."""
    payload: dict[str, Any] | None = None

    if settings.refresh_source:
        url = "https://api.crossref.org/works"
        params = {
            "query": settings.source_query,
            "filter": settings.source_filter,
            "rows": settings.max_results,
            "mailto": "student@vinuni.edu.vn",
        }
        for attempt in range(3):
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    payload = response.json()
                    write_json(settings.paths.raw_api_response, payload)
                    break
            except Exception:
                continue

    if payload is None:
        if settings.paths.raw_api_response.exists():
            payload = read_json(settings.paths.raw_api_response)
        elif settings.paths.raw_records_json.exists():
            return load_raw_records(settings.paths.raw_records_json)
        else:
            raise FileNotFoundError("Neither raw API response nor raw records snapshot exists.")

    records = parse_crossref_payload(payload)
    write_json(settings.paths.raw_records_json, [asdict(r) for r in records])
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Load JSON snapshot and map into list of PaperRecord."""
    raw_data = read_json(path)
    records: list[PaperRecord] = []
    for item in raw_data:
        records.append(PaperRecord(**item))
    return records
