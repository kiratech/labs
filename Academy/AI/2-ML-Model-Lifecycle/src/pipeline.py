import subprocess
from prefect import flow
from itertools import product
import mlflow, tempfile, subprocess

# -----------------------------------------------------------
# 1) sweep: lancia molti train con log_model=False
@flow
def train_sweep():
    params_grid = {
        "n_estimators": [50, 100, 200, 400],
        "max_depth":   [None, 5, 10],
    }
    for n_est, d in product(params_grid["n_estimators"], params_grid["max_depth"]):
        train.with_options(name=f"rf_ne{n_est}_md{d}").submit(
            n_estimators=n_est, max_depth=d, log_model=False
        )

# 2) train_best: sceglie il run con max accuracy e salva il modello
@flow
def train_best():
    client = mlflow.MlflowClient()
    runs = mlflow.search_runs(order_by=["metrics.accuracy DESC"], max_results=1)
    top = runs.iloc[0]
    best_params = {
        "n_estimators": int(top["params.n_estimators"]),
        "max_depth": None if top["params.max_depth"] == "None" else int(top["params.max_depth"]),
    }
    train(**best_params, log_model=True)

# 3) serve_best: scarica l'ultimo modello loggato e avvia FastAPI
@flow
def serve_best():
    runs = mlflow.search_runs(
        filter_string="tags.mlflow.runName LIKE '%rf_%'",
        order_by=["start_time DESC"],
        max_results=1,
    )
    run_id = runs.iloc[0]["run_id"]
    client = mlflow.MlflowClient()
    art = client.list_artifacts(run_id)
    model_path = next(a.path for a in art if a.path.endswith(".pkl"))
    with tempfile.TemporaryDirectory() as tmp:
        local_pkl = client.download_artifacts(run_id, model_path, tmp)
        subprocess.run(["python", "-m", "src.serve", local_pkl])
