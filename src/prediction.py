import os
import torch
import torch.nn as nn
import librosa
import numpy as np
import joblib
from collections import Counter
import torchaudio


# ==========================================================
# Model Definitions
# ==========================================================

class MLP(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 2)
        )

    def forward(self, x):
        return self.net(x)


class CNNClassifier(nn.Module):
    def __init__(self, n_mels=64, num_classes=2, target_len=173):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        with torch.no_grad():
            dummy = torch.randn(1, 1, n_mels, target_len)
            flatten_dim = self.features(dummy).view(1, -1).size(1)

        self.classifier = nn.Sequential(
            nn.Linear(flatten_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)


# ==========================================================
# Load Models
# ==========================================================

scaler = joblib.load("scaler.pkl")
svm = joblib.load("svm_ai_vs_real.pkl")
rf = joblib.load("rf_ai_vs_real.pkl")
xgb = joblib.load("xgb_ai_vs_real.pkl")
le = joblib.load("label_encoder.pkl")

mlp = MLP(13)
mlp.load_state_dict(torch.load("mlp_ai_vs_real.pth", map_location="cpu"))
mlp.eval()

early_mlp = MLP(13)
early_mlp.load_state_dict(torch.load("early_stopping_mlp_ai_vs_real.pth", map_location="cpu"))
early_mlp.eval()

cnn = CNNClassifier(n_mels=64)
cnn.load_state_dict(torch.load("cnn_ai_vs_real.pth", map_location="cpu"))
cnn.eval()

early_cnn = CNNClassifier(n_mels=64)
early_cnn.load_state_dict(torch.load("early_stopping_epoch_cnn_ai_vs_real_best.pth", map_location="cpu"))
early_cnn.eval()


# ==========================================================
# Model Accuracy (used for tie-breaking)
# ==========================================================

model_accuracy = {
    'svm': 0.77,
    'rf': 0.87,
    'xgboost': 0.87,
    'mlp': 0.87,
    'early_stopping_mlp': 0.87,
    'cnn': 0.979,
    'early_stopping_cnn': 0.988
}


# ==========================================================
# Helper: CNN Preprocessing
# ==========================================================

def preprocess_for_cnn(chunk, sr, n_mels=64, target_len=173):
    waveform = torch.tensor(chunk).unsqueeze(0)
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

    return logmel.unsqueeze(0)  # (1, 1, n_mels, target_len)


# ==========================================================
# Main Ensemble Prediction Function
# ==========================================================

def ensemble_predict(file_path, chunk_sec=10, sr=22050):
    """
    Returns:
        chunk_predictions: list of dicts with model outputs per chunk
        model_majority: dict showing per-model majority across chunks
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    y, _ = librosa.load(file_path, sr=sr, mono=True)
    chunk_samples = chunk_sec * sr
    chunks = [y[i:i + chunk_samples] for i in range(0, len(y), chunk_samples)]

    preds_all_chunks = []

    for chunk in chunks:
        # === Classical + MLP ===
        mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1).reshape(1, -1)
        X = scaler.transform(mfcc_mean)

        p_svm = svm.predict(X)[0]
        p_rf = rf.predict(X)[0]
        p_xgb = le.inverse_transform([xgb.predict(X)[0]])[0]

        with torch.no_grad():
            p_mlp = ["real", "ai"][mlp(torch.tensor(X, dtype=torch.float32)).argmax().item()]
            p_early_mlp = ["real", "ai"][early_mlp(torch.tensor(X, dtype=torch.float32)).argmax().item()]

        # === CNN ===
        logmel_tensor = preprocess_for_cnn(chunk, sr=sr, n_mels=64, target_len=173)
        with torch.no_grad():
            p_cnn = ["real", "ai"][cnn(logmel_tensor).argmax().item()]
            p_early_cnn = ["real", "ai"][early_cnn(logmel_tensor).argmax().item()]

        preds_dict = {
            'svm': p_svm,
            'rf': p_rf,
            'xgboost': p_xgb,
            'mlp': p_mlp,
            'early_stopping_mlp': p_early_mlp,
            'cnn': p_cnn,
            'early_stopping_cnn': p_early_cnn
        }

        # Majority vote for this chunk
        majority_counts = Counter(preds_dict.values())
        max_count = max(majority_counts.values())
        top_preds = [k for k, v in majority_counts.items() if v == max_count]

        if len(top_preds) == 1:
            chunk_majority = top_preds[0]
        else:
            sorted_models = sorted(preds_dict.items(), key=lambda x: model_accuracy[x[0]], reverse=True)
            for model_name, pred in sorted_models:
                if pred in top_preds:
                    chunk_majority = pred
                    break

        preds_all_chunks.append({'preds_per_model': preds_dict, 'chunk_majority': chunk_majority})

    # === Model-wise majority across chunks ===
    model_wise = {}
    for model in model_accuracy.keys():
        votes = [c['preds_per_model'][model] for c in preds_all_chunks]
        model_wise[model] = Counter(votes).most_common(1)[0][0]

    return preds_all_chunks, model_wise
