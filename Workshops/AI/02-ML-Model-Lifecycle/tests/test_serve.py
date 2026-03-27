"""
Unit test for FastAPI model serving without relying on a pre-existing trained model.

- Creates a dummy RandomForestClassifier
- Saves it to a temporary .pkl file
- Builds the FastAPI app using the test model
- Sends a prediction request to /predict
"""

import tempfile
import joblib
from pathlib import Path
from fastapi.testclient import TestClient
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from src import serve

def test_build_app_and_predict():
    """
    Test that the FastAPI app is correctly built with a temporary dummy model,
    and that the /predict endpoint returns a valid response.
    """
    # --- Create a dummy model and train it on minimal synthetic data ---
    model = RandomForestClassifier()
    X_dummy = pd.DataFrame([{
        "alcohol": 13.0,
        "malic_acid": 2.0,
        "ash": 2.5,
        "alcalinity_of_ash": 15.0,
        "magnesium": 100.0,
        "total_phenols": 2.0,
        "flavanoids": 2.5,
        "nonflavanoid_phenols": 0.3,
        "proanthocyanins": 1.9,
        "color_intensity": 5.0,
        "hue": 1.0,
        "od280_od315_of_diluted_wines": 3.0,
        "proline": 1000,
    }])
    y_dummy = [1]
    model.fit(X_dummy, y_dummy)

    # --- Save model to a temporary .pkl file ---
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
        model_path = Path(tmp.name)
        joblib.dump(model, model_path)

    # --- Build FastAPI app using the dummy model ---
    api = serve.build_app(model_path)

    # --- Create a test client and send a sample request ---
    sample = X_dummy.iloc[0].to_dict()
    client = TestClient(api)
    response = client.post("/predict", json=sample)

    # --- Assertions ---
    assert response.status_code == 200
    result = response.json()
    assert "class" in result
    assert isinstance(result["class"], int)
