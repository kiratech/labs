# src/sweep.py
"""
Train-sweep demo
———————
• Ciclo su piccoli hyper-parametri RF
• Log parametri + accuracy su MLflow
• Flow tracciata sulla UI di Prefect 2 (Orion)
"""

from itertools import product

import mlflow
from prefect import flow, task
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# --------------------------------------------------------------------
# configura MLflow ➜ cartella locale "mlruns" nella root del progetto
mlflow.set_tracking_uri("file:mlruns")

# --------------------------------------------------------------------
@task(log_prints=True)
def train_once(n_estimators: int, max_depth: int | None):
    """Un singolo addestramento + log su MLflow."""
    X, y = load_wine(return_X_y=True, as_frame=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training with n_estimators={n_estimators}, max_depth={max_depth}")
    with mlflow.start_run():
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)

        model = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth, random_state=0
        ).fit(X_tr, y_tr)

        acc = accuracy_score(y_te, model.predict(X_te))
        mlflow.log_metric("accuracy", acc)

        return acc


@flow(name="train_sweep")
def train_sweep():
    """Grid-search minimal su due hyper-parametri RF."""
    grid = {
        "n_estimators": [1, 10, 100],
        "max_depth": [None, 5, 10],
    }

    for n_est, m_depth in product(grid["n_estimators"], grid["max_depth"]):
        train_once.submit(n_estimators=n_est, max_depth=m_depth)  # .submit = task async, appare come sub-run


if __name__ == "__main__":
    train_sweep()
