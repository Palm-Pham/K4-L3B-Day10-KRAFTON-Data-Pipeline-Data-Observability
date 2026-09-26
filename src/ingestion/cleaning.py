from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Iterable

import pandas as pd

from core.utils import compact_join, normalize_whitespace
from ingestion.crossref import PaperRecord


def _clean_jats_xml(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    return normalize_whitespace(cleaned)


def _format_text_for_embedding(
    title: str,
    authors_joined: str,
    published: str,
    categories_joined: str,
    summary: str,
) -> str:
    return (
        f"Title: {title}\n"
        f"Authors: {authors_joined}\n"
        f"Published: {published}\n"
        f"Categories: {categories_joined}\n"
        f"Summary: {summary}"
    )


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Clean raw records into a prepared DataFrame ready for embedding."""
    run_d = run_date.date() if isinstance(run_date, datetime) else run_date
    rows = []

    for r in records:
        paper_id = normalize_whitespace(r.paper_id)
        if not paper_id:
            continue

        title = normalize_whitespace(r.title)
        if not title:
            continue

        summary = _clean_jats_xml(r.summary)
        authors = [normalize_whitespace(a) for a in r.authors if normalize_whitespace(a)]
        categories = [normalize_whitespace(c) for c in r.categories if normalize_whitespace(c)]

        authors_joined = compact_join(authors, sep=", ")
        categories_joined = compact_join(categories, sep=", ")
        primary_category = r.primary_category or (categories[0] if categories else "General")

        published = r.published[:10] if r.published else "2026-01-01"
        updated = r.updated[:10] if r.updated else published

        try:
            pub_date = datetime.strptime(published, "%Y-%m-%d").date()
            age_days = max(0, (run_d - pub_date).days)
        except Exception:
            age_days = 0

        text_for_embedding = _format_text_for_embedding(
            title=title,
            authors_joined=authors_joined,
            published=published,
            categories_joined=categories_joined,
            summary=summary,
        )

        rows.append(
            {
                "paper_id": paper_id,
                "title": title,
                "summary": summary,
                "authors": authors,
                "categories": categories,
                "primary_category": primary_category,
                "published": published,
                "updated": updated,
                "abs_url": r.abs_url,
                "pdf_url": r.pdf_url,
                "comment": r.comment,
                "authors_joined": authors_joined,
                "categories_joined": categories_joined,
                "summary_chars": len(summary),
                "age_days": age_days,
                "text_for_embedding": text_for_embedding,
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=["paper_id"], keep="first")
        df = df.sort_values(by=["published", "paper_id"], ascending=[False, True]).reset_index(drop=True)

    return df
