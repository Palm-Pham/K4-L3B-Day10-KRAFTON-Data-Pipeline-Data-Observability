from __future__ import annotations

import argparse
import json
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "dashboard"
INDEX_LOCK = Lock()


def read_artifact(relative_path: str):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def overview() -> dict:
    states = {}
    for name in ("baseline", "corrupted", "repaired"):
        states[name] = {
            "metrics": read_artifact(f"data/results/{name}_metrics.json"),
            "quality": read_artifact(f"data/quality/{name}_quality_report.json"),
            "freshness": read_artifact(
                "data/quality/freshness_report.json"
                if name == "baseline" else f"data/quality/{name}_freshness_report.json"
            ),
        }
    return {
        "states": states,
        "challenge": read_artifact("data/results/challenge_metrics.json"),
        "scenarios": read_artifact("data/results/corruption_log.json")["scenarios"],
        "questions": [
            {"id": item["id"], "question": item["question"], "type": item["question_type"]}
            for item in read_artifact("data/eval/test_set.json")
        ],
        "corpus_count": len(read_artifact("data/clean/papers_clean.json")),
        "llm_metrics_available": (ROOT / "data/results/llm_baseline_metrics.json").exists(),
    }


@lru_cache(maxsize=3)
def load_index(state: str):
    from core.config import load_settings
    from retrieval.index import LocalEmbeddingIndex

    settings = load_settings(ROOT)
    manifest = {
        "baseline": settings.paths.embeddings_json,
        "corrupted": settings.paths.corrupted_embeddings_json,
        "repaired": settings.paths.repaired_embeddings_json,
    }[state]
    return settings, LocalEmbeddingIndex.load(settings, manifest)


class DashboardHandler(BaseHTTPRequestHandler):
    def send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, payload: dict, status: int = 200) -> None:
        self.send_bytes(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
            status,
        )

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/overview":
            try:
                self.send_json(overview())
            except (OSError, ValueError) as exc:
                self.send_json({"error": f"Không đọc được artifact: {exc}"}, 500)
            return
        files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/styles.css": ("styles.css", "text/css; charset=utf-8"),
            "/app.js": ("app.js", "application/javascript; charset=utf-8"),
        }
        if path not in files:
            self.send_error(404)
            return
        filename, content_type = files[path]
        self.send_bytes((STATIC / filename).read_bytes(), content_type)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/answer":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                raise ValueError("Yêu cầu quá dài hoặc rỗng.")
            data = json.loads(self.rfile.read(length))
            question = str(data.get("question", "")).strip()
            state = str(data.get("state", "baseline"))
            if state not in {"baseline", "corrupted", "repaired"}:
                raise ValueError("Trạng thái không hợp lệ.")
            if not 3 <= len(question) <= 500:
                raise ValueError("Câu hỏi cần từ 3 đến 500 ký tự.")
            from retrieval.qa import answer_question

            with INDEX_LOCK:
                settings, index = load_index(state)
                result = answer_question(question, settings, index)
            self.send_json({
                "answer": result.answer,
                "state": state,
                "sources": [
                    {"doi": doi, "title": title}
                    for doi, title in zip(
                        result.retrieved_doc_ids, result.retrieved_titles, strict=True
                    )
                ],
                "mode": "metadata",
            })
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, 400)
        except Exception as exc:
            self.send_json({"error": f"Truy xuất thất bại: {exc}"}, 500)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local presentation dashboard")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DashboardHandler)
    print(f"Dashboard: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
