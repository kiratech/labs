# src/serve.py
import joblib, uvicorn, typer
from fastapi import FastAPI
from pydantic import BaseModel
from config import CFG

app = FastAPI(title="Wine Quality Inference")

model = joblib.load(CFG.artifacts_dir / CFG.model_name)

class Features(BaseModel):               # 11 feature numeriche
    alcohol: float
    magnesium: float
    hue: float
    # … (completare con le altre)

@app.post("/predict")
def predict(feat: Features):
    import numpy as np, pandas as pd
    X = pd.DataFrame([feat.dict()])
    proba = model.predict_proba(X)[0].tolist()
    return {"class": int(model.predict(X)[0]), "proba": proba}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
