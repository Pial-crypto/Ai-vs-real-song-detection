from __future__ import annotations

import numpy as np

from backend.app.services.ml_pipeline.pipeline import (
    CrossValidator,
    EarlyStopping,
    ExperimentTracker,
    HyperparameterTuner,
    compute_metrics,
    confusion_matrix,
    stratified_split,
)


def test_stratified_split():
    X = np.arange(20).reshape(10, 2)
    y = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
    split = stratified_split(X, y, test_size=0.2, val_size=0.1, random_state=1)
    assert split.X_train.shape[0] + split.X_val.shape[0] + split.X_test.shape[0] == 10


def test_compute_metrics():
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1])
    m = compute_metrics(y_true, y_pred)
    assert m["accuracy"] == 0.75
    assert m["tp"] == 2


def test_confusion_matrix():
    cm = confusion_matrix(np.array([0, 1, 1]), np.array([0, 1, 0]))
    assert cm == [[1, 0], [1, 1]]


def test_early_stopping():
    es = EarlyStopping(patience=2, min_delta=1e-3)
    assert es.step(1.0) is False
    assert es.step(1.1) is False
    assert es.step(1.2) is True


def test_cross_validator():
    X = np.arange(10)
    y = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
    cv = CrossValidator(n_splits=5, random_state=1)
    folds = list(cv.split(X, y))
    assert len(folds) == 5
    for tr, te in folds:
        assert len(tr) + len(te) == 10


def test_experiment_tracker(tmp_path):
    from backend.app.services.ml_pipeline.pipeline import TrainingResult

    tr = TrainingResult(model_name="m", test_accuracy=0.9, test_f1=0.88, best_val_loss=0.1, best_epoch=3)
    tracker = ExperimentTracker(output_dir=str(tmp_path / "exp"))
    run_id = tracker.log_run(tr)
    assert run_id.startswith("run_")
    assert len(tracker.summary()) == 1


def test_hyperparameter_tuner():
    tuner = HyperparameterTuner({"a": [1, 2], "b": [3, 4]})
    combos = tuner.grid_combinations()
    assert len(combos) == 4
    rnd = tuner.random_combinations(n=2, seed=1)
    assert len(rnd) == 2
