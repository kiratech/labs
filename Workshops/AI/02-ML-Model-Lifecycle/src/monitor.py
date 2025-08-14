"""
src/monitor.py
Data drift monitoring module using Evidently.

- Compares current data to a reference dataset.
- Generates an HTML and JSON report saved to artifacts/.
- Can be called via CLI or integrated as a Prefect task.
"""

import json
from pathlib import Path

import pandas as pd
import typer
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from src.utils import get_logger
from src.config import CFG

app = typer.Typer(add_completion=False)


def compute_drift(
    output_json: Path = Path(CFG.artifacts_dir / "drift_report.json"),
) -> float:
    """
    Computes the minimum drift score from an Evidently JSON report.

    Args:
        output_json (Path, optional): Path to the JSON drift report (default: artifacts/drift_report.json).

    Returns:
        float: The minimum drift score across all monitored features.
    """
    logger = get_logger()
    logger.info("Computing minimum drift score from report...")

    # Load the JSON report
    report = json.loads(output_json.read_text())
    pvals = []

    # Extract drift scores for each monitored column
    for attribute, value in report["metrics"][1]["result"]["drift_by_columns"].items():
        pvals.append(value["drift_score"])

    # Compute and return the minimum p-value
    min_p = min(pvals)
    logger.info(f"Minimum drift score detected: {min_p}.")
    return min_p


def generate_drift_report(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    output_path_html: Path,
    output_path_json: Path,
) -> Path:
    """
    Generates a drift report comparing current data with reference data.

    Args:
        reference_data (pd.DataFrame): DataFrame containing the reference dataset.
        current_data (pd.DataFrame): DataFrame containing the current dataset to monitor.
        output_path_html (Path): Path to save the generated HTML report.
        output_path_json (Path): Path to save the generated JSON report.

    Returns:
        Path: Path to the generated JSON report (for downstream processing).
    """
    logger = get_logger()
    logger.info("Starting drift report generation...")

    # Initialize Evidently report with DataDriftPreset
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_data, current_data=current_data)

    # Save the report as both HTML and JSON
    output_path_html.parent.mkdir(exist_ok=True)
    report.save_html(str(output_path_html))
    report.save_json(str(output_path_json))
    logger.info(f"Drift report saved to {output_path_html} and {output_path_json}.")
    return output_path_json


def run(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    output_html: Path = Path(CFG.artifacts_dir / "drift_report.html"),
    output_json: Path = Path(CFG.artifacts_dir / "drift_report.json"),
) -> Path:
    """
    CLI entry point for generating a drift report.

    Args:
        reference_data (pd.DataFrame): DataFrame containing the reference dataset.
        current_data (pd.DataFrame): DataFrame containing the current dataset.
        output_html (Path, optional): Output path for the HTML report (default: artifacts/drift_report.html).
        output_json (Path, optional): Output path for the JSON report (default: artifacts/drift_report.json).

    Returns:
        Path: Path to the generated JSON report.
    """
    return generate_drift_report(reference_data, current_data, output_html, output_json)


if __name__ == "__main__":
    app()
