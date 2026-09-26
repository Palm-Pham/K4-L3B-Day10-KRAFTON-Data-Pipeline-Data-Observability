from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import write_json


# Fixed questions and answers from the supplied 24-paper Crossref snapshot.
# Keep these labels independent of the dataframe being evaluated.
_GOLDEN_CASES = [
    ("summary", "What problem do static benchmarks create for enterprise knowledge bases?",
     "Static benchmarks fail to capture domain drift in enterprise knowledge bases.", "1812"),
    ("authors", "Who wrote the multi-agent debate paper on fact verification?",
     "Phong Vu, Ngan Hoang", "1808"),
    ("date", "When was DOI 10.1145/3637528.3671804 published?",
     "2026-07-05", "1804"),
    ("categories", "Which subject areas classify the paper on fuzzing vector search with corrupted chunks?",
     "Robustness, Information Retrieval", "1807"),
    ("summary", "What problem do orphaned embeddings from soft deletion cause?",
     "Soft-deletions in vector databases leave orphaned embeddings that lead to hallucinations.", "1803"),
    ("authors", "Who wrote the study combining sparse lexical retrieval with dense vectors?",
     "Dat Tran, Lan Pham", "1811"),
    ("date", "What is the publication date of DOI 10.1145/3637528.3671818?",
     "2026-06-06", "1818"),
    ("categories", "What categories apply to DOI 10.1145/3637528.3671809?",
     "Information Retrieval, Natural Language Processing", "1809"),
    ("summary", "What happens to RAG answer faithfulness when data is silently corrupted?",
     "Silent data corruption in RAG pipelines degrades LLM answer faithfulness without throwing runtime errors.", "1802"),
    ("authors", "Who are the authors of the Great Expectations data-quality profiling study?",
     "Son Nguyen, Thuy Doan", "1810"),
]

_NO_ANSWER = "I don't know from the indexed corpus."
_CHALLENGE_CASES = [
    ("authors", "Who authored 'Quantum Potato Retrieval Networks'?"),
    ("date", "When was 'A Completely Unknown Study of Martian Indexes' published?"),
]


def build_test_set(df: pd.DataFrame, output_path: Path) -> list[dict[str, Any]]:
    """Write the fixed 10-question benchmark for the supplied Crossref snapshot."""
    if len(df) < 10:
        raise ValueError(f"DataFrame must contain at least 10 documents, found {len(df)}.")
    available_ids = set(df["paper_id"].astype(str))
    test_set = []
    for index, (question_type, question, ground_truth, suffix) in enumerate(_GOLDEN_CASES, start=1):
        paper_id = f"10.1145/3637528.367{suffix}"
        if paper_id not in available_ids:
            raise ValueError(
                f"Golden paper {paper_id} is missing. Use the supplied raw snapshot "
                "or create a separate benchmark for a refreshed corpus."
            )
        test_set.append({
            "id": f"q-{index:02d}",
            "question_type": question_type,
            "question": question,
            "ground_truth": ground_truth,
            "ground_truth_doc_ids": [paper_id],
        })
    write_json(Path(output_path), test_set)
    return test_set


def build_challenge_set(df: pd.DataFrame, output_path: Path) -> list[dict[str, Any]]:
    """Write two unanswerable questions to verify grounded abstention."""
    titles = set(df["title"].astype(str).str.casefold())
    challenge = []
    for index, (question_type, question) in enumerate(_CHALLENGE_CASES, start=1):
        quoted_title = question.split("'", 2)[1].casefold()
        if quoted_title in titles:
            raise ValueError(f"Challenge title unexpectedly exists in corpus: {quoted_title}")
        challenge.append({
            "id": f"challenge-{index:02d}",
            "question_type": question_type,
            "question": question,
            "ground_truth": _NO_ANSWER,
            "ground_truth_doc_ids": [],
        })
    write_json(Path(output_path), challenge)
    return challenge
