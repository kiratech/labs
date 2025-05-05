"""
src/pipeline_ml.py
Prefect 2 flows for the Wine Quality ML pipeline.

Flows:
- train_experiment: Performs a grid search (hyperparameter sweep) without saving models.
- train_best: Trains the best model based on MLflow runs and saves the model artifact.
- serve_best: Downloads the best saved model and serves it through a FastAPI endpoint.
"""

from itertools import product
from pathlib import Path
import tempfile

import mlflow
from prefect import flow, task

from src.config import CFG
from src.data import data_collection as data_coll_run, data_preparation as data_prep_run
from src.train import run as train_run
from src.serve import deploy
from src.utils import get_logger

# ---------------------------------------------------------------------------
#  Tasks
# ---------------------------------------------------------------------------

@task
def data_collection_task() -> tuple:
    """
    Collects the dataset (features and labels).

    Returns:
        tuple: (X, y) dataset.
    """
    return data_coll_run()

@task
def data_preparation_task(dataset: tuple) -> tuple:
    """
    Prepares the dataset for training:
    - Fixes feature names.
    - Splits into train/test sets.

    Args:
        dataset (tuple): (X, y) dataset.

    Returns:
        tuple: (X_train, X_test, y_train, y_test).
    """
    return data_prep_run(dataset)

@task
def model_training_task(
    dataset: tuple, n_estimators: int, max_depth: int | None, log_model: bool = False
) -> float:
    """
    Trains a RandomForest model and optionally logs it to MLflow.

    Args:
        dataset (tuple): Prepared train/test splits.
        n_estimators (int): Number of trees.
        max_depth (int | None): Maximum depth per tree.
        log_model (bool): Whether to save model artifact to MLflow.

    Returns:
        float: Model accuracy.
    """
    return train_run(dataset, n_estimators=n_estimators, max_depth=max_depth, log_model=log_model)

@task
def find_best_params_task(metric: str = "accuracy") -> tuple:
    """
    Retrieves the best model hyperparameters from MLflow by specified metric.

    Args:
        metric (str, optional): Metric to order by (default: 'accuracy').

    Returns:
        tuple: (n_estimators, max_depth) for best model.
    """
    logger = get_logger()
    logger.info(f"Searching best hyperparameters by {metric}...")

    runs = mlflow.search_runs(order_by=[f"metrics.{metric} DESC"], max_results=1)
    best = runs.iloc[0]
    params = {
        "n_estimators": int(best["params.n_estimators"]),
        "max_depth": None if best["params.max_depth"] in ("", "None") else int(best["params.max_depth"]),
    }
    logger.info(f"Best hyperparameters found: n_estimators={params['n_estimators']}, max_depth={params['max_depth']}.")
    return params["n_estimators"], params["max_depth"]

@task
def download_best_model(metric: str = "accuracy") -> Path:
    """
    Downloads the best model artifact from MLflow.

    Args:
        metric (str, optional): Metric to order by (default: 'accuracy').

    Returns:
        Path: Local path to downloaded model (.pkl file).
    """
    logger = get_logger()
    logger.info(f"Downloading best model artifact in experiment {CFG.experiment_name}...")

    exp = mlflow.get_experiment_by_name(CFG.experiment_name)
    runs = mlflow.search_runs(
        experiment_ids=[exp.experiment_id], order_by=[f"metrics.{metric} DESC"], max_results=1
    )
    run_id = runs.iloc[0]["run_id"]

    client = mlflow.MlflowClient()
    artifacts = client.list_artifacts(run_id)
    pkl_path = next(a.path for a in artifacts if a.path.endswith(".pkl"))

    tmp_dir = tempfile.mkdtemp()
    local_path = Path(client.download_artifacts(run_id, pkl_path, tmp_dir))
    logger.info(f"Downloaded best model to: {local_path}")
    return local_path

@task
def serve_model_task(model_path: Path):
    """
    Deploys a FastAPI app for model inference.

    Args:
        model_path (Path): Path to serialized model (.pkl).
    """
    deploy(model_path=model_path)

# ---------------------------------------------------------------------------
#  Flows
# ---------------------------------------------------------------------------

@flow(name="train_experiment")
def train_experiment():
    """
    End-to-end grid search training flow:
    - Collects and prepares dataset.
    - Launches multiple model training tasks for different hyperparameters.
    - Only logs parameters and metrics, no model artifacts.
    """
    logger = get_logger()
    logger.info("Starting train_experiment flow...")

    dataset = data_collection_task()
    dataset_prep = data_preparation_task(dataset)

    grid = {
        "n_estimators": [1, 5, 10],
        "max_depth": [None, 5, 10],
    }

    for n_est, m_depth in product(grid["n_estimators"], grid["max_depth"]):
        model_training_task.submit(
            dataset=dataset_prep, n_estimators=n_est, max_depth=m_depth
        )

@flow(name="train_best")
def train_best():
    """
    Retrains the best model based on MLflow search:
    - Finds best hyperparameters.
    - Retrains model and saves it as artifact.
    """
    logger = get_logger()
    logger.info("Starting train_best flow...")

    dataset = data_collection_task()
    dataset_prep = data_preparation_task(dataset)
    n_estimators, max_depth = find_best_params_task()
    model_training_task(
        dataset_prep, n_estimators=n_estimators, max_depth=max_depth, log_model=True
    )

@flow(name="serve_best")
def serve_best():
    """
    Deploys the best model as a live API:
    - Downloads best model from MLflow.
    - Builds FastAPI app.
    - Launches serving.
    """
    logger = get_logger()
    logger.info("Starting serve_best flow...")

    model_path = download_best_model()
    #api = build_app_task(model_path=model_path)
    serve_model_task(model_path)

if __name__ == "__main__":
    import sys
    locals()[sys.argv[1]]()
