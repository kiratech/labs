.PHONY: setup ci train serve monitor retrain pipeline clean
SHELL := /bin/zsh
ENV := lab_env_2
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
NOX    := $(CONDA_ACTIVATE) $(ENV) && nox

setup:              ## create environment + install hooks
	conda env create -f environment.yaml --quiet
	$(NOX) pre-commit install

## ----------------------------------------------
## simulazione "push" su vari branch Git / GitHub
## ----------------------------------------------

push-feature:           ## simula push su feature/*
	$(NOX) -R -s feature_pipeline

push-develop:           ## simula push su develop
	$(NOX) -R -s lint -s tests -s develop_pipeline

push-master:            ## simula push su master/main
	$(NOX) -R -s lint -s tests -s master_pipeline
