# tests/test_train.py
from src.train import RandomForestClassifier, load

def test_accuracy():
    X_tr, X_te, y_tr, y_te = load()
    model = RandomForestClassifier(random_state=0).fit(X_tr, y_tr)
    assert model.score(X_te, y_te) > 0.8
