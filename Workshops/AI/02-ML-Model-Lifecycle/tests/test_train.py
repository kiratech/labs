"""
Unit test for the train module in the Wine Quality ML pipeline.

Covers:
- Training a RandomForestClassifier
- Validating model accuracy and structure
"""

from src import data, train

def test_train_model_accuracy_threshold():
    """
    Test that the train_model function returns a trained model with acceptable accuracy.

    - Uses a real dataset split
    - Checks that accuracy is above a baseline threshold
    - Verifies that the model supports .predict()
    """
    # Load and split the dataset
    X, y = data.data_collection()
    prepared = data.data_preparation((X, y))

    # Train a RandomForest model with basic hyperparameters
    model, acc = train.train_model(prepared, n_estimators=10, max_depth=5)

    # Assert accuracy is above 50% (weak sanity check)
    assert acc > 0.5, f"Expected accuracy > 0.5, got {acc}"

    # Check that model has a predict method
    assert hasattr(model, "predict"), "Model does not implement .predict()"
