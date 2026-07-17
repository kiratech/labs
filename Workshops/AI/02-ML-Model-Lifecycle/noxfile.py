# noxfile.py — Local CI/CD simulation using Nox sessions
import nox

# Reuse virtualenvs across runs to avoid reinstallation
nox.options.reuse_existing_virtualenvs = True
# Shared environment for all sessions
nox.options.envdir = ".nox/shared"  

# Python version to use in all sessions
PYTHON = "3.11"

# ------------------------------------------------------------
# Shared setup for installing local package
# ------------------------------------------------------------


def install_project(session):
    """
    Install the local src/ package in editable mode.
    """
    session.install("-e", ".")


# ------------------------------------------------------------
# Core CI checks: linting and unit tests
# ------------------------------------------------------------


@nox.session(python=PYTHON)
def lint(session):
    """
    Run pre-commit hooks for linting and formatting.
    """
    session.run("pre-commit", "run", "--all-files", "--hook-stage", "manual")

@nox.session(python=PYTHON)
def tests(session):
    """
    Run unit tests using pytest.
    """
    install_project(session)
    session.run("pytest", "-q")


# ------------------------------------------------------------
# Simulated ML workflows triggered by Git pushes
# ------------------------------------------------------------


@nox.session(python=PYTHON)
def feature_pipeline(session):
    """
    Simulates a push to feature/*:
    - Runs hyperparameter sweep (no model saved).
    """
    install_project(session)
    session.run("python", "-m", "src.pipeline_ml", "train_experiment")


@nox.session(python=PYTHON)
def develop_pipeline(session):
    """
    Simulates a push to develop:
    - Trains the model using best hyperparameters.
    - Logs metrics and saves model to MLflow.
    """
    install_project(session)
    session.run("python", "-m", "src.pipeline_ml", "train_best")


@nox.session(python=PYTHON)
def main_pipeline(session):
    """
    Simulates a push to main:
    - Downloads the best saved model.
    - Serves the model through FastAPI.
    """
    install_project(session)
    session.run("python", "-m", "src.pipeline_ml", "serve_best")
