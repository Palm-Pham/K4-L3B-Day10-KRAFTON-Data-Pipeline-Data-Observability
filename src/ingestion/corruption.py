from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import ensure_parent, write_json


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


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path: Path | str) -> pd.DataFrame:
    """Simulate 6 realistic data corruption scenarios on clean dataframe.

    Scenarios:
    1. Drop latest records (remove ~20% newest records).
    2. Blank summary (clear summary for several papers).
    3. Inject noise (insert garbage characters into summary).
    4. Truncate title (truncate titles to < 8 characters).
    5. Stale date (shift published dates to past to violate Freshness SLA).
    6. Duplicate rows (duplicate records to violate uniqueness constraint).
    """
    corrupted_df = df.copy()
    original_count = len(corrupted_df)
    scenarios_log: list[dict[str, Any]] = []

    # 1. Drop latest records (20% of newest records)
    drop_count = max(1, int(len(corrupted_df) * 0.2))
    # df is sorted by published descending
    dropped_papers = corrupted_df.iloc[:drop_count]["paper_id"].tolist()
    corrupted_df = corrupted_df.iloc[drop_count:].copy().reset_index(drop=True)
    scenarios_log.append(
        {
            "scenario": "drop_latest_records",
            "description": f"Dropped {drop_count} newest records (~20%)",
            "affected_paper_ids": dropped_papers,
        }
    )

    # 2. Blank summary (rows 0, 1)
    blank_targets = []
    for idx in [0, 1]:
        if idx < len(corrupted_df):
            pid = corrupted_df.at[idx, "paper_id"]
            corrupted_df.at[idx, "summary"] = ""
            corrupted_df.at[idx, "summary_chars"] = 0
            blank_targets.append(pid)
    scenarios_log.append(
        {
            "scenario": "blank_summary",
            "description": "Cleared summary text for target papers",
            "affected_paper_ids": blank_targets,
        }
    )

    # 3. Inject noise into summary (rows 2, 3)
    noise_targets = []
    noise_prefix = "[CORRUPTED_NOISE_###!@#_MALFORMED] "
    for idx in [2, 3]:
        if idx < len(corrupted_df):
            pid = corrupted_df.at[idx, "paper_id"]
            current_sum = corrupted_df.at[idx, "summary"]
            corrupted_df.at[idx, "summary"] = noise_prefix + str(current_sum)
            corrupted_df.at[idx, "summary_chars"] = len(corrupted_df.at[idx, "summary"])
            noise_targets.append(pid)
    scenarios_log.append(
        {
            "scenario": "inject_noise",
            "description": "Injected random corrupt noise string into summary",
            "affected_paper_ids": noise_targets,
        }
    )

    # 4. Truncate title < 8 characters (rows 4, 5)
    truncate_targets = []
    for idx in [4, 5]:
        if idx < len(corrupted_df):
            pid = corrupted_df.at[idx, "paper_id"]
            corrupted_df.at[idx, "title"] = "Bad"
            truncate_targets.append(pid)
    scenarios_log.append(
        {
            "scenario": "truncate_title",
            "description": "Truncated paper title to 'Bad' (< 8 chars) to fail length check",
            "affected_paper_ids": truncate_targets,
        }
    )

    # 5. Stale date (shift dates back by > 400 days on 8 rows to breach 25% stale SLA threshold)
    stale_targets = []
    for idx in range(min(8, len(corrupted_df))):
        pid = corrupted_df.at[idx, "paper_id"]
        corrupted_df.at[idx, "published"] = "2024-01-01"
        corrupted_df.at[idx, "age_days"] = 999
        stale_targets.append(pid)
    scenarios_log.append(
        {
            "scenario": "stale_date",
            "description": "Shifted publication dates to 2024-01-01 (age_days=999) to violate Freshness SLA",
            "affected_paper_ids": stale_targets,
        }
    )

    # 6. Duplicate rows (duplicate first 2 rows)
    dupe_rows = corrupted_df.iloc[:2].copy()
    corrupted_df = pd.concat([corrupted_df, dupe_rows], ignore_index=True)
    scenarios_log.append(
        {
            "scenario": "duplicate_rows",
            "description": f"Duplicated {len(dupe_rows)} records to violate uniqueness constraint",
            "duplicated_paper_ids": dupe_rows["paper_id"].tolist(),
        }
    )

    # 7. Rebuild text_for_embedding for all rows in corrupted dataframe
    corrupted_df["text_for_embedding"] = corrupted_df.apply(
        lambda row: _format_text_for_embedding(
            title=str(row["title"]),
            authors_joined=str(row.get("authors_joined", "")),
            published=str(row["published"]),
            categories_joined=str(row.get("categories_joined", "")),
            summary=str(row["summary"]),
        ),
        axis=1,
    )

    log_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "original_record_count": original_count,
        "corrupted_record_count": len(corrupted_df),
        "scenarios": scenarios_log,
    }

    path = Path(output_log_path)
    ensure_parent(path)
    write_json(path, log_payload)

    return corrupted_df
