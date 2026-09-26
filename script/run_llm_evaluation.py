from __future__ import annotations

from core.config import load_settings, require_llm_credentials
from evaluation.metrics import evaluate_pipeline
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    settings = load_settings()
    require_llm_credentials(settings)
    index = LocalEmbeddingIndex.load(settings)
    results = settings.paths.baseline_metrics.parent
    bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=results / "llm_baseline_metrics.json",
        answers_output_path=results / "llm_baseline_answers.json",
        answer_mode="llm",
    )
    summary = bundle.summary
    print(
        f"LLM golden evaluation: {summary['samples']} questions, "
        f"Hit@1={summary['retrieval_hit_at_1']:.1%}, "
        f"Hit@4={summary['retrieval_hit_rate']:.1%}, "
        f"F1={summary['mean_token_f1']:.4f}, "
        f"LLM judge={summary['judge_llm_count']}/{summary['samples']}"
    )


if __name__ == "__main__":
    main()
