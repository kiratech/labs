"""
src/data.py
Data handling module for the Wine Quality pipeline.

Provides:
- data_collection: Loads the wine dataset from scikit-learn.
- new_data_collection: Simulates a new batch with data drift in alcohol.
- data_preparation: Prepares the dataset (renames columns, performs train-test split).
"""

import random

import pandas as pd
import typer
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from src.utils import get_logger

app = typer.Typer(add_completion=False)


def data_collection() -> tuple[pd.DataFrame, pd.Series]:
    """
    Loads the wine dataset.

    Returns:
        tuple:
            - X (pd.DataFrame): Feature matrix.
            - y (pd.Series): Target labels.
    """
    logger = get_logger()
    logger.info("Loading Wine dataset...")
    X, y = load_wine(return_X_y=True, as_frame=True)
    logger.info(
        f"Wine dataset loaded with {X.shape[0]} samples and {X.shape[1]} features."
    )
    return (X, y)


def new_data_collection() -> pd.DataFrame:
    """
    Loads the wine dataset and introduces data drift in the 'alcohol' feature.

    Randomly perturbs alcohol values within a multiplier range
    to simulate a distributional change for monitoring.

    Returns:
        pd.DataFrame: Drifted dataset (features only, no target).
    """
    X, _ = data_collection()
    df = X.copy()

    logger = get_logger()
    logger.info("Generating drifted data batch...")

    # Filter high alcohol wines
    df_filtered = df[df["alcohol"] > 13]

    # Apply random scaling to simulate drift
    rnd_drift = random.uniform(1.03, 1.13)
    df_filtered["alcohol"] = df["alcohol"] * rnd_drift
    logger.warning(f"Random drif generated for alchol with coefficient {rnd_drift}.")
    # Sample up to 100 instances
    df_current = df_filtered.sample(min(100, len(df_filtered)), random_state=0)
    return df_current


def data_preparation(
    dataset: tuple[pd.DataFrame, pd.Series], split: float = 0.2, seed: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Prepares the dataset for training:
    - Renames any problematic columns (e.g., replaces slashes).
    - Splits the dataset into train and test sets.

    Args:
        dataset (tuple): Tuple containing (X, y).
        split (float, optional): Proportion of the dataset to include in the test split (default: 0.2).
        seed (int, optional): Random seed for reproducibility (default: 42).

    Returns:
        tuple:
            - X_train (pd.DataFrame): Training features.
            - X_test (pd.DataFrame): Testing features.
            - y_train (pd.Series): Training labels.
            - y_test (pd.Series): Testing labels.
    """
    X, y = dataset
    logger = get_logger()
    # Ensure column names are safe (replace slashes with underscores)
    logger.info("Replacing / with - in column names...")
    X.columns = X.columns.str.replace("/", "_")

    # Split into train/test
    logger.info(f"Preparing dataset: split={split}, seed={seed}...")
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=split, random_state=seed)
    logger.info(
        f"Dataset split into {X_tr.shape[0]} train and {X_te.shape[0]} test samples."
    )
    return (X_tr, X_te, y_tr, y_te)


if __name__ == "__main__":
    app()
