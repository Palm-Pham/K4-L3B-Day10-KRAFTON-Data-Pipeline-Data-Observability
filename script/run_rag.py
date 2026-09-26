from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.config import load_settings
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records
from retrieval.index import LocalEmbeddingIndex
from retrieval.qa import answer_question, answer_question_with_llm


def main() -> None:
    parser = argparse.ArgumentParser(description="Build/search the paper RAG index independently.")
    parser.add_argument(
        "--question",
        default="Summarize 'Data Observability and Quality Gates for Production RAG Systems'.",
    )
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--rebuild", action="store_true", help="Rebuild the baseline index from raw data.")
    parser.add_argument("--llm", action="store_true", help="Generate a grounded answer with the configured LLM.")
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be positive")

    settings = load_settings()
    manifest = settings.paths.embeddings_json
    if args.rebuild or not manifest.exists():
        records = fetch_source_records(settings)
        clean = build_clean_dataframe(records, datetime.now(UTC))
        index = LocalEmbeddingIndex.build(clean, settings)
        print(f"Built {index.collection_name}: {index.collection.count()} papers")
    else:
        index = LocalEmbeddingIndex.load(settings)
        print(f"Loaded {index.collection_name}: {index.collection.count()} papers")

    answer_fn = answer_question_with_llm if args.llm else answer_question
    result = answer_fn(args.question, settings, index, top_k=args.top_k)
    print(f"Question: {result.question}")
    print(f"Answer: {result.answer}")
    print("Retrieved papers:")
    for paper_id, title in zip(result.retrieved_doc_ids, result.retrieved_titles, strict=True):
        print(f"- {paper_id}: {title}")


if __name__ == "__main__":
    main()
