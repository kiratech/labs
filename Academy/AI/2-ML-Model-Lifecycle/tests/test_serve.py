from src import serve
from src.config import CFG

def test_build_app_and_predict():
    # Carica modello (assicurati che esista già da train_best)
    model_path = CFG.artifacts_dir / CFG.model_name
    assert model_path.exists(), "Trained model file is missing"

    api = serve.build_app(model_path)

    sample = {
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
    }

    from fastapi.testclient import TestClient
    client = TestClient(api)
    response = client.post("/predict", json=sample)
    assert response.status_code == 200
    result = response.json()
    assert "class" in result
    assert isinstance(result["class"], int)
