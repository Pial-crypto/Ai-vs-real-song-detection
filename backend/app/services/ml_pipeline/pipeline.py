"""Machine learning training and evaluation pipeline utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class DatasetSplit:
    X_train: np.ndarray
    y_train: np.ndarray
    X_val: np.ndarray
    y_val: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray


@dataclass
class TrainingConfig:
    test_size: float = 0.2
    val_size: float = 0.1
    random_state: int = 42
    batch_size: int = 32
    epochs: int = 50
    learning_rate: float = 1e-3
    early_stopping_patience: int = 5
    min_delta: float = 1e-4


@dataclass
class TrainingResult:
    model_name: str
    train_loss: List[float] = field(default_factory=list)
    val_loss: List[float] = field(default_factory=list)
    train_acc: List[float] = field(default_factory=list)
    val_acc: List[float] = field(default_factory=list)
    best_epoch: int = 0
    best_val_loss: float = float("inf")
    test_accuracy: float = 0.0
    test_f1: float = 0.0
    confusion_matrix: Optional[List[List[int]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def stratified_split(X: np.ndarray, y: np.ndarray, test_size: float = 0.2, val_size: float = 0.1, random_state: int = 42) -> DatasetSplit:
    rng = np.random.default_rng(random_state)
    indices = np.arange(len(y))
    rng.shuffle(indices)
    n_test = int(len(y) * test_size)
    n_val = int(len(y) * val_size)
    test_idx = indices[:n_test]
    val_idx = indices[n_test:n_test + n_val]
    train_idx = indices[n_test + n_val:]
    return DatasetSplit(
        X_train=X[train_idx], y_train=y[train_idx],
        X_val=X[val_idx], y_val=y[val_idx],
        X_test=X[test_idx], y_test=y[test_idx],
    )


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    accuracy = (tp + tn) / max(1, tp + tn + fp + fn)
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-12, precision + recall)
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
    }


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int = 2) -> List[List[int]]:
    cm = [[0] * num_classes for _ in range(num_classes)]
    for t, p in zip(y_true, y_pred):
        cm[int(t)][int(p)] += 1
    return cm


class EarlyStopping:
    def __init__(self, patience: int = 5, min_delta: float = 1e-4) -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.best = float("inf")
        self.counter = 0
        self.should_stop = False

    def step(self, value: float) -> bool:
        if value < self.best - self.min_delta:
            self.best = value
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop


class LearningRateScheduler:
    def __init__(self, base_lr: float, decay: float = 0.95, step_size: int = 5) -> None:
        self.base_lr = base_lr
        self.decay = decay
        self.step_size = step_size
        self.epoch = 0

    def get_lr(self, epoch: int) -> float:
        return self.base_lr * (self.decay ** (epoch // self.step_size))


class CrossValidator:
    def __init__(self, n_splits: int = 5, shuffle: bool = True, random_state: int = 42) -> None:
        self.n_splits = n_splits
        self.shuffle = shuffle
        self.random_state = random_state

    def split(self, X: np.ndarray, y: np.ndarray):
        n = len(y)
        indices = np.arange(n)
        if self.shuffle:
            rng = np.random.default_rng(self.random_state)
            rng.shuffle(indices)
        fold_sizes = np.full(self.n_splits, n // self.n_splits, dtype=int)
        fold_sizes[: n % self.n_splits] += 1
        current = 0
        folds = []
        for size in fold_sizes:
            folds.append(indices[current:current + size])
            current += size
        for i in range(self.n_splits):
            test_idx = folds[i]
            train_idx = np.concatenate([folds[j] for j in range(self.n_splits) if j != i])
            yield train_idx, test_idx


class ExperimentTracker:
    def __init__(self, output_dir: str = "./experiments") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.runs: List[Dict[str, Any]] = []

    def log_run(self, result: TrainingResult, extra: Optional[Dict[str, Any]] = None) -> str:
        run_id = f"run_{len(self.runs):04d}"
        payload = {
            "run_id": run_id,
            "model_name": result.model_name,
            "best_epoch": result.best_epoch,
            "best_val_loss": result.best_val_loss,
            "test_accuracy": result.test_accuracy,
            "test_f1": result.test_f1,
            "confusion_matrix": result.confusion_matrix,
            "metadata": result.metadata,
        }
        if extra:
            payload.update(extra)
        path = self.output_dir / f"{run_id}.json"
        path.write_text(json.dumps(payload, indent=2, default=str))
        self.runs.append(payload)
        return run_id

    def summary(self) -> List[Dict[str, Any]]:
        return list(self.runs)


class FeatureExtractor:
    """Extract hand-crafted audio features from a waveform."""

    def __init__(self, sr: int = 22050) -> None:
        self.sr = sr

    def extract_mfcc(self, y: np.ndarray, n_mfcc: int = 13) -> np.ndarray:
        import librosa

        mfcc = librosa.feature.mfcc(y=y, sr=self.sr, n_mfcc=n_mfcc)
        return np.mean(mfcc, axis=1)

    def extract_spectral(self, y: np.ndarray) -> np.ndarray:
        import librosa

        centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=self.sr))
        bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=self.sr))
        rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=self.sr))
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        return np.array([centroid, bandwidth, rolloff, zcr])

    def extract_rhythm(self, y: np.ndarray) -> np.ndarray:
        import librosa

        tempo, _ = librosa.beat.beat_track(y=y, sr=self.sr)
        onset_env = librosa.onset.onset_strength(y=y, sr=self.sr)
        onset_mean = float(np.mean(onset_env))
        return np.array([float(tempo), onset_mean])

    def extract_all(self, y: np.ndarray) -> np.ndarray:
        mfcc = self.extract_mfcc(y)
        spectral = self.extract_spectral(y)
        rhythm = self.extract_rhythm(y)
        return np.concatenate([mfcc, spectral, rhythm])


class DataAugmenter:
    def __init__(self, sr: int = 22050) -> None:
        self.sr = sr

    def add_noise(self, y: np.ndarray, noise_factor: float = 0.005) -> np.ndarray:
        noise = np.random.randn(len(y))
        return y + noise_factor * noise

    def time_shift(self, y: np.ndarray, shift_max: float = 0.2) -> np.ndarray:
        shift = int(len(y) * np.random.uniform(-shift_max, shift_max))
        return np.roll(y, shift)

    def pitch_shift(self, y: np.ndarray, n_steps: float = 2.0) -> np.ndarray:
        import librosa

        return librosa.effects.pitch_shift(y, sr=self.sr, n_steps=n_steps)

    def time_stretch(self, y: np.ndarray, rate: float = 1.1) -> np.ndarray:
        import librosa

        return librosa.effects.time_stretch(y, rate=rate)

    def augment_batch(self, y: np.ndarray, n_augmentations: int = 3) -> List[np.ndarray]:
        out = [y]
        methods = [self.add_noise, self.time_shift]
        for _ in range(n_augmentations):
            method = methods[np.random.randint(len(methods))]
            out.append(method(y))
        return out


class ModelEvaluator:
    def __init__(self) -> None:
        pass

    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        metrics = compute_metrics(y_true, y_pred)
        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm
        return metrics

    def compare_models(self, results: Dict[str, Dict[str, float]]) -> List[Tuple[str, float]]:
        ranked = sorted(results.items(), key=lambda kv: kv[1].get("f1", 0.0), reverse=True)
        return [(name, m.get("f1", 0.0)) for name, m in ranked]

    def threshold_analysis(self, y_true: np.ndarray, y_scores: np.ndarray, thresholds: Optional[List[float]] = None) -> List[Dict[str, float]]:
        if thresholds is None:
            thresholds = [i / 100 for i in range(1, 100)]
        out = []
        for thr in thresholds:
            preds = (y_scores >= thr).astype(int)
            m = compute_metrics(y_true, preds)
            m["threshold"] = thr
            out.append(m)
        return out


class HyperparameterTuner:
    def __init__(self, param_grid: Dict[str, List[Any]]) -> None:
        self.param_grid = param_grid

    def grid_combinations(self) -> List[Dict[str, Any]]:
        import itertools

        keys = list(self.param_grid.keys())
        values = [self.param_grid[k] for k in keys]
        combos = []
        for combo in itertools.product(*values):
            combos.append(dict(zip(keys, combo)))
        return combos

    def random_combinations(self, n: int = 10, seed: int = 42) -> List[Dict[str, Any]]:
        rng = np.random.default_rng(seed)
        combos = self.grid_combinations()
        if n >= len(combos):
            return combos
        idx = rng.choice(len(combos), size=n, replace=False)
        return [combos[i] for i in idx]


def save_training_result(result: TrainingResult, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps({
        "model_name": result.model_name,
        "best_epoch": result.best_epoch,
        "best_val_loss": result.best_val_loss,
        "test_accuracy": result.test_accuracy,
        "test_f1": result.test_f1,
        "confusion_matrix": result.confusion_matrix,
        "train_loss": result.train_loss,
        "val_loss": result.val_loss,
        "metadata": result.metadata,
    }, indent=2, default=str))


def load_training_result(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text())
