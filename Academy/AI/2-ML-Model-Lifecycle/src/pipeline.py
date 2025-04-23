# src/pipeline.py
"""Prefect 2 flows:
   • train_sweep     grid-search parallelo (solo metadati)
   • train_best      recupera best hp + addestra salvando modello
   • serve_best      scarica modello migliore e lo serve via FastAPI
"""
from itertools import product
from pathlib import Path
from subprocess import Popen
import tempfile

import mlflow
from prefect import flow, task, get_run_logger

from src.config import CFG
from src.train import run as train_run
from src.serve import run as serve_run

# ---------------------------------------------------------------------------
#  Tasks
# ---------------------------------------------------------------------------


@task
def train_task(n_estimators: int, max_depth: int | None):
    return train_run(n_estimators=n_estimators, max_depth=max_depth, log_model=False)


@task
def find_best_params(metric: str = "accuracy") -> dict:
    logger = get_run_logger()
    runs = mlflow.search_runs(order_by=[f"metrics.{metric} DESC"], max_results=1)
    best = runs.iloc[0]
    params = {
        "n_estimators": int(best["params.n_estimators"]),
        "max_depth": None
        if best["params.max_depth"] in ("", "None")
        else int(best["params.max_depth"]),
    }
    logger.info(f"Best params found: {params}")
    return params


@task
def download_best_model(metric: str = "accuracy") -> Path:
    logger = get_run_logger()
    EXP_ID = mlflow.get_experiment_by_name(CFG.experiment_name).experiment_id
    runs = mlflow.search_runs(
        experiment_ids=[EXP_ID], order_by=[f"metrics.{metric} DESC"], max_results=1
    )
    run_id = runs.iloc[0]["run_id"]

    client = mlflow.MlflowClient()
    art = client.list_artifacts(run_id)
    pkl_path = next(a.path for a in art if a.path.endswith(".pkl"))

    tmp_dir = tempfile.mkdtemp()
    local_path = Path(client.download_artifacts(run_id, pkl_path, tmp_dir))
    logger.info(f"Downloaded best model to: {local_path}")
    return local_path


@task
def serve_model(model_path: Path):
    # Avvia l'API in un processo dedicato (non blocca il flow calling)
    Popen(["python", "-m", "src.serve", "--model-path", str(model_path)])


# ---------------------------------------------------------------------------
#  Flows
# ---------------------------------------------------------------------------


@flow(name="train_sweep")
def train_sweep():
    grid = {
        "n_estimators": [50, 100, 200],
        "max_depth": [None, 5, 10],
    }
    for n_est, m_depth in product(grid["n_estimators"], grid["max_depth"]):
        train_task.submit(n_estimators=n_est, max_depth=m_depth)


@flow(name="train_best")
def train_best():
    params = find_best_params()
    # unpack dict in **kwargs, salva anche il modello
    train_run(**params, log_model=True)


@flow(name="serve_best")
def serve_best():
    model_path = download_best_model()
    serve_model(model_path)


if __name__ == "__main__":
    import sys

    # Facile CLI: python -m src.pipeline <flow-name>
    locals()[sys.argv[1]]()
