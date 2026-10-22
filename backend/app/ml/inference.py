"""Machine learning model definitions and loading utilities."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import torch
import torchaudio
from torch import nn

from backend.app.config import get_settings
from backend.app.logging_config import get_logger

logger = get_logger("app.ml")

# ==========================================================
# Model Definitions
# ==========================================================


class MLP(nn.Module):
    def __init__(self, input_dim: int = 13) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class CNNClassifier(nn.Module):
    def __init__(self, n_mels: int = 64, num_classes: int = 2, target_len: int = 173) -> None:
        super().__init__()
        self.n_mels = n_mels
        self.target_len = target_len
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        with torch.no_grad():
            dummy = torch.randn(1, 1, n_mels, target_len)
            flatten_dim = self.features(dummy).view(1, -1).size(1)
        self.classifier = nn.Sequential(
            nn.Linear(flatten_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)


MODEL_ACCURACY: dict[str, float] = {
    "svm": 0.77,
    "rf": 0.87,
    "xgboost": 0.87,
    "mlp": 0.87,
    "early_stopping_mlp": 0.87,
    "cnn": 0.979,
    "early_stopping_cnn": 0.988,
}


@dataclass
class ModelBundle:
    scaler: Any
    svm: Any
    rf: Any
    xgb: Any
    label_encoder: Any
    mlp: MLP
    early_mlp: MLP
    cnn: CNNClassifier
    early_cnn: CNNClassifier
    device: str


_bundle: ModelBundle | None = None


def _model_path(name: str) -> Path:
    settings = get_settings()
    base = Path(settings.model_dir)
    # Fallback to src/ if models not found in configured dir
    if not base.exists():
        candidate = Path("src")
        if (candidate / name).exists():
            base = candidate
    return base / name


def load_models(force: bool = False) -> ModelBundle:
    """Load all models (cached)."""
    global _bundle
    if _bundle is not None and not force:
        return _bundle

    settings = get_settings()
    device = settings.device
    base = Path(settings.model_dir)
    if not base.exists() and Path("src").exists():
        base = Path("src")
        settings.model_dir = str(base)

    logger.info("Loading ML models", extra={"model_dir": str(base), "device": device})

    scaler = joblib.load(base / "scaler.pkl")
    svm = joblib.load(base / "svm_ai_vs_real.pkl")
    rf = joblib.load(base / "rf_ai_vs_real.pkl")
    xgb = joblib.load(base / "xgb_ai_vs_real.pkl")
    le = joblib.load(base / "label_encoder.pkl")

    mlp = MLP(13)
    mlp.load_state_dict(torch.load(base / "mlp_ai_vs_real.pth", map_location="cpu"))
    mlp.eval()

    early_mlp = MLP(13)
    early_mlp.load_state_dict(torch.load(base / "early_stopping_mlp_ai_vs_real.pth", map_location="cpu"))
    early_mlp.eval()

    cnn = CNNClassifier(n_mels=64)
    cnn.load_state_dict(torch.load(base / "cnn_ai_vs_real.pth", map_location="cpu"))
    cnn.eval()

    early_cnn = CNNClassifier(n_mels=64)
    early_cnn.load_state_dict(torch.load(base / "early_stopping_epoch_cnn_ai_vs_real_best.pth", map_location="cpu"))
    early_cnn.eval()

    _bundle = ModelBundle(
        scaler=scaler,
        svm=svm,
        rf=rf,
        xgb=xgb,
        label_encoder=le,
        mlp=mlp,
        early_mlp=early_mlp,
        cnn=cnn,
        early_cnn=early_cnn,
        device=device,
    )
    logger.info("ML models loaded successfully")
    return _bundle


def reset_models() -> None:
    global _bundle
    _bundle = None


def preprocess_for_cnn(chunk: np.ndarray, sr: int, n_mels: int = 64, target_len: int = 173) -> torch.Tensor:
    waveform = torch.tensor(chunk, dtype=torch.float32).unsqueeze(0)
    if sr != 16000:
        resample = torchaudio.transforms.Resample(sr, 16000)
        waveform = resample(waveform)
        sr = 16000

    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=16000, n_fft=1024, hop_length=512, n_mels=n_mels
    )
    db_transform = torchaudio.transforms.AmplitudeToDB()

    mel = mel_transform(waveform)
    logmel = db_transform(mel)

    if logmel.shape[-1] < target_len:
        pad_amount = target_len - logmel.shape[-1]
        logmel = nn.functional.pad(logmel, (0, pad_amount))
    else:
        logmel = logmel[:, :, :target_len]

    return logmel.unsqueeze(0)


def predict_chunk(chunk: np.ndarray, sr: int, bundle: ModelBundle | None = None) -> dict[str, str]:
    if bundle is None:
        bundle = load_models()
    import librosa

    mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1).reshape(1, -1)
    x = bundle.scaler.transform(mfcc_mean)

    p_svm = bundle.svm.predict(x)[0]
    p_rf = bundle.rf.predict(x)[0]
    p_xgb = bundle.label_encoder.inverse_transform([bundle.xgb.predict(x)[0]])[0]

    with torch.no_grad():
        p_mlp = ["real", "ai"][bundle.mlp(torch.tensor(x, dtype=torch.float32)).argmax().item()]
        p_early_mlp = ["real", "ai"][bundle.early_mlp(torch.tensor(x, dtype=torch.float32)).argmax().item()]

    logmel_tensor = preprocess_for_cnn(chunk, sr=sr, n_mels=64, target_len=173)
    with torch.no_grad():
        p_cnn = ["real", "ai"][bundle.cnn(logmel_tensor).argmax().item()]
        p_early_cnn = ["real", "ai"][bundle.early_cnn(logmel_tensor).argmax().item()]

    return {
        "svm": p_svm,
        "rf": p_rf,
        "xgboost": p_xgb,
        "mlp": p_mlp,
        "early_stopping_mlp": p_early_mlp,
        "cnn": p_cnn,
        "early_stopping_cnn": p_early_cnn,
    }


def ensemble_predict(file_path: str, chunk_sec: int = 10, sr: int = 22050) -> tuple:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    import librosa

    y, _ = librosa.load(file_path, sr=sr, mono=True)
    chunk_samples = chunk_sec * sr
    chunks = [y[i : i + chunk_samples] for i in range(0, len(y), chunk_samples)]

    bundle = load_models()
    preds_all_chunks = []

    for chunk in chunks:
        preds_dict = predict_chunk(chunk, sr, bundle=bundle)

        from collections import Counter

        majority_counts = Counter(preds_dict.values())
        max_count = max(majority_counts.values())
        top_preds = [k for k, v in majority_counts.items() if v == max_count]

        if len(top_preds) == 1:
            chunk_majority = top_preds[0]
        else:
            sorted_models = sorted(preds_dict.items(), key=lambda x: MODEL_ACCURACY[x[0]], reverse=True)
            chunk_majority = top_preds[0]
            for model_name, pred in sorted_models:
                if pred in top_preds:
                    chunk_majority = pred
                    break

        preds_all_chunks.append({"preds_per_model": preds_dict, "chunk_majority": chunk_majority})

    model_wise = {}
    for model in MODEL_ACCURACY:
        votes = [c["preds_per_model"][model] for c in preds_all_chunks]
        model_wise[model] = __import__("collections").Counter(votes).most_common(1)[0][0]

    return preds_all_chunks, model_wise
