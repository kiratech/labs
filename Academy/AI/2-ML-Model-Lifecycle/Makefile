# Makefile — Local GitHub Actions simulation using nox + conda environments
.PHONY: setup ci train serve monitor retrain pipeline clean
SHELL := /bin/zsh

# Conda environment name
ENV := lab_env_2

# Activate Conda + run nox in the correct environment
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
NOX := $(CONDA_ACTIVATE) $(ENV) && nox --no-venv

# ------------------------------------------------------------
# Environment setup
# ------------------------------------------------------------

setup:              ## Create conda environment + install pre-commit hooks
	conda env create -f environment.yaml --quiet
	$(NOX) pre-commit install

# ------------------------------------------------------------
# Simulated Git branch pushes (as CI/CD entrypoints)
# ------------------------------------------------------------

push-feature:       ## Simulate push to feature/* → hyperparameter sweep only
	$(NOX) -R -s feature_pipeline

push-develop:       ## Simulate push to develop → lint + tests + train best model
	$(NOX) -R -s lint
	$(NOX) -R -s tests
	$(NOX) -R -s develop_pipeline

push-main:        ## Simulate push to master/main → lint + tests + serve model
	$(NOX) -R -s lint
	$(NOX) -R -s tests
	$(NOX) -R -s main_pipeline
