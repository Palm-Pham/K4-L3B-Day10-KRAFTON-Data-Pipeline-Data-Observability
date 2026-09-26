from __future__ import annotations

from datetime import datetime, timezone

from core.config import load_settings
from core.utils import ensure_parent, read_json, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.agent import build_agent, run_agent_question
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    """Run baseline Phase 1 end-to-end pipeline."""
    print("=" * 60)
    print("🚀 [Phase 1] Starting Baseline Data Pipeline & Observability")
    print("=" * 60)

    settings = load_settings()
    run_date = datetime.now(timezone.utc)

    # 1. Fetch / load raw records
    print("📥 [1/7] Fetching scholarly paper records from Crossref...")
    records = fetch_source_records(settings)
    print(f"   -> Loaded {len(records)} raw records.")

    # 2. Clean data & construct text_for_embedding
    print("🧹 [2/7] Cleaning records and constructing text_for_embedding...")
    clean_df = build_clean_dataframe(records, run_date=run_date)
    ensure_parent(settings.paths.clean_csv)
    write_csv(clean_df, settings.paths.clean_csv)
    ensure_parent(settings.paths.clean_json)
    clean_df.to_json(settings.paths.clean_json, orient="records", indent=2)
    print(f"   -> Saved clean dataset ({len(clean_df)} rows) to CSV & JSON.")

    # 3. Build ChromaDB baseline index
    print(f"🧠 [3/7] Building ChromaDB index for collection '{settings.baseline_collection_name}'...")
    index = LocalEmbeddingIndex.build(
        df=clean_df,
        settings=settings,
        embeddings_output_path=settings.paths.embeddings_json,
    )
    print(f"   -> Indexed {len(clean_df)} documents in ChromaDB.")

    # 4. Generate or load evaluation test set
    print("🎯 [4/7] Generating benchmark evaluation test set...")
    if not settings.paths.eval_testset.exists() or settings.refresh_test_set:
        test_set = build_test_set(clean_df, output_path=settings.paths.eval_testset)
        print(f"   -> Generated {len(test_set)} benchmark questions.")
    else:
        test_set = read_json(settings.paths.eval_testset)
        print(f"   -> Loaded existing {len(test_set)} benchmark questions.")

    # 5. Evaluate RAG retrieval & QA performance
    print("📊 [5/7] Evaluating baseline QA and retrieval performance...")
    eval_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )
    summary = eval_bundle.summary
    print(f"   -> Retrieval Hit Rate : {summary['retrieval_hit_rate'] * 100:.1f}%")
    print(f"   -> Mean Token F1       : {summary['mean_token_f1']:.4f}")
    print(f"   -> Judge Accuracy     : {summary['judge_accuracy'] * 100:.1f}%")
    print(f"   -> Mean Judge Score   : {summary['mean_judge_score']:.2f} / 5.0")

    # 6. Run Data Quality Gate (GX 1.x) & Freshness SLA
    print("🛡️ [6/7] Running Data Observability checks (GX 1.x & Freshness)...")
    quality_report = run_data_quality_checks(clean_df, settings=settings, report_name="baseline")
    freshness_report = build_freshness_report(clean_df, settings=settings, report_path=settings.paths.freshness_report)
    print(f"   -> GX 1.x Quality Gate: {'PASSED ✅' if quality_report['success'] else 'FAILED ❌'}")
    print(f"   -> Freshness SLA      : {'PASSED ✅' if freshness_report['is_fresh'] else 'VIOLATED ⚠️'} (Stale ratio: {freshness_report['stale_ratio'] * 100:.1f}%)")

    # 7. Generate Phase 1 markdown report
    print("📝 [7/7] Generating Phase 1 markdown report...")
    source_summary = {
        "source_name": settings.source_api,
        "total_raw": len(records),
        "total_clean": len(clean_df),
        "embedding_model": settings.embedding_model,
        "collection_name": settings.baseline_collection_name,
        "timestamp": run_date.strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    generate_phase1_report(
        report_path=settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=summary,
        quality=quality_report,
        freshness=freshness_report,
    )
    print(f"   -> Report saved to: {settings.paths.baseline_report}")

    # Optional demo question with Agent
    try:
        sample_q = test_set[0]["question"]
        agent = build_agent(settings=settings, index=index)
        demo_resp = run_agent_question(agent, sample_q)
        write_json(
            settings.paths.demo_answers,
            {"sample_question": sample_q, "agent_response": demo_resp},
        )
        print("🤖 Optional agent demo completed successfully.")
    except Exception as exc:
        print(f"ℹ️ Optional agent demo skipped or fell back ({exc}).")

    print("\n✅ [Phase 1] Completed successfully! All artifacts generated.")


if __name__ == "__main__":
    main()
