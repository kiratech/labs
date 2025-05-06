
# Lab: From Experiments to Production with Wine Classification

Welcome to this live lab!
In the previous lab session we:

1. **Created a classification model** using **Scikit-learn**, leveraging temperature and humidity to predict rain.  
2. **Integrated MLflow** to track training parameters, log evaluation metrics, and manage model versions in a structured way.  
3. **Explored and compared results** through the MLflow UI interface, reviewing different configurations and loading a saved model for future predictions.  

In this session, you will learn how to:

1. **Train a classification model** on a real dataset using `Scikit-learn`.
2. **Manage and track your experiments** with `MLflow`.
3. **Build CI/CD-like workflows** using `Makefile` and `nox`.
4. **Build scalable and orchestrated ML pipelines** using `Prefect`.
5. **Monitor data drift over time** and trigger retraining with `Evidently`.

We will follow a step-by-step approach combining **code execution**, **conceptual explanation**, and **UI walkthroughs**.

---

## 1 Context and Story

A mid‑sized wine producer wants to modernise quality control.  
Instead of relying on manual tasting alone, the company decides to analyse
chemical characteristics of each batch and predict the wine’s *cultivar*
(three classes) using machine learning.  
The stakes:

- **Repeatable experimentation** – new blends need fresh tuning
- **Fast promotion** – once a model looks good, it must move to production quickly
- **Operational monitoring** – chemical profiles may drift with soil and weather; the system must recognise drift and retrain autonomously

Our lab demonstrates how to meet these requirements **entirely on a laptop**,
using open‑source tools and zero cloud resources.

---
## 2 Dataset Overview – UCI Wine Recognition

The lab uses the well-known [**Wine Recognition**](https://archive.ics.uci.edu/dataset/109/wine) dataset from the UCI Machine Learning Repository.
Originally collected at the Institute of Oenology and Viticulture in Italy, the dataset contains the results of a chemical analysis of **178 wine samples** from three different *cultivars* (grape varieties) grown in the same region.
Each sample is described by **13 continuous variables** that capture key chemical properties influencing flavour and quality.

### 2.1 Features

| Feature                        | Description                                 | Typical Range |
| ------------------------------ | ------------------------------------------- | ------------- |
| `alcohol`                      | Ethyl-alcohol content (%)                   | 11 – 14 %     |
| `malic_acid`                   | Malic acid concentration (g/L)              | 0.7 – 5.8     |
| `ash`                          | Total ash (g/100 mL)                        | 1.3 – 3.3     |
| `alcalinity_of_ash`            | Ash alkalinity (mEq NaOH)                   | 10 – 30       |
| `magnesium`                    | Magnesium (mg/L)                            | 70 – 162      |
| `total_phenols`                | Total phenolic content (g/L)                | 0.9 – 3.9     |
| `flavanoids`                   | Flavonoid phenols (g/L)                     | 0.3 – 5.1     |
| `nonflavanoid_phenols`         | Non-flavonoid phenols (g/L)                 | 0.1 – 0.7     |
| `proanthocyanins`              | Proanthocyanins (g/L)                       | 0.4 – 3.6     |
| `color_intensity`              | Red/blue color intensity                    | 1.3 – 13.0    |
| `hue`                          | Hue at 520 nm relative to 420 nm            | 0.4 – 1.8     |
| `od280_od315_of_diluted_wines` | Optical density ratio (aromatic compounds)  | 1.3 – 4.0     |
| `proline`                      | Proline (mg/L) – associated with mouth-feel | 270 – 1680    |

### 2.2 Target variable: `class`

The classes are almost balanced (59 / 71 / 48 samples):

- **Class 0** – Cultivar A
- **Class 1** – Cultivar B
- **Class 2** – Cultivar C

### 2.3 Why This Dataset Fits the Demo

1. **Compact and clean** – You can train models in seconds, perfect for live coding.
2. **Chemically interpretable features** – Easy to discuss how drifting alcohol content affects predictions.
3. **Multi-class problem** – Demonstrates probabilities and class selection in the REST API.
4. **No privacy concerns** – The data are public domain, ideal for workshops.

### 2.4 Synthetic Drift Generation

To illustrate monitoring, the lab creates a *current batch* where `alcohol` values are artificially increased (e.g., harvest with higher sugar).
Evidently then compares this drifted batch to the original reference set, detects the shift and—if severe—triggers retraining through Prefect.

---

## 3 Tooling Overview – Concept + Our Usage

| Tool | Key Concept | How We Use It in the Lab |
|------|-------------|--------------------------|
| [**Makefile**](https://www.gnu.org/software/make/manual/make.html) | Declarative build/task runner | Simulates Git push events and invokes Nox sessions (`push-feature`, `push-develop`, `push-master`). |
| [**Nox**](https://nox.thea.codes/en/stable/) | Python automation with virtual/conda envs | Acts like GitHub Actions runners; executes lint, tests and Prefect flows in a reproducible and isolated way. |
| [**Prefect**](https://docs.prefect.io/v3/get-started) | Workflow orchestration + observability | Wraps training, serving and monitoring as flows; offers scheduling, retries and a UI at [http://127.0.0.1:4200](http://127.0.0.1:4200). |
| [**MLflow**](https://mlflow.org/) | Experiment tracking & model registry | Logs parameters, metrics and model artefacts; source of truth for the “best model”. UI at [http://127.0.0.1:5000](http://127.0.0.1:5000). |
| [**Scikit-learn**](https://scikit-learn.org/stable/index.html) | ML algorithms and utilities | Provides a fast RandomForest classifier for our demo. |
| [**FastAPI**](https://fastapi.tiangolo.com/) | High‑performance Python web API | Exposes the model at `/predict` with auto‑generated docs at [http://127.0.0.1:9000](http://127.0.0.1:9000). |
| [**Evidently**](https://docs.evidentlyai.com/introduction) | Data drift & model monitoring | Generates HTML/JSON drift reports; triggers retraining when drift is detected. |

---

## 4 Environment Setup

### 4.0 Requirements

This lab assumes that **Python** and **miniconda** are already installed, the repository [kiratech/labs](https://github.com/kiratech/labs.git) is accessible, and **Git** is properly configured on your local machine. Furthermore, **VSCode** or an IDE able to run Jupyter Notebooks, must be installed as well.  
As in the previous lab, in order to execute this laboratory, you will be asked to install a set of tools common in MLOps field.

### 4.1  Clone the Repository

To start, clone the lab repository by running the following command in the terminal:

```sh
  git clone https://github.com/kiratech/labs.git
```

### 4.2 Checkout the Lab Branch

After cloning the repository, checkout the `academy-ai` branch:

```sh
  git checkout academy-ai
```  

Then, navigate to the project folder:

```sh
  cd labs/Academy/AI/2-ML-Model-Lifecycle
```  

This folder contains resources related to this lab.

### 4.3 Create a Virtual Environment

A virtual environment allows you to isolate the project's dependencies from the system-wide ones.  
In the previous lab, we first created the environment and then installed the dependencies. This time we'll do it with a single command, creating the environment with all the necessary dependencies.

In your terminal, create a virtual environment from an existing file:

```sh
  conda env create -f environment.yaml
```

Activate the Virtual Environment:

```sh
  conda activate lab_env_2
```

You should see the `(lab_env_2)` prefix in the terminal, indicating that the virtual environment is active.

### 4.4 Open the Project in VSCode

At this point, open VSCode from the file explorer or by running the command:

```sh
  code .
```

### 4.5 Start the services

Open three integrated terminals and in each one activate the environemnt with `conda activate lab_env_2` and then:

| Terminal | Command | Purpose |
|----------|---------|---------|
| T‑1 | `prefect server start` | Prefect API + UI |
| T‑2 | `mlflow ui` | Experiment tracking UI |
| T‑3 | `-` | Run workflow commands (next sections) |

### 4.6 Open services UI

Open in the browser Prefect and MLflow at:  
| Service | Address |
|----------|---------|
| Prefect | [http://127.0.0.1:4200](http://127.0.0.1:4200) |
| MLflow | [http://127.0.0.1:5000](http://127.0.0.1:5000) |

---

## 5 Branch Workflows

### 5.1 Feature Branch Workflow

- **Command**  
In your terminal, once the conda environment is active, run:  

```sh
  make push-feature
```

- **Goal**  
  Explore the parameter space quickly and cheaply. No model is intended for production at this stage.  
  We only want evidence that “something promising” exists.
- **What the Command Simulates**  
  A developer pushes code to **`feature/<experiment‑name>`**.  
  CI/CD should **only run experiments**, producing metrics the team can compare later.
- **What It Does**
  - A Nox session calls Prefect flow `train_experiment`.
  - Nine RandomForest training tasks run in parallel (3  `n_estimators` × 3  `max_depth`).
  - Each task logs **parameters + accuracy** to MLflow, but **does not store a model file**.
  - Prefect captures task logs and execution graph.
- **What to Explore**
  - MLflow UI: nine runs with different hyper‑params, no artifacts saved.
  - Prefect UI: one flow, nine parallel tasks—visual confirmation of parallel runs.

### 5.2 Develop Branch Workflow 

- **Command**  
In your terminal, once the conda environment is active, run:  

```sh
  make push-develop
```

- **Goal**  
  Promote the best experimental configuration, validate code quality, and log a **deployable model artifact**.
- **What the Command Simulates**  
  A merge/push to **`develop`**. CI/CD should lint, test, **re‑train with chosen hyper‑params**, and register the resulting model.
- **What It Does**  
  
  1. **Lint** (`ruff via pre‑commit`) and **unit tests** (`pytest`) run first. Build stops on failure.
  2. Prefect flow `train_best` queries MLflow, grabs the run with highest accuracy.
  3. It re‑trains a RandomForest using those parameters on fresh data splits.
  4. Saves the `.pkl` artifact to `artifacts/` and logs it to MLflow.

- **What to Explore**
  - Terminal: lint/test output.
  - MLflow UI: a new run with an **artifact path**, this is the candidate for production.
  - Prefect UI: see the “find best params” task feeding the “train” task.

### 5.3 Master Branch Workflow  `make push-master`

- **Command**  
In your terminal, once the conda environment is active, run:  

```sh
  make push-main
```

- **Goal**  
  Deploy the champion model as an HTTP service usable by downstream teams.
- **What the Command Simulates**  
  A merge/push to **`main`**. CI/CD should perform a last sanity check, then bring the model online.
- **What It Does**  
  
  1. Re‑runs lint and tests (quick safety net).
  2. Prefect flow `serve_best` downloads the best model artifact from MLflow.
  3. Builds a FastAPI app and launches Uvicorn on **port 9000**.

- **What to Explore**
  - Swagger UI at `http://127.0.0.1:9000/docs`: live documentation, try a prediction.
  - Prefect UI: a small flow made of download, build app and serve.
  - MLflow UI: confirm the run ID of the served model matches the develop stage.
### 5.4 Querying the Best Model

Once the **main branch workflow** has deployed the FastAPI service, you can send a prediction request directly from the terminal:

```bash
curl -X POST http://localhost:9000/predict \
     -H "Content-Type: application/json" \
     -d '{
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
           "proline": 1000
         }'
```

Expected JSON response:

```json
{
  "class": 1,
  "proba": [0.02, 0.95, 0.03]
}
```

---

## 6 Monitoring & Auto‑Retraining 

- **Command**  
In your terminal, once the conda environment is active, run:  

```sh
  python -m src.pipeline_monitoring monitoring_best
```

- **Goal**  
  Detect distributional drift and kick off retraining only when needed.
- **What the Command Simulates**  
  A **scheduled batch job** (cron in Prefect) that runs nightly, comparing that day’s data against a reference baseline.
- **What It Does**  
  
  1. Generates (or ingests) the **current batch**. Here we synthesise drift by nudging alcohol levels.
  2. Evidently creates an HTML + JSON drift report.
  3. Prefect parses the `alchol` feature p‑value between the training set distribution and the new drifted set distribution. If ≤ 0.05, it calls the same `train_best` flow used on develop.
  4. All actions—report generation and optional retraining—are logged in Prefect and MLflow.

- **What to Explore**
  - Drift Report: open `artifacts/drift_report.html`; discuss which features drifted.
  - Prefect UI: see conditional branching—one path ends, the other chains into a training flow.
  - MLflow UI: a new run appears **only** when drift threshold is exceeded, proving closed‑loop automation.

---

## 7 Conclusions

Over the course of this lab we have:

- **Simulated a full CI/CD loop locally**
  using Makefile to trigger branch‑style workflows and Nox as a lightweight stand‑in for GitHub Actions.
- **Captured the complete model lineage**
  in MLflow, from exploratory runs to the promoted, deployable artifact.
- **Orchestrated repeatable pipelines**
  with Prefect, gaining retry logic, scheduling, and an audit‑friendly UI.
- **Deployed an inference endpoint**
  via FastAPI that is immediately testable through cURL or Swagger docs.
- **Closed the monitoring loop**
  by integrating Evidently to detect drift and automatically retrain when data shifts.  

Together these elements demonstrate an end‑to‑end, production‑style MLOps workflow that fits entirely on a developer laptop—yet scales conceptually to cloud or on‑prem environments.  
The key takeaway: **tooling synergy** matters more than individual components.
By combining focused, purpose‑built tools, we achieve reproducibility, observability and automation without heavyweight infrastructure.

## 8 Next steps
TBD
