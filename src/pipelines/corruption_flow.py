from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from core.config import load_settings
from core.utils import ensure_parent, read_json, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.crossref import load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    """Execute end-to-end Corruption -> Evaluate -> Repair -> Compare flow."""
    print("=" * 70)
    print("⚡ [Phase 2] Starting Data Corruption, Observability & Idempotent Repair")
    print("=" * 70)

    settings = load_settings()

    # 1. Load Baseline Metrics & Clean Dataset
    print("\n📂 [1/6] Loading Baseline artifacts...")
    if not settings.paths.baseline_metrics.exists() or not settings.paths.clean_json.exists():
        raise FileNotFoundError(
            "Baseline artifacts missing. Please run Phase 1 (script/run_phase1.py) before running corruption flow."
        )

    baseline_metrics = read_json(settings.paths.baseline_metrics)
    baseline_quality = read_json(settings.paths.baseline_quality_report)
    baseline_freshness = read_json(settings.paths.freshness_report)
    clean_df = pd.read_json(settings.paths.clean_json)
    print(f"   -> Loaded baseline metrics (Hit Rate: {baseline_metrics['retrieval_hit_rate'] * 100:.1f}%, F1: {baseline_metrics['mean_token_f1']:.4f})")
    print(f"   -> Loaded clean dataset with {len(clean_df)} records.")

    # 2. Inject Data Corruption (6 Scenarios)
    print("\n☣️  [2/6] Injecting 6 Synthetic Data Corruption Scenarios...")
    corrupted_df = corrupt_clean_dataframe(clean_df, output_log_path=settings.paths.corruption_log)
    ensure_parent(settings.paths.corrupted_clean_csv)
    write_csv(corrupted_df, settings.paths.corrupted_clean_csv)
    ensure_parent(settings.paths.corrupted_clean_json)
    corrupted_df.to_json(settings.paths.corrupted_clean_json, orient="records", indent=2)
    print(f"   -> Saved corrupted dataset ({len(corrupted_df)} records) to CSV & JSON.")
    print(f"   -> Corruption log saved to: {settings.paths.corruption_log}")

    # 3. Build Corrupted Index & Evaluate Degraded RAG Agent
    print(f"\n📉 [3/6] Building corrupted Chroma index '{settings.corrupted_collection_name}' & evaluating...")
    corrupted_index = LocalEmbeddingIndex.build(
        df=corrupted_df,
        settings=settings,
        embeddings_output_path=settings.paths.corrupted_embeddings_json,
    )
    corrupted_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers,
    )
    corrupted_metrics = corrupted_bundle.summary
    corrupted_quality = run_data_quality_checks(corrupted_df, settings=settings, report_name="corrupted")
    corrupted_freshness = build_freshness_report(
        corrupted_df,
        settings=settings,
        report_path=settings.paths.quality_dir / "corrupted_freshness_report.json",
    )
    print(f"   -> Corrupted Hit Rate : {corrupted_metrics['retrieval_hit_rate'] * 100:.1f}%")
    print(f"   -> Corrupted Token F1  : {corrupted_metrics['mean_token_f1']:.4f}")
    print(f"   -> GX 1.x Quality Gate: {'PASSED ✅' if corrupted_quality['success'] else 'FAILED ❌'}")
    print(f"   -> Freshness SLA      : {'PASSED ✅' if corrupted_freshness['is_fresh'] else 'VIOLATED ⚠️'} (Stale ratio: {corrupted_freshness['stale_ratio'] * 100:.1f}%)")

    repair_reasons = []
    if not corrupted_quality["success"]:
        repair_reasons.append("GX quality gate failed")
    if not corrupted_freshness["is_fresh"]:
        repair_reasons.append("Freshness SLA was violated")
    if not repair_reasons:
        raise RuntimeError(
            "Corruption suite did not trigger an observability alert; automatic repair was not started."
        )
    print(f"   -> Auto-repair triggered: {', '.join(repair_reasons)}")

    # 4. Perform Idempotent Repair from Immutable Raw Snapshot
    print("\n🛠️  [4/6] Executing Idempotent Repair from raw snapshot...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    repaired_df = build_clean_dataframe(raw_records, run_date=datetime.now(timezone.utc))
    ensure_parent(settings.paths.repaired_clean_csv)
    write_csv(repaired_df, settings.paths.repaired_clean_csv)
    ensure_parent(settings.paths.repaired_clean_json)
    repaired_df.to_json(settings.paths.repaired_clean_json, orient="records", indent=2)
    print(f"   -> Repaired dataset created ({len(repaired_df)} records) from raw snapshot.")

    # 5. Build Repaired Index & Evaluate Recovered RAG Agent
    print(f"\n📈 [5/6] Building repaired Chroma index '{settings.repaired_collection_name}' & evaluating...")
    repaired_index = LocalEmbeddingIndex.build(
        df=repaired_df,
        settings=settings,
        embeddings_output_path=settings.paths.repaired_embeddings_json,
    )
    repaired_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers,
    )
    repaired_metrics = repaired_bundle.summary
    repaired_quality = run_data_quality_checks(repaired_df, settings=settings, report_name="repaired")
    repaired_freshness = build_freshness_report(
        repaired_df,
        settings=settings,
        report_path=settings.paths.quality_dir / "repaired_freshness_report.json",
    )
    print(f"   -> Repaired Hit Rate  : {repaired_metrics['retrieval_hit_rate'] * 100:.1f}%")
    print(f"   -> Repaired Token F1   : {repaired_metrics['mean_token_f1']:.4f}")
    print(f"   -> GX 1.x Quality Gate: {'PASSED ✅' if repaired_quality['success'] else 'FAILED ❌'}")
    print(f"   -> Freshness SLA      : {'PASSED ✅' if repaired_freshness['is_fresh'] else 'VIOLATED ⚠️'}")

    # 6. Generate 3-State Comparison Markdown Report
    print("\n📋 [6/6] Generating 3-State Comparison Report...")
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_metrics,
        repaired_metrics=repaired_metrics,
        baseline_quality=baseline_quality,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        baseline_freshness=baseline_freshness,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
    )
    print(f"   -> Saved comparison report to: {settings.paths.comparison_report}")

    # Print Comparison Table to Console
    print("\n" + "=" * 70)
    print("📊 BẢNG ĐỐI CHIẾU ĐỊNH LƯỢNG 3 TRẠNG THÁI (BASELINE vs CORRUPTED vs REPAIRED)")
    print("=" * 70)
    print(f"{'Chỉ số / Trạng thái':<26} | {'1. Baseline':<12} | {'2. Corrupted':<12} | {'3. Repaired':<12}")
    print("-" * 70)
    gate = lambda report: "PASSED ✅" if report.get("success") else "FAILED ❌"
    fresh = lambda report: "ĐẠT SLA ✅" if report.get("is_fresh") else "VI PHẠM ⚠️"
    print(f"{'Data Quality Gate (GX 1.x)':<26} | {gate(baseline_quality):<12} | {gate(corrupted_quality):<12} | {gate(repaired_quality):<12}")
    print(f"{'Freshness SLA':<26} | {fresh(baseline_freshness):<12} | {fresh(corrupted_freshness):<12} | {fresh(repaired_freshness):<12}")
    print(f"{'Retrieval Hit Rate':<26} | {baseline_metrics['retrieval_hit_rate']*100:>10.1f}% | {corrupted_metrics['retrieval_hit_rate']*100:>10.1f}% | {repaired_metrics['retrieval_hit_rate']*100:>10.1f}%")
    print(f"{'Mean Token F1':<26} | {baseline_metrics['mean_token_f1']:>11.4f} | {corrupted_metrics['mean_token_f1']:>11.4f} | {repaired_metrics['mean_token_f1']:>11.4f}")
    print(f"{'Judge Accuracy':<26} | {baseline_metrics['judge_accuracy']*100:>10.1f}% | {corrupted_metrics['judge_accuracy']*100:>10.1f}% | {repaired_metrics['judge_accuracy']*100:>10.1f}%")
    print(f"{'Mean Judge Score (1-5)':<26} | {baseline_metrics['mean_judge_score']:>11.2f} | {corrupted_metrics['mean_judge_score']:>11.2f} | {repaired_metrics['mean_judge_score']:>11.2f}")
    print("=" * 70)
    print("\n🎉 [Phase 2] Completed successfully! All comparison artifacts generated.")


if __name__ == "__main__":
    main()
