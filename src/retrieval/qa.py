from __future__ import annotations

from dataclasses import dataclass
import re

from core.config import Settings
from core.utils import first_sentence
from retrieval.index import LocalEmbeddingIndex, SearchResult


@dataclass(frozen=True)
class AnswerResult:
    question: str
    answer: str
    retrieved_doc_ids: list[str]
    retrieved_contexts: list[str]
    retrieved_titles: list[str]


def _extract_answer(question: str, top_result: SearchResult) -> str:
    lowered = question.casefold()
    metadata = top_result.metadata
    if re.search(r"\b(authors?|authored|wrote|written by)\b", lowered):
        answer = metadata.get("authors_joined", "")
    elif re.search(r"\b(published|publication date|date of publication)\b", lowered) or "when was" in lowered:
        answer = metadata.get("published", "")
    elif re.search(r"\b(categories|category|subjects?)\b", lowered):
        answer = metadata.get("categories_joined", "")
    else:
        answer = first_sentence(metadata.get("summary", ""))
    return answer or "I don't know from the indexed corpus."


def answer_question(
    question: str,
    settings: Settings,
    index: LocalEmbeddingIndex,
    top_k: int | None = None,
) -> AnswerResult:
    """Return a reproducible metadata answer for evaluation and offline demos."""
    quoted_titles = re.findall(r"'([^']+)'", question)
    if quoted_titles and not any(index.lookup(title) for title in quoted_titles):
        return AnswerResult(
            question=question,
            answer="I don't know from the indexed corpus.",
            retrieved_doc_ids=[],
            retrieved_contexts=[],
            retrieved_titles=[],
        )
    retrieved = index.search(question, top_k=top_k)
    answer = (
        _extract_answer(question, retrieved[0])
        if retrieved else "I don't know from the indexed corpus."
    )
    return AnswerResult(
        question=question,
        answer=answer,
        retrieved_doc_ids=[item.paper_id for item in retrieved],
        retrieved_contexts=[item.content for item in retrieved],
        retrieved_titles=[item.title for item in retrieved],
    )


def answer_question_with_llm(
    question: str,
    settings: Settings,
    index: LocalEmbeddingIndex,
    top_k: int | None = None,
) -> AnswerResult:
    """Generate an answer grounded in retrieved papers, with DOI citations."""
    from retrieval.llm import build_llm

    retrieved = answer_question(question, settings, index, top_k=top_k)
    if not retrieved.retrieved_contexts:
        return retrieved

    context = "\n\n".join(
        f"[{paper_id}] {content}"
        for paper_id, content in zip(
            retrieved.retrieved_doc_ids, retrieved.retrieved_contexts, strict=True
        )
    )
    prompt = (
        "Answer the question using only the paper excerpts below. "
        "If they do not contain enough evidence, say that you do not know. "
        "Cite supporting papers by DOI in square brackets.\n\n"
        f"Question: {question}\n\nPaper excerpts:\n{context}"
    )
    response = build_llm(settings, temperature=0.0).invoke(prompt)
    content = response.content
    if isinstance(content, str):
        answer = content.strip()
    elif isinstance(content, list):
        answer = " ".join(
            part if isinstance(part, str) else str(part.get("text", ""))
            for part in content
        ).strip()
    else:
        answer = str(content).strip()
    return AnswerResult(
        question=question,
        answer=answer or "I don't know from the indexed corpus.",
        retrieved_doc_ids=retrieved.retrieved_doc_ids,
        retrieved_contexts=retrieved.retrieved_contexts,
        retrieved_titles=retrieved.retrieved_titles,
    )
