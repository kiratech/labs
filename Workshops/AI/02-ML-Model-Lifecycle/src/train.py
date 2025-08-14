"""
src/train.py
Model training module for the Wine Quality pipeline.

- Trains a RandomForestClassifier on provided dataset splits.
- Logs parameters, metrics, and optionally the trained model to MLflow.
- Can be executed both via CLI (Typer) or imported in Prefect flows.
"""

import joblib
import mlflow
import typer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from src.config import CFG

from src.utils import get_logger

app = typer.Typer(add_completion=False)

# Configure MLflow tracking (uses the experiment defined in CFG)
mlflow.set_tracking_uri(CFG.mlflow_uri)
mlflow.set_experiment(CFG.experiment_name)


def train_model(
    dataset_split: tuple, n_estimators: int, max_depth: int | None
) -> tuple:
    """
    Trains a RandomForest model on the provided dataset.

    Args:
        dataset_split (tuple): Tuple of (X_train, X_test, y_train, y_test) splits.
        n_estimators (int): Number of trees in the forest.
        max_depth (int | None): Maximum depth of the trees (None means no limit).

    Returns:
        tuple:
            - model (RandomForestClassifier): Trained model.
            - acc (float): Accuracy on the test set.
    """
    logger = get_logger()
    logger.info(
        f"Training RandomForest with n_estimators={n_estimators}, max_depth={max_depth}..."
    )

    X_tr, X_te, y_tr, y_te = dataset_split

    # Train the RandomForest model
    model = RandomForestClassifier(
        n_estimators=n_estimators, max_depth=max_depth, random_state=0
    ).fit(X_tr, y_tr)

    # Compute accuracy on the test set
    acc = accuracy_score(y_te, model.predict(X_te))
    logger.info(f"Model trained. Accuracy={acc:.4f}.")
    return model, acc


def run(
    dataset_split: tuple,
    n_estimators: int = 200,
    max_depth: int | None = None,
    log_model: bool = typer.Option(
        True,
        "--log-model/--no-log-model",
        help="Whether to log the model artifact to MLflow.",
    ),
) -> float:
    """
    Main training entry point.

    - Trains a model using specified hyperparameters.
    - Logs training parameters, accuracy metric, and optionally the trained model to MLflow.

    Args:
        dataset_split (tuple): Tuple of (X_train, X_test, y_train, y_test) splits.
        n_estimators (int, optional): Number of trees (default: 200).
        max_depth (int | None, optional): Maximum tree depth (default: None, unlimited).
        log_model (bool, optional): If True, logs the model artifact to MLflow (default: True).

    Returns:
        float: Accuracy score of the trained model.
    """
    logger = get_logger()
    logger.info(
        f"Running full training pipeline (MLflow logging enabled={log_model})..."
    )

    with mlflow.start_run():
        # Log hyperparameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)

        # Train the model
        model, acc = train_model(dataset_split, n_estimators, max_depth)

        # Log model accuracy
        mlflow.log_metric("accuracy", acc)

        # Optionally serialize and log the trained model
        if log_model:
            outfile = CFG.artifacts_dir / CFG.model_name
            joblib.dump(model, outfile)
            mlflow.log_artifact(outfile)

    logger.info("Training run completed and logged to MLflow.")
    return acc  # Useful for Prefect tasks or external calls


if __name__ == "__main__":
    app()
