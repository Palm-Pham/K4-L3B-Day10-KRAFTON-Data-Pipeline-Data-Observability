from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd

from core.config import Settings
from core.utils import write_json


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Execute Great Expectations 1.x ephemeral checks and save the quality report."""
    context = gx.get_context(mode="ephemeral")
    data_source_name = f"papers_source_{report_name}"
    data_asset_name = f"papers_asset_{report_name}"
    batch_def_name = f"papers_batch_{report_name}"

    data_source = context.data_sources.add_pandas(name=data_source_name)
    data_asset = data_source.add_dataframe_asset(name=data_asset_name)
    batch_def = data_asset.add_batch_definition_whole_dataframe(batch_def_name)
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})

    suite = gx.ExpectationSuite(name=f"papers_quality_{report_name}")
    suite.add_expectation(gxe.ExpectTableRowCountToBeBetween(min_value=1, max_value=1000))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="paper_id"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="title"))
    suite.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="paper_id"))
    suite.add_expectation(gxe.ExpectColumnValueLengthsToBeBetween(column="title", min_value=8))

    validation_result = batch.validate(suite)

    expectation_results = []
    for item in validation_result.results:
        exp_config = item.expectation_config
        expectation_results.append(
            {
                "expectation_type": exp_config.type if hasattr(exp_config, "type") else str(type(exp_config)),
                "success": bool(item.success),
                "result": item.result,
            }
        )

    summary = {
        "report_name": report_name,
        "success": bool(validation_result.success),
        "total_records": len(df),
        "suite_name": suite.name,
        "evaluated_expectations": len(validation_result.results),
        "successful_expectations": sum(1 for item in validation_result.results if item.success),
        "failed_expectations": sum(1 for item in validation_result.results if not item.success),
        "results": expectation_results,
    }

    if report_name == "baseline":
        output_path = settings.paths.baseline_quality_report
    elif report_name == "corrupted":
        output_path = settings.paths.corrupted_quality_report
    else:
        output_path = settings.paths.quality_dir / f"{report_name}_quality_report.json"

    write_json(output_path, summary)
    return summary


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path: Path) -> dict[str, Any]:
    """Aggregate freshness SLA report based on age_days and publication dates."""
    total_rows = len(df)
    if total_rows == 0:
        summary = {
            "total_rows": 0,
            "latest_published": None,
            "oldest_published": None,
            "stale_rows": 0,
            "fresh_rows": 0,
            "stale_ratio": 0.0,
            "threshold_days": settings.freshness_threshold_days,
            "is_fresh": False,
        }
        write_json(report_path, summary)
        return summary

    published_series = df["published"].dropna().astype(str)
    latest_pub = str(published_series.max()) if not published_series.empty else "N/A"
    oldest_pub = str(published_series.min()) if not published_series.empty else "N/A"

    stale_mask = df["age_days"] > settings.freshness_threshold_days
    stale_rows = int(stale_mask.sum())
    stale_ratio = stale_rows / total_rows
    # SLA: is_fresh = False if ratio of age_days > 180 exceeds 25%
    is_fresh = stale_ratio <= 0.25

    summary = {
        "total_rows": total_rows,
        "latest_published": latest_pub,
        "oldest_published": oldest_pub,
        "stale_rows": stale_rows,
        "fresh_rows": total_rows - stale_rows,
        "stale_ratio": round(stale_ratio, 4),
        "threshold_days": settings.freshness_threshold_days,
        "max_allowed_stale_ratio": 0.25,
        "is_fresh": bool(is_fresh),
    }

    write_json(report_path, summary)
    return summary
