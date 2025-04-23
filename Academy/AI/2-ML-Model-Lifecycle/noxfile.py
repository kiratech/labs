import nox
nox.options.reuse_existing_virtualenvs = True

PYTHON = "3.11"

# ----- helper ------------------------------------------------
def install_project(session):
    session.install("-e", ".")     # pacchetto src/

# ----------------- CI step di base --------------------------
@nox.session(python=PYTHON)
def lint(session):
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", "--show-diff-on-failure")

@nox.session(python=PYTHON)
def tests(session):
    session.install("pytest", "scikit-learn", "pandas")
    install_project(session)
    session.run("pytest", "-q")

# ----------------- WORKFLOW SIMULATI ------------------------
@nox.session(python=PYTHON)
def feature_pipeline(session):
    """Hyper-parameter sweep – solo metadati."""
    install_project(session)
    # lancia Prefect flow
    session.run("python", "-m", "src.pipeline", "train_sweep")

@nox.session(python=PYTHON)
def develop_pipeline(session):
    """Train con best hp – salva anche il modello."""
    install_project(session)
    session.run("python", "-m", "src.pipeline", "train_best")

@nox.session(python=PYTHON)
def master_pipeline(session):
    """Serve il miglior modello salvato."""
    install_project(session)
    session.run("python", "-m", "src.pipeline", "serve_best")
