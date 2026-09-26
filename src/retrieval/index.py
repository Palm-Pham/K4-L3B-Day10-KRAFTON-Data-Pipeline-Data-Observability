from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import math
import re
from typing import Any

import chromadb
import pandas as pd

from core.config import Settings
from core.utils import read_json, safe_slug, write_json
from retrieval.embeddings import MiniLMEmbeddings


@dataclass(frozen=True)
class SearchResult:
    paper_id: str
    title: str
    score: float
    content: str
    metadata: dict[str, Any]


class LocalEmbeddingIndex:
    def __init__(
        self,
        settings: Settings,
        collection_name: str,
        documents: list[dict[str, Any]],
        persist_path: Path,
    ):
        self.settings = settings
        self.collection_name = collection_name
        self.documents = documents
        self.persist_path = persist_path
        self.embedding_backend = "chroma"
        self.embedding_model = MiniLMEmbeddings(settings.embedding_model)
        self.client = chromadb.PersistentClient(path=str(persist_path))
        self.collection = self.client.get_collection(name=collection_name)
        self.documents_by_paper_id = {document["paper_id"].lower(): document for document in documents}
        self.documents_by_title = {document["title"].lower(): document for document in documents}
        # A small sparse index complements dense search when related papers
        # share almost identical abstracts but differ in title specificity.
        self._lexical_terms: dict[str, Counter[str]] = {}
        self._lexical_lengths: dict[str, int] = {}
        document_frequency: Counter[str] = Counter()
        for paper_id, document in self.documents_by_paper_id.items():
            tokens = self._tokens(
                f"{document['title']} {document['title']} {document['metadata']['summary']}"
            )
            counts = Counter(tokens)
            self._lexical_terms[paper_id] = counts
            self._lexical_lengths[paper_id] = len(tokens)
            document_frequency.update(counts.keys())
        self._document_frequency = document_frequency
        self._lexical_count = len(self._lexical_terms)
        self._average_length = (
            sum(self._lexical_lengths.values()) / self._lexical_count
            if self._lexical_count else 1.0
        )

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.casefold())

    def _bm25_scores(self, query: str) -> dict[str, float]:
        terms = set(self._tokens(query))
        scores: dict[str, float] = {}
        for paper_id, counts in self._lexical_terms.items():
            length = self._lexical_lengths[paper_id]
            score = 0.0
            for term in terms:
                frequency = counts[term]
                if frequency == 0:
                    continue
                document_frequency = self._document_frequency[term]
                idf = math.log(
                    1 + (self._lexical_count - document_frequency + 0.5)
                    / (document_frequency + 0.5)
                )
                score += idf * frequency * 2.2 / (
                    frequency + 1.2 * (0.25 + 0.75 * length / self._average_length)
                )
            scores[paper_id] = score
        return scores

    @staticmethod
    def _build_documents(df: pd.DataFrame) -> list[dict[str, Any]]:
        records = df.to_dict(orient="records")
        documents: list[dict[str, Any]] = []
        for index, row in enumerate(records):
            documents.append(
                {
                    "record_id": f"{row['paper_id']}::{index}",
                    "paper_id": row["paper_id"],
                    "title": row["title"],
                    "content": row["text_for_embedding"],
                    "metadata": {
                        "paper_id": row["paper_id"],
                        "title": row["title"],
                        "published": row["published"],
                        "authors_joined": row["authors_joined"],
                        "categories_joined": row["categories_joined"],
                        "summary": row["summary"],
                        "abs_url": row["abs_url"],
                        "pdf_url": row["pdf_url"],
                    },
                }
            )
        return documents

    @staticmethod
    def _derive_collection_name(settings: Settings, embeddings_output_path: Path | None) -> str:
        if embeddings_output_path is None:
            return settings.baseline_collection_name

        name_map = {
            settings.paths.embeddings_json.resolve(): settings.baseline_collection_name,
            settings.paths.corrupted_embeddings_json.resolve(): settings.corrupted_collection_name,
            settings.paths.repaired_embeddings_json.resolve(): settings.repaired_collection_name,
        }
        resolved_path = embeddings_output_path.resolve()
        if resolved_path in name_map:
            return name_map[resolved_path]
        return safe_slug(embeddings_output_path.stem)

    @classmethod
    def build(
        cls,
        df: pd.DataFrame,
        settings: Settings,
        embeddings_output_path: Path | None = None,
    ) -> "LocalEmbeddingIndex":
        collection_name = cls._derive_collection_name(settings, embeddings_output_path)
        required = {
            "paper_id", "title", "text_for_embedding", "published", "authors_joined",
            "categories_joined", "summary", "abs_url", "pdf_url",
        }
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Cannot build index; missing columns: {sorted(missing)}")
        documents = cls._build_documents(df)
        if not documents or any(
            not str(doc["paper_id"]).strip() or not str(doc["content"]).strip()
            for doc in documents
        ):
            raise ValueError("Cannot build index from empty or invalid documents.")
        # Finish the expensive step before replacing a usable collection.
        embedding_model = MiniLMEmbeddings(settings.embedding_model)
        embeddings = embedding_model.embed_documents(
            [document["content"] for document in documents]
        )
        persist_path = settings.paths.chroma_dir
        persist_path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(persist_path))
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass
        collection = client.create_collection(
            name=collection_name,
            configuration={"hnsw": {"space": "cosine"}},
        )
        collection.add(
            ids=[document["record_id"] for document in documents],
            embeddings=embeddings,
            documents=[document["content"] for document in documents],
            metadatas=[document["metadata"] for document in documents],
        )

        manifest_path = embeddings_output_path or settings.paths.embeddings_json
        write_json(
            manifest_path,
            {
                "backend": "chroma",
                "embedding_model": settings.embedding_model,
                "persist_path": str(persist_path.relative_to(settings.paths.project_dir)),
                "collection_name": collection_name,
                "documents": documents,
            },
        )
        return cls(
            settings=settings,
            collection_name=collection_name,
            documents=documents,
            persist_path=persist_path,
        )

    @classmethod
    def load(cls, settings: Settings, embeddings_path: Path | None = None) -> "LocalEmbeddingIndex":
        payload = read_json(embeddings_path or settings.paths.embeddings_json)
        if payload["embedding_model"] != settings.embedding_model:
            raise ValueError("Index embedding model differs from current settings; rebuild the index.")
        return cls(
            settings=settings,
            collection_name=payload["collection_name"],
            documents=payload["documents"],
            # The repository may contain a manifest written on another machine.
            persist_path=settings.paths.chroma_dir,
        )

    def _exact_documents(self, query: str) -> list[dict[str, Any]]:
        """Find DOI/title mentions, preferring the longest title on overlaps."""
        text = query.casefold()
        matches: list[tuple[int, int, dict[str, Any]]] = []
        for document in self.documents:
            for value in (document["paper_id"], document["title"]):
                match = re.search(
                    r"(?<!\w)" + re.escape(value.casefold()) + r"(?!\w)", text
                )
                if match:
                    matches.append((match.start(), match.end(), document))
        selected: list[tuple[int, int, dict[str, Any]]] = []
        seen_ids: set[str] = set()
        for start, end, document in sorted(matches, key=lambda item: (-(item[1] - item[0]), item[0])):
            if document["paper_id"] in seen_ids:
                continue
            if any(start < old_end and end > old_start for old_start, old_end, _ in selected):
                continue
            selected.append((start, end, document))
            seen_ids.add(document["paper_id"])
        return [document for _, _, document in sorted(selected, key=lambda item: item[0])]

    def search(self, query: str, top_k: int | None = None) -> list[SearchResult]:
        if not query.strip():
            return []
        limit = top_k if top_k is not None else self.settings.top_k
        if limit < 1:
            raise ValueError("top_k must be positive.")
        count = self.collection.count()
        if count == 0:
            return []

        scored: list[SearchResult] = []
        seen_ids: set[str] = set()
        for document in self._exact_documents(query):
            scored.append(SearchResult(
                paper_id=document["paper_id"],
                title=document["title"],
                score=1.0,
                content=document["content"],
                metadata=dict(document["metadata"]),
            ))
            seen_ids.add(document["paper_id"])
            if len(scored) == limit:
                return scored

        query_embedding = self.embedding_model.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(max(limit * 4, 32), count),
            include=["documents", "metadatas", "distances"],
        )
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        candidates: list[SearchResult] = []
        for record_id, content, metadata, distance in zip(
            ids, documents, metadatas, distances, strict=False
        ):
            if not record_id or not metadata or not content:
                continue
            paper_id = str(metadata["paper_id"])
            if paper_id in seen_ids:
                continue
            candidates.append(SearchResult(
                paper_id=paper_id,
                title=str(metadata["title"]),
                score=max(0.0, 1.0 - float(distance or 0.0)),
                content=str(content),
                metadata=dict(metadata),
            ))

        sparse = self._bm25_scores(query)
        max_sparse = max(sparse.values(), default=0.0) or 1.0
        candidates.sort(
            key=lambda item: (
                0.7 * item.score
                + 0.3 * sparse.get(item.paper_id.casefold(), 0.0) / max_sparse,
                item.score,
            ),
            reverse=True,
        )
        for candidate in candidates:
            if candidate.paper_id in seen_ids:
                continue
            scored.append(candidate)
            seen_ids.add(candidate.paper_id)
            if len(scored) == limit:
                break
        return scored

    def lookup(self, value: str) -> dict[str, Any] | None:
        needle = value.strip().lower()
        if needle in self.documents_by_paper_id:
            return self.documents_by_paper_id[needle]
        if needle in self.documents_by_title:
            return self.documents_by_title[needle]
        return None
