"""
Unit tests for the data module in the Wine Quality ML pipeline.

Covers:
- Dataset loading
- Train-test splitting logic
"""

from src import data

def test_data_collection():
    """
    Test that the wine dataset is loaded correctly with non-empty features and labels.
    """
    X, y = data.data_collection()

    # Assert features and labels are not empty and match in length
    assert not X.empty, "Feature dataframe is empty"
    assert len(X) == len(y), "Mismatch between features and labels"
    assert "alcohol" in X.columns, "'alcohol' column should exist in features"

def test_data_preparation():
    """
    Test that the dataset is correctly split into train and test sets.
    """
    X, y = data.data_collection()
    X_tr, X_te, y_tr, y_te = data.data_preparation((X, y), split=0.2)

    # Assert that the train + test sizes add up to the original
    assert len(X_tr) + len(X_te) == len(X), "Train + test features mismatch"
    assert len(y_tr) + len(y_te) == len(y), "Train + test labels mismatch"

    # Optional: Check that no data was lost and all parts are non-empty
    assert not X_tr.empty and not X_te.empty, "Split feature sets are empty"
    assert not y_tr.empty and not y_te.empty, "Split label sets are empty"
