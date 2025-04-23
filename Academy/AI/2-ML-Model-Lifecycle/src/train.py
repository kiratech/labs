# src/train.py
import mlflow, joblib, typer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from src.config import CFG
from src.data import load

app = typer.Typer()

@app.command()
def run(
    n_estimators: int = 200,
    max_depth: int | None = None,
    log_model: bool = typer.Option(True, "--log-model/--no-log-model")
):
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("weather_classification_experiment")

    X_tr, X_te, y_tr, y_te = load()
    with mlflow.start_run():
        model = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth, random_state=42
        ).fit(X_tr, y_tr)
        
        acc = accuracy_score(y_te, model.predict(X_te))
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_metric("accuracy", acc)
        
        if log_model:
            joblib.dump(model, CFG.artifacts_dir / CFG.model_name)
            mlflow.log_artifact(CFG.artifacts_dir / CFG.model_name)
        typer.echo(f"✅  accuracy={acc:0.3f}")

if __name__ == "__main__":
    app()
