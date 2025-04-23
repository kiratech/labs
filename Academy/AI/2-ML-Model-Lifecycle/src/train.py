# src/train.py
"""Un singolo ciclo di training + logging su MLflow."""

from pathlib import Path

import joblib
import mlflow
import typer
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from src.config import CFG

app = typer.Typer(add_completion=False)

# Configura il backend MLflow (cartella "mlruns" nella root)
mlflow.set_tracking_uri(CFG.mlflow_uri)
mlflow.set_experiment(CFG.experiment_name)  

def _train_core(n_estimators: int, max_depth: int | None):
    """Ritorna modello addestrato e accuracy."""
    X, y = load_wine(return_X_y=True, as_frame=True)
    X.columns = X.columns.str.replace('/', '_')
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(
        n_estimators=n_estimators, max_depth=max_depth, random_state=0
    ).fit(X_tr, y_tr)

    acc = accuracy_score(y_te, model.predict(X_te))
    return model, acc


@app.command()
def run(
    n_estimators: int = 200,
    max_depth: int | None = None,
    log_model: bool = typer.Option(
        True, "--log-model/--no-log-model", help="Salva anche il modello su MLflow."
    ),
) -> float:
    """Addestra e logga parametri + metriche (+ modello opzionale)."""
    with mlflow.start_run():
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)

        model, acc = _train_core(n_estimators, max_depth)
        mlflow.log_metric("accuracy", acc)

        if log_model:
            outfile = CFG.artifacts_dir / CFG.model_name
            joblib.dump(model, outfile)
            mlflow.log_artifact(outfile)

    typer.echo(f"✅  accuracy={acc:0.3f}")
    return acc  # utile se importato come funzione


if __name__ == "__main__":
    app()
