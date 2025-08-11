"""
src/config.py
Configuration module for the Wine Quality pipeline.

- Defines global paths, MLflow settings, artifact naming, and Evidently monitoring endpoints.
- Uses Pydantic's BaseModel for structured configuration.
"""

from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    """
    Centralized application settings.

    Attributes:
        project_root (Path): Root directory of the project.
        artifacts_dir (Path): Directory where artifacts (models, reports) will be stored.
        model_name (str): Default filename for the trained model artifact.
        mlflow_uri (str): URI where MLflow tracking server or local files are stored.
        experiment_name (str): Name of the MLflow experiment.
        evidently_url (str): Base URL where the Evidently UI dashboard is running.
        evidently_project (str): Project name under Evidently for monitoring.
    """

    # Root of the project (assumes config.py is in src/)
    project_root: Path = Path(__file__).resolve().parents[1]

    # Directory for storing artifacts (models, drift reports, etc.)
    artifacts_dir: Path = project_root / "artifacts"

    # Default model filename for serialization
    model_name: str = "wine_rf.pkl"

    # MLflow tracking URI (using local file storage in 'mlruns/')
    mlflow_uri: str = f"file:{project_root/'mlruns'}"

    # MLflow experiment name for tracking runs
    experiment_name: str = "WineSweepDemo"

    # Evidently monitoring - URL to the local Evidently UI server
    evidently_url: str = "http://localhost:8000"

    # Evidently monitoring - Name of the project for batch drift tracking
    evidently_project: str = "wine_quality_monitoring"


# Singleton instance used throughout the project
CFG = Settings()

# Ensure artifacts directory exists (create if it doesn't)
CFG.artifacts_dir.mkdir(exist_ok=True)
