from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import first_sentence, write_json


def build_test_set(df: pd.DataFrame, output_path: Path) -> list[dict[str, Any]]:
    """Build standardized benchmark evaluation test set across 4 business question types."""
    if len(df) < 10:
        raise ValueError(f"DataFrame must contain at least 10 documents, found {len(df)}.")

    sample_papers = df.iloc[:10].to_dict(orient="records")
    test_set: list[dict[str, Any]] = []

    # Distribution: 3 summary, 3 authors, 2 date, 2 categories = 10 questions
    types_plan = [
        "summary",
        "authors",
        "date",
        "categories",
        "summary",
        "authors",
        "date",
        "categories",
        "summary",
        "authors",
    ]

    for index, (row, q_type) in enumerate(zip(sample_papers, types_plan, strict=False), start=1):
        title = row["title"]
        paper_id = row["paper_id"]

        if q_type == "summary":
            question = f"Summarize '{title}'."
            ground_truth = first_sentence(row["summary"])
        elif q_type == "authors":
            question = f"Who authored '{title}'?"
            ground_truth = str(row["authors_joined"])
        elif q_type == "date":
            question = f"When was '{title}' published?"
            ground_truth = str(row["published"])
        elif q_type == "categories":
            question = f"What categories does '{title}' belong to?"
            ground_truth = str(row["categories_joined"])
        else:
            question = f"Summarize '{title}'."
            ground_truth = first_sentence(row["summary"])

        test_set.append(
            {
                "id": f"q-{index:02d}",
                "question_type": q_type,
                "question": question,
                "ground_truth": ground_truth,
                "ground_truth_doc_ids": [paper_id],
            }
        )

    write_json(Path(output_path), test_set)
    return test_set
