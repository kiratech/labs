"""Test basilari sul caricamento e integrità del dataset"""

from src.data import load
import pandas as pd

def test_split_shapes():
    X_tr, X_te, y_tr, y_te = load()
    assert len(X_tr) > 0 and len(X_te) > 0
    assert len(X_tr) == len(y_tr)
    assert len(X_te) == len(y_te)

def test_no_missing_values():
    X_tr, X_te, y_tr, y_te = load()
    assert not X_tr.isna().any().any()
    assert not X_te.isna().any().any()
