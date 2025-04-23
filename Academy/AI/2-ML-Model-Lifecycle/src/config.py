# src/config.py
from pathlib import Path
from pydantic import BaseModel

class Settings(BaseModel):
    project_root: Path = Path(__file__).resolve().parents[1]
    artifacts_dir: Path = project_root / "artifacts"
    model_name: str = "wine_rf.pkl"
    mlflow_uri: str = f"file:{project_root/'mlruns'}"
    experiment_name: str = "WineSweepDemo"      

CFG = Settings()
CFG.artifacts_dir.mkdir(exist_ok=True)
