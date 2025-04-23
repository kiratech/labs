# src/data.py
import pandas as pd
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split

def load(split: float = .2, seed: int = 42):
    X, y = load_wine(return_X_y=True, as_frame=True)
    return train_test_split(X, y, test_size=split, random_state=seed)
