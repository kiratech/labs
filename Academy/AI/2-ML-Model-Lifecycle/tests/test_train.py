from src import data, train

def test_train_model_accuracy_threshold():
    dataset = data.data_collection()
    prepared = data.data_preparation(dataset)
    model, acc = train.train_model(prepared, n_estimators=10, max_depth=5)
    assert acc > 0.5  # basic threshold check
    assert hasattr(model, "predict")
