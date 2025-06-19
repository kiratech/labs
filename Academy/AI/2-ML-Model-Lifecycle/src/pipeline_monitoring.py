"""
src/pipeline_monitoring.py
Prefect 2 flows for the Wine Quality ML pipeline.

Flow:
- monitoring_best: Detects data drift and triggers retraining if significant drift is found.
"""

import pandas as pd
from pathlib import Path

from prefect import flow, task
from src.data import data_collection as data_coll_run, new_data_collection as new_data_coll_run
from src.monitor import run as monitoring_run, compute_drift
from src.pipeline_ml import train_best
from src.utils import get_logger

# ---------------------------------------------------------------------------
#  Tasks
# ---------------------------------------------------------------------------

@task
def data_collection_task() -> tuple:
    """
    Collects the original reference dataset.

    Returns:
        tuple: (X, y) dataset.
    """
    return data_coll_run()

@task
def get_drift_data_task() -> pd.DataFrame:
    """
    Generates a new dataset with simulated data drift.

    Returns:
        pd.DataFrame: New batch of data with potential drift.
    """
    return new_data_coll_run()

@task 
def create_drift_report_task(current_data: pd.DataFrame, reference_data: pd.DataFrame) -> Path:
    """
    Creates a drift monitoring report comparing current batch vs reference.

    Args:
        current_data (pd.DataFrame): Current dataset batch.
        reference_data (pd.DataFrame): Original reference dataset.

    Returns:
        Path: Path to the generated JSON drift report.
    """
    return monitoring_run(current_data=current_data, reference_data=reference_data)

@task
def compute_drift_task(output_json: Path) -> float:
    """
    Computes the minimum drift score from the JSON report.

    Args:
        output_json (Path): Path to the generated JSON report.

    Returns:
        float: Minimum p-value detected across all features.
    """
    return compute_drift(output_json)

@task
def trigger_if_drift_task(min_p: float, threshold: float = 0.05):
    """
    Triggers retraining if minimum drift p-value is below the threshold.

    Args:
        min_p (float): Minimum p-value detected.
        threshold (float, optional): Threshold below which retraining is triggered (default: 0.05).
    """
    logger = get_logger()
    logger.info("Starting monitoring_best flow...")

    if min_p <= threshold:
        logger.warning(f"Drift detected (min_p={min_p}). Launching retraining...")
        train_best()               
    else:
        logger.warning(f"No drift detected (min_p={min_p}).")

# ---------------------------------------------------------------------------
#  Flows
# ---------------------------------------------------------------------------

@flow(name="monitoring_best")
def monitoring_best():
    """
    Drift monitoring flow:
    - Collects reference and new batch datasets.
    - Generates drift report (HTML + JSON).
    - Computes drift metrics.
    - Triggers model retraining if drift is significant.
    """
    logger = get_logger()
    logger.info("Starting monitoring_best flow...")

    training_data, _ = data_collection_task()
    new_data = get_drift_data_task()
    report_json = create_drift_report_task(current_data=new_data, reference_data=training_data)
    p_val = compute_drift_task(report_json)
    trigger_if_drift_task(min_p=p_val)

if __name__ == "__main__":
    # Serve this flow with a cron schedule (here: every minute)
    monitoring_best.serve(cron="* * * * *")
