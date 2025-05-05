from src import data

def test_data_collection():
    X, y = data.data_collection()
    assert not X.empty
    assert len(X) == len(y)
    assert "alcohol" in X.columns

def test_data_preparation():
    X, y = data.data_collection()
    X_tr, X_te, y_tr, y_te = data.data_preparation((X, y), split=0.2)
    assert len(X_tr) + len(X_te) == len(X)
    assert len(y_tr) + len(y_te) == len(y)
