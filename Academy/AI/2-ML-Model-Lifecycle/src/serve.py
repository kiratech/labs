# src/serve.py
"""Inferenza FastAPI: serve un modello RF salvato con joblib."""
from pathlib import Path
from typing import Optional

import joblib
import typer
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.config import CFG

app_cli = typer.Typer(add_completion=False)


def build_app(model_path: Path) -> FastAPI:
    model = joblib.load(model_path)

    class Features(BaseModel):
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

    api = FastAPI(title="Wine Quality Inference")

    @api.post("/predict")
    def predict(feat: Features):
        import pandas as pd

        X = pd.DataFrame([feat.dict()])
        proba = model.predict_proba(X)[0].tolist()
        return {"class": int(model.predict(X)[0]), "proba": proba}

    return api


@app_cli.command()
def run(
    model_path: Optional[Path] = typer.Option(
        None,
        "--model-path",
        "-m",
        help="Percorso del modello .pkl; default = ultimo train locale.",
    ),
    host: str = "0.0.0.0",
    port: int = 8000,
):
    """Avvia l'API sul modello indicato (o su quello di default)."""
    path = model_path or (CFG.artifacts_dir / CFG.model_name)
    api = build_app(path)
    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    app_cli()
