"""
src/serve.py
FastAPI inference service for the Wine Quality model.

- Loads a RandomForestClassifier model (joblib).
- Serves predictions via a REST API endpoint.
- CLI options allow flexible deployment or local testing.

Endpoints:
- POST /predict : Accepts wine features and returns the predicted class and probabilities.
"""

import subprocess
from pathlib import Path
from typing import Optional

import joblib
import typer
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.utils import get_logger

app = typer.Typer(add_completion=False)


def build_app(model_path: Path) -> FastAPI:
    """
    Constructs the FastAPI app with the loaded model.

    Args:
        model_path (Path): Path to the trained model file (.pkl).

    Returns:
        FastAPI: Configured FastAPI app with one /predict endpoint.
    """
    # Load trained model
    model = joblib.load(model_path)

    class Features(BaseModel):
        """
        Request body schema for prediction.
        """

        alcohol: float
        malic_acid: float
        ash: float
        alcalinity_of_ash: float
        magnesium: float
        total_phenols: float
        flavanoids: float
        nonflavanoid_phenols: float
        proanthocyanins: float
        color_intensity: float
        hue: float
        od280_od315_of_diluted_wines: float
        proline: float

    # Initialize FastAPI app
    api = FastAPI(title="Wine Quality Inference")

    @api.post("/predict")
    def predict(feat: Features):
        """
        Predicts the wine quality class based on provided features.

        Args:
            feat (Features): Input wine features.

        Returns:
            dict: Predicted class and probabilities for each class.
        """
        import pandas as pd

        # Convert input features to DataFrame
        X = pd.DataFrame([feat.dict()])

        # Predict class and class probabilities
        proba = model.predict_proba(X)[0].tolist()
        predicted_class = int(model.predict(X)[0])

        return {"class": predicted_class, "proba": proba}

    return api


def deploy(model_path: Path, host: str = "0.0.0.0", port: int = 9000):
    """
    Deploys the given FastAPI app with Uvicorn.

    Args:
        api (FastAPI): The app to serve.
        host (str, optional): Host IP address to bind (default: 0.0.0.0).
        port (int, optional): Port number to expose (default: 9000).
    """
    logger = get_logger()
    logger.info(f"Building FastAPI app for model from {model_path}...")
    logger.info(f"Starting Uvicorn server on {host}:{port}...")
    subprocess.Popen(["python", "-m", "src.serve", "--model-path", str(model_path)])


@app.command()
def run(
    model_path: Optional[Path] = typer.Option(
        None,
        "--model-path",
        "-m",
        help="Path to the .pkl model file.",
    ),
    host: str = "0.0.0.0",
    port: int = 9000,
):
    """
    CLI entry point for running the API locally.

    - Loads the model from the given path (or default artifacts directory).
    - Builds the FastAPI app.
    - Serves the API with Uvicorn.

    Args:
        model_path (Optional[Path], optional): Path to the .pkl model file.
        host (str, optional): Host IP to bind (default: 0.0.0.0).
        port (int, optional): Port to expose the API (default: 9000).
    """
    api = build_app(model_path)
    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    app()
