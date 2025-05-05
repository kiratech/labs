
# Wine Quality ML Pipeline – Technical Review Guide

This README provides a step-by-step guide for reviewing the Wine Quality MLOps proof of concept.  
All workflows must be tested using the `Makefile` commands only.

---

## 1. Environment Setup

Create and activate the Conda environment (`lab_env_2`):

```bash
conda env create -f environment.yaml
conda activate lab_env_2
```

---

## 2. Start Required Services

### MLflow UI

```bash
conda activate lab_env_2
mlflow ui
```

Open: [http://localhost:5000](http://localhost:5000)  

---

### Prefect Server

```bash
conda activate lab_env_2
prefect server start
```

Open: [http://localhost:4200](http://localhost:4200)  

---

## 3. Run Workflows via `make`

All workflows must be executed via the provided `Makefile` in another terminal:
```bash
conda activate lab_env_2
```

### Feature Branch (Hyperparameter Sweep)

```bash
make push-feature
```

- Runs `train_experiment` on a parameter grid
- Logs metadata only (no model artifact)

---

### Develop Branch (Train Best Model)

```bash
make push-develop
```

- Runs: `lint`, `tests`, `train_best`
- Trains model using best hyperparams from MLflow
- Logs model artifact to MLflow

---

### Main Branch (Model Serving)

```bash
make push-main
```

- Runs: `lint`, `tests`, `serve_best`
- Starts a FastAPI app at [http://localhost:9000/predict](http://localhost:9000/predict)
- To shutdown the FastAPI server: `kill -9 $(lsof -ti :9000)`

Example test request:

```bash
curl -X POST http://localhost:9000/predict -H "Content-Type: application/json" \
  -d '{"alcohol":13.0,"malic_acid":2.0,"ash":2.5,"alcalinity_of_ash":15.0,
       "magnesium":100.0,"total_phenols":2.0,"flavanoids":2.5,
       "nonflavanoid_phenols":0.3,"proanthocyanins":1.9,"color_intensity":5.0,
       "hue":1.0,"od280_od315_of_diluted_wines":3.0,"proline":1000}'
```

---

### Monitoring + Drift Detection

This runs a simulated batch with drift. If drift is detected (p ≤ 0.05), it retriggers training.

```bash
python -m src.pipeline_monitoring
```

Generates:
- A deployment of flow running every minute
- `artifacts/drift_report.html`
- `artifacts/drift_report.json`
- Retraining of best model if triggered

---

## 4. Verify Output in UI Tools

| Component | URL | Check |
|----------|-----|-------|
| **MLflow UI** | http://localhost:5000 | Parameters, metrics, model |
| **Prefect UI** | http://localhost:4200 | Flow runs, logs |
| **FastAPI** | http://localhost:9000/predict | Model serving |
| **Drift Report** | `artifacts/drift_report.html` | Open manually in browser |

---

## Summary

This PoC runs fully locally using:

- Conda
- Nox
- Make
- MLflow
- Prefect
- FastAPI

No Docker or remote services are required.

Please run and verify each `make` command as documented above.
