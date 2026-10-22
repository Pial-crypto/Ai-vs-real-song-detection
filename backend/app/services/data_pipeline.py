"""Data processing pipeline for audio datasets."""

from __future__ import annotations

import csv
import json
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


def load_audio(path: str, sr: int = 22050, mono: bool = True) -> Tuple[np.ndarray, int]:
    import librosa

    y, sr = librosa.load(path, sr=sr, mono=mono)
    return y, sr


def save_audio(path: str, y: np.ndarray, sr: int = 22050) -> None:
    import soundfile as sf

    sf.write(path, y, sr)


def resample(y: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    import librosa

    return librosa.resample(y, orig_sr=orig_sr, target_sr=target_sr)


def trim_silence(y: np.ndarray, top_db: int = 30) -> np.ndarray:
    import librosa

    y_trimmed, _ = librosa.effects.trim(y, top_db=top_db)
    return y_trimmed


def normalize_audio(y: np.ndarray, method: str = "peak") -> np.ndarray:
    y = np.asarray(y, dtype=float)
    if method == "peak":
        mx = np.max(np.abs(y)) if y.size else 1.0
        if mx == 0:
            mx = 1.0
        return y / mx
    if method == "rms":
        rms = np.sqrt(np.mean(y ** 2)) if y.size else 1.0
        if rms == 0:
            rms = 1.0
        return y / rms
    return y


def pad_audio(y: np.ndarray, target_len: int, mode: str = "constant") -> np.ndarray:
    if len(y) >= target_len:
        return y[:target_len]
    pad = target_len - len(y)
    if mode == "constant":
        return np.pad(y, (0, pad))
    if mode == "reflect":
        return np.pad(y, (0, pad), mode="reflect")
    if mode == "wrap":
        return np.pad(y, (0, pad), mode="wrap")
    return np.pad(y, (0, pad))


def chunk_audio(y: np.ndarray, chunk_sec: int, sr: int) -> List[np.ndarray]:
    chunk_samples = chunk_sec * sr
    return [y[i:i + chunk_samples] for i in range(0, len(y), chunk_samples)]


def compute_mfcc(y: np.ndarray, sr: int = 22050, n_mfcc: int = 13) -> np.ndarray:
    import librosa

    return librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)


def compute_mel(y: np.ndarray, sr: int = 22050, n_mels: int = 64) -> np.ndarray:
    import librosa

    return librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)


def compute_chroma(y: np.ndarray, sr: int = 22050) -> np.ndarray:
    import librosa

    return librosa.feature.chroma_stft(y=y, sr=sr)


def compute_spectral_contrast(y: np.ndarray, sr: int = 22050) -> np.ndarray:
    import librosa

    return librosa.feature.spectral_contrast(y=y, sr=sr)


def compute_tonnetz(y: np.ndarray, sr: int = 22050) -> np.ndarray:
    import librosa

    return librosa.feature.tonnetz(y=y, sr=sr)


def compute_tempogram(y: np.ndarray, sr: int = 22050) -> np.ndarray:
    import librosa

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    return librosa.feature.tempogram(onset_enn=onset_env, sr=sr)


def compute_onset_env(y: np.ndarray, sr: int = 22050) -> np.ndarray:
    import librosa

    return librosa.onset.onset_strength(y=y, sr=sr)


def compute_beats(y: np.ndarray, sr: int = 22050) -> Tuple[float, np.ndarray]:
    import librosa

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    return float(tempo), beats


def compute_hpss(y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    import librosa

    return librosa.effects.hpss(y)


def compute_pitch(y: np.ndarray, sr: int = 22050) -> Tuple[np.ndarray, np.ndarray]:
    import librosa

    f0, voiced, prob = librosa.pyin(y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr)
    return f0, prob


def compute_rms(y: np.ndarray) -> np.ndarray:
    import librosa

    return librosa.feature.rms(y=y)


def compute_zcr(y: np.ndarray) -> np.ndarray:
    import librosa

    return librosa.feature.zero_crossing_rate(y)


def compute_spectral_centroid(y: np.ndarray, sr: int = 22050) -> np.ndarray:
    import librosa

    return librosa.feature.spectral_centroid(y=y, sr=sr)


def compute_spectral_bandwidth(y: np.ndarray, sr: int = 22050) -> np.ndarray:
    import librosa

    return librosa.feature.spectral_bandwidth(y=y, sr=sr)


def compute_spectral_rolloff(y: np.ndarray, sr: int = 22050) -> np.ndarray:
    import librosa

    return librosa.feature.spectral_rolloff(y=y, sr=sr)


def compute_spectral_flatness(y: np.ndarray) -> np.ndarray:
    import librosa

    return librosa.feature.spectral_flatness(y=y)


class FeaturePipeline:
    def __init__(self, sr: int = 22050, n_mfcc: int = 13, n_mels: int = 64) -> None:
        self.sr = sr
        self.n_mfcc = n_mfcc
        self.n_mels = n_mels

    def run(self, y: np.ndarray) -> Dict[str, Any]:
        return {
            "mfcc": compute_mfcc(y, self.sr, self.n_mfcc),
            "mel": compute_mel(y, self.sr, self.n_mels),
            "chroma": compute_chroma(y, self.sr),
            "spectral_contrast": compute_spectral_contrast(y, self.sr),
            "tonnetz": compute_tonnetz(y, self.sr),
            "rms": compute_rms(y),
            "zcr": compute_zcr(y),
            "spectral_centroid": compute_spectral_centroid(y, self.sr),
            "spectral_bandwidth": compute_spectral_bandwidth(y, self.sr),
            "spectral_rolloff": compute_spectral_rolloff(y, self.sr),
            "spectral_flatness": compute_spectral_flatness(y),
        }

    def summarize(self, features: Dict[str, Any]) -> Dict[str, float]:
        out = {}
        for k, v in features.items():
            arr = np.asarray(v, dtype=float)
            out[f"{k}_mean"] = float(np.mean(arr))
            out[f"{k}_std"] = float(np.std(arr))
            out[f"{k}_min"] = float(np.min(arr))
            out[f"{k}_max"] = float(np.max(arr))
        return out

    def to_vector(self, features: Dict[str, Any]) -> List[float]:
        vec = []
        for k in sorted(features.keys()):
            arr = np.asarray(features[k], dtype=float).ravel()
            vec.extend([float(np.mean(arr)), float(np.std(arr)), float(np.min(arr)), float(np.max(arr))])
        return vec


class DatasetBuilder:
    def __init__(self, root_dir: str, sr: int = 22050) -> None:
        self.root_dir = root_dir
        self.sr = sr

    def scan(self, extensions: Tuple[str, ...] = (".wav", ".mp3", ".flac")) -> List[str]:
        files = []
        for root, _, fs in os.walk(self.root_dir):
            for f in fs:
                if f.lower().endswith(extensions):
                    files.append(os.path.join(root, f))
        return sorted(files)

    def load_all(self) -> List[Tuple[str, np.ndarray]]:
        out = []
        for p in self.scan():
            y, _ = load_audio(p, sr=self.sr)
            out.append((p, y))
        return out

    def build_features(self, pipeline: FeaturePipeline) -> List[Tuple[str, List[float]]]:
        out = []
        for path, y in self.load_all():
            feats = pipeline.run(y)
            vec = pipeline.to_vector(feats)
            out.append((path, vec))
        return out

    def save_features(self, path: str, data: List[Tuple[str, List[float]]]) -> None:
        with open(path, "w") as f:
            json.dump([{"path": p, "features": v} for p, v in data], f)

    def load_features(self, path: str) -> List[Tuple[str, List[float]]]:
        with open(path) as f:
            data = json.load(f)
        return [(d["path"], d["features"]) for d in data]


class DataAugmentation:
    def __init__(self, sr: int = 22050) -> None:
        self.sr = sr

    def add_noise(self, y: np.ndarray, snr_db: float = 20.0) -> np.ndarray:
        rms = np.sqrt(np.mean(y ** 2)) if y.size else 1.0
        noise_rms = rms / (10 ** (snr_db / 20))
        noise = np.random.normal(0, noise_rms, size=y.shape)
        return y + noise

    def time_stretch(self, y: np.ndarray, rate: float = 1.0) -> np.ndarray:
        import librosa

        return librosa.effects.time_stretch(y, rate=rate)

    def pitch_shift(self, y: np.ndarray, n_steps: float = 0.0) -> np.ndarray:
        import librosa

        return librosa.effects.pitch_shift(y, sr=self.sr, n_steps=n_steps)

    def shift(self, y: np.ndarray, shift: int) -> np.ndarray:
        return np.roll(y, shift)

    def reverse(self, y: np.ndarray) -> np.ndarray:
        return y[::-1].copy()

    def fade_in(self, y: np.ndarray, duration: float = 0.5) -> np.ndarray:
        n = int(duration * self.sr)
        n = min(n, len(y))
        fade = np.linspace(0, 1, n)
        out = y.copy()
        out[:n] *= fade
        return out

    def fade_out(self, y: np.ndarray, duration: float = 0.5) -> np.ndarray:
        n = int(duration * self.sr)
        n = min(n, len(y))
        fade = np.linspace(1, 0, n)
        out = y.copy()
        out[-n:] *= fade
        return out

    def gain(self, y: np.ndarray, db: float = 0.0) -> np.ndarray:
        return y * (10 ** (db / 20))

    def clip(self, y: np.ndarray, threshold: float = 0.99) -> np.ndarray:
        return np.clip(y, -threshold, threshold)

    def random_crop(self, y: np.ndarray, crop_len: int) -> np.ndarray:
        if len(y) <= crop_len:
            return pad_audio(y, crop_len)
        start = np.random.randint(0, len(y) - crop_len)
        return y[start:start + crop_len]

    def mix(self, y1: np.ndarray, y2: np.ndarray, alpha: float = 0.5) -> np.ndarray:
        n = min(len(y1), len(y2))
        return alpha * y1[:n] + (1 - alpha) * y2[:n]

    def augment_batch(self, y: np.ndarray, n: int = 4) -> List[np.ndarray]:
        out = [y]
        methods = [self.add_noise, lambda x: self.time_stretch(x, 1.1), lambda x: self.pitch_shift(x, 2.0), self.reverse]
        for i in range(n):
            m = methods[i % len(methods)]
            try:
                out.append(m(y))
            except Exception:
                out.append(y.copy())
        return out


class DataValidator:
    def __init__(self) -> None:
        pass

    def is_valid_audio(self, y: np.ndarray) -> bool:
        if y is None or len(y) == 0:
            return False
        if not np.all(np.isfinite(y)):
            return False
        return True

    def check_duration(self, y: np.ndarray, sr: int, min_sec: float = 1.0, max_sec: float = 600.0) -> bool:
        dur = len(y) / sr
        return min_sec <= dur <= max_sec

    def check_clipping(self, y: np.ndarray, threshold: float = 0.99) -> bool:
        return bool(np.max(np.abs(y)) < threshold) if y.size else True

    def check_silence(self, y: np.ndarray, threshold: float = 1e-4) -> bool:
        rms = np.sqrt(np.mean(y ** 2)) if y.size else 0.0
        return rms >= threshold

    def validate_all(self, y: np.ndarray, sr: int) -> Dict[str, bool]:
        return {
            "valid_audio": self.is_valid_audio(y),
            "duration_ok": self.check_duration(y, sr),
            "no_clipping": self.check_clipping(y),
            "not_silent": self.check_silence(y),
        }


class DataSplitter:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def split(self, items: List[Any], ratios: Tuple[float, ...] = (0.8, 0.1, 0.1)) -> List[List[Any]]:
        rng = np.random.default_rng(self.seed)
        idx = np.arange(len(items))
        rng.shuffle(idx)
        n = len(items)
        boundaries = [0]
        acc = 0
        for r in ratios[:-1]:
            acc += int(n * r)
            boundaries.append(acc)
        boundaries.append(n)
        out = []
        for i in range(len(ratios)):
            out.append([items[idx[j]] for j in range(boundaries[i], boundaries[i + 1])])
        return out

    def stratified_split(self, items: List[Any], labels: List[int], ratios=(0.8, 0.1, 0.1)) -> List[List[Any]]:
        from collections import defaultdict

        groups = defaultdict(list)
        for it, lab in zip(items, labels):
            groups[lab].append(it)
        splits = [[] for _ in ratios]
        for lab, grp in groups.items():
            grp_splits = self.split(grp, ratios)
            for i, part in enumerate(grp_splits):
                splits[i].extend(part)
        return splits


class DataBalancer:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def oversample(self, items: List[Any], labels: List[int]) -> Tuple[List[Any], List[int]]:
        from collections import Counter

        c = Counter(labels)
        max_count = max(c.values()) if c else 0
        rng = np.random.default_rng(self.seed)
        new_items = list(items)
        new_labels = list(labels)
        for cls, cnt in c.items():
            need = max_count - cnt
            idxs = [i for i, lab in enumerate(labels) if lab == cls]
            for _ in range(need):
                i = rng.choice(idxs)
                new_items.append(items[i])
                new_labels.append(labels[i])
        return new_items, new_labels

    def undersample(self, items: List[Any], labels: List[int]) -> Tuple[List[Any], List[int]]:
        from collections import Counter

        c = Counter(labels)
        min_count = min(c.values()) if c else 0
        rng = np.random.default_rng(self.seed)
        new_items = []
        new_labels = []
        for cls in c:
            idxs = [i for i, lab in enumerate(labels) if lab == cls]
            chosen = rng.choice(idxs, size=min_count, replace=False)
            for i in chosen:
                new_items.append(items[i])
                new_labels.append(labels[i])
        return new_items, new_labels


class DataExporter:
    def __init__(self) -> None:
        pass

    def to_csv(self, rows: List[Dict[str, Any]], path: str) -> None:
        if not rows:
            return
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def to_json(self, rows: List[Dict[str, Any]], path: str) -> None:
        with open(path, "w") as f:
            json.dump(rows, f, indent=2, default=str)

    def to_jsonl(self, rows: List[Dict[str, Any]], path: str) -> None:
        with open(path, "w") as f:
            for r in rows:
                f.write(json.dumps(r, default=str) + "\n")

    def from_csv(self, path: str) -> List[Dict[str, Any]]:
        with open(path) as f:
            return list(csv.DictReader(f))

    def from_json(self, path: str) -> List[Dict[str, Any]]:
        with open(path) as f:
            return json.load(f)

    def from_jsonl(self, path: str) -> List[Dict[str, Any]]:
        out = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out


class DataImporter:
    def __init__(self) -> None:
        pass

    def from_directory(self, directory: str, extensions: Tuple[str, ...] = (".wav", ".mp3")) -> List[str]:
        files = []
        for root, _, fs in os.walk(directory):
            for f in fs:
                if f.lower().endswith(extensions):
                    files.append(os.path.join(root, f))
        return sorted(files)

    def from_manifest(self, path: str) -> List[Dict[str, Any]]:
        with open(path) as f:
            return json.load(f)

    def from_csv_manifest(self, path: str) -> List[Dict[str, Any]]:
        with open(path) as f:
            return list(csv.DictReader(f))


class DataCleaner:
    def __init__(self) -> None:
        pass

    def remove_duplicates(self, items: List[Any]) -> List[Any]:
        seen = set()
        out = []
        for it in items:
            key = str(it)
            if key not in seen:
                seen.add(key)
                out.append(it)
        return out

    def remove_empty(self, items: List[Any]) -> List[Any]:
        return [it for it in items if it is not None and it != "" and it != []]

    def fill_missing(self, items: List[Optional[Any]], fill: Any = 0) -> List[Any]:
        return [fill if it is None else it for it in items]

    def clip_values(self, values: List[float], low: float, high: float) -> List[float]:
        return [max(low, min(high, v)) for v in values]

    def standardize(self, values: List[float]) -> List[float]:
        arr = np.asarray(values, dtype=float)
        mu = arr.mean() if arr.size else 0.0
        sd = arr.std() if arr.size else 1.0
        if sd == 0:
            sd = 1.0
        return ((arr - mu) / sd).tolist()


class DataStatistics:
    def __init__(self) -> None:
        pass

    def describe(self, values: List[float]) -> Dict[str, float]:
        arr = np.asarray(values, dtype=float)
        if arr.size == 0:
            return {"count": 0, "mean": 0, "std": 0, "min": 0, "max": 0, "median": 0}
        return {
            "count": float(arr.size),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "median": float(np.median(arr)),
            "q25": float(np.percentile(arr, 25)),
            "q75": float(np.percentile(arr, 75)),
        }

    def correlation(self, x: List[float], y: List[float]) -> float:
        a = np.asarray(x, dtype=float)
        b = np.asarray(y, dtype=float)
        n = min(a.size, b.size)
        a = a[:n] - a[:n].mean()
        b = b[:n] - b[:n].mean()
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def covariance(self, x: List[float], y: List[float]) -> float:
        a = np.asarray(x, dtype=float)
        b = np.asarray(y, dtype=float)
        n = min(a.size, b.size)
        return float(np.cov(a[:n], b[:n])[0, 1])

    def histogram(self, values: List[float], bins: int = 10) -> Tuple[List[float], List[float]]:
        counts, edges = np.histogram(values, bins=bins)
        return counts.tolist(), edges.tolist()

    def value_counts(self, values: List[Any]) -> Dict[Any, int]:
        from collections import Counter

        return dict(Counter(values))


class DataTransformer:
    def __init__(self) -> None:
        pass

    def apply(self, values: List[Any], func: Callable) -> List[Any]:
        return [func(v) for v in values]

    def map_values(self, values: List[Any], mapping: Dict[Any, Any]) -> List[Any]:
        return [mapping.get(v, v) for v in values]

    def filter_values(self, values: List[Any], predicate: Callable) -> List[Any]:
        return [v for v in values if predicate(v)]

    def reduce_values(self, values: List[Any], func: Callable, init: Any = None) -> Any:
        acc = init
        for v in values:
            acc = func(acc, v) if acc is not None else v
        return acc

    def group_by(self, items: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
        from collections import defaultdict

        groups = defaultdict(list)
        for it in items:
            groups[it.get(key)].append(it)
        return dict(groups)

    def sort_by(self, items: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
        return sorted(items, key=lambda x: x.get(key), reverse=reverse)

    def unique_by(self, items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        seen = set()
        out = []
        for it in items:
            v = it.get(key)
            if v not in seen:
                seen.add(v)
                out.append(it)
        return out


def create_pipeline(sr: int = 22050) -> FeaturePipeline:
    return FeaturePipeline(sr=sr)


def run_pipeline_on_file(path: str, pipeline: Optional[FeaturePipeline] = None) -> Dict[str, Any]:
    if pipeline is None:
        pipeline = FeaturePipeline()
    y, sr = load_audio(path, sr=pipeline.sr)
    features = pipeline.run(y)
    return {"path": path, "features": features, "summary": pipeline.summarize(features)}


def run_pipeline_on_directory(directory: str, pipeline: Optional[FeaturePipeline] = None) -> List[Dict[str, Any]]:
    if pipeline is None:
        pipeline = FeaturePipeline()
    builder = DatasetBuilder(directory, sr=pipeline.sr)
    results = []
    for path, y in builder.load_all():
        features = pipeline.run(y)
        results.append({"path": path, "features": features, "summary": pipeline.summarize(features)})
    return results


def save_pipeline_results(results: List[Dict[str, Any]], path: str) -> None:
    with open(path, "w") as f:
        json.dump(results, f, default=str, indent=2)


def load_pipeline_results(path: str) -> List[Dict[str, Any]]:
    with open(path) as f:
        return json.load(f)


def compute_dataset_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_summaries = [r.get("summary", {}) for r in results]
    if not all_summaries:
        return {}
    keys = all_summaries[0].keys()
    out = {}
    for k in keys:
        vals = [s.get(k, 0) for s in all_summaries]
        out[k] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "min": float(np.min(vals)),
            "max": float(np.max(vals)),
        }
    return out


def filter_results(results: List[Dict[str, Any]], predicate: Callable) -> List[Dict[str, Any]]:
    return [r for r in results if predicate(r)]


def sort_results(results: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    return sorted(results, key=lambda r: r.get(key, 0), reverse=reverse)


def group_results(results: List[Dict[str, Any]], key: str) -> Dict[Any, List[Dict[str, Any]]]:
    from collections import defaultdict

    groups = defaultdict(list)
    for r in results:
        groups[r.get(key)].append(r)
    return dict(groups)


def merge_results(a: List[Dict[str, Any]], b: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return a + b


def deduplicate_results(results: List[Dict[str, Any]], key: str = "path") -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for r in results:
        v = r.get(key)
        if v not in seen:
            seen.add(v)
            out.append(r)
    return out


def sample_results(results: List[Dict[str, Any]], n: int, seed: int = 42) -> List[Dict[str, Any]]:
    rng = np.random.default_rng(seed)
    if n >= len(results):
        return list(results)
    idx = rng.choice(len(results), size=n, replace=False)
    return [results[i] for i in idx]


def split_results(results: List[Dict[str, Any]], test_size: float = 0.2, seed: int = 42) -> Tuple[List, List]:
    rng = np.random.default_rng(seed)
    idx = np.arange(len(results))
    rng.shuffle(idx)
    n_test = int(len(results) * test_size)
    test_idx = idx[:n_test]
    train_idx = idx[n_test:]
    return [results[i] for i in train_idx], [results[i] for i in test_idx]


def create_manifest(results: List[Dict[str, Any]], path: str) -> None:
    with open(path, "w") as f:
        json.dump(results, f, default=str, indent=2)


def read_manifest(path: str) -> List[Dict[str, Any]]:
    with open(path) as f:
        return json.load(f)


def validate_manifest(manifest: List[Dict[str, Any]]) -> bool:
    required = {"path", "features"}
    for entry in manifest:
        if not required.issubset(entry.keys()):
            return False
    return True


def convert_to_numpy(results: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[str]]:
    paths = [r["path"] for r in results]
    feats = [r["features"] if isinstance(r["features"], list) else r["summary"] for r in results]
    # flatten features to vectors if needed
    vecs = []
    for f in feats:
        if isinstance(f, dict):
            vecs.append(list(f.values()))
        else:
            vecs.append(list(f))
    return np.asarray(vecs, dtype=float), paths


def compute_feature_matrix(results: List[Dict[str, Any]]) -> np.ndarray:
    arr, _ = convert_to_numpy(results)
    return arr


def normalize_feature_matrix(X: np.ndarray) -> np.ndarray:
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd = np.where(sd == 0, 1.0, sd)
    return (X - mu) / sd


def reduce_dimensions(X: np.ndarray, n_components: int = 2) -> np.ndarray:
    from sklearn.decomposition import PCA

    pca = PCA(n_components=n_components)
    return pca.fit_transform(X)


def cluster_features(X: np.ndarray, n_clusters: int = 3) -> np.ndarray:
    from sklearn.cluster import KMeans

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    return km.fit_predict(X)


def detect_outliers(X: np.ndarray, contamination: float = 0.1) -> np.ndarray:
    from sklearn.ensemble import IsolationForest

    iso = IsolationForest(contamination=contamination, random_state=42)
    return iso.fit_predict(X)


def scale_features(X: np.ndarray, method: str = "standard") -> np.ndarray:
    if method == "standard":
        from sklearn.preprocessing import StandardScaler

        return StandardScaler().fit_transform(X)
    if method == "minmax":
        from sklearn.preprocessing import MinMaxScaler

        return MinMaxScaler().fit_transform(X)
    if method == "robust":
        from sklearn.preprocessing import RobustScaler

        return RobustScaler().fit_transform(X)
    return X


def encode_labels(labels: List[str]) -> Tuple[np.ndarray, Dict[str, int]]:
    from sklearn.preprocessing import LabelEncoder

    le = LabelEncoder()
    enc = le.fit_transform(labels)
    mapping = {cls: i for i, cls in enumerate(le.classes_)}
    return enc, mapping


def split_data(X: np.ndarray, y: np.ndarray, test_size: float = 0.2, seed: int = 42):
    from sklearn.model_selection import train_test_split

    return train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y if len(set(y)) > 1 else None)


def cross_validate_model(model, X: np.ndarray, y: np.ndarray, cv: int = 5) -> List[float]:
    from sklearn.model_selection import cross_val_score

    return cross_val_score(model, X, y, cv=cv).tolist()


def evaluate_classification(model, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

    preds = model.predict(X)
    return {
        "accuracy": float(accuracy_score(y, preds)),
        "precision": float(precision_score(y, preds, average="weighted", zero_division=0)),
        "recall": float(recall_score(y, preds, average="weighted", zero_division=0)),
        "f1": float(f1_score(y, preds, average="weighted", zero_division=0)),
    }


def evaluate_regression(model, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    preds = model.predict(X)
    return {
        "mse": float(mean_squared_error(y, preds)),
        "mae": float(mean_absolute_error(y, preds)),
        "r2": float(r2_score(y, preds)),
    }


def train_random_forest(X: np.ndarray, y: np.ndarray, n_estimators: int = 100):
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    model.fit(X, y)
    return model


def train_gradient_boosting(X: np.ndarray, y: np.ndarray, n_estimators: int = 100):
    from sklearn.ensemble import GradientBoostingClassifier

    model = GradientBoostingClassifier(n_estimators=n_estimators, random_state=42)
    model.fit(X, y)
    return model


def train_svm(X: np.ndarray, y: np.ndarray, kernel: str = "rbf"):
    from sklearn.svm import SVC

    model = SVC(kernel=kernel, probability=True, random_state=42)
    model.fit(X, y)
    return model


def train_logistic(X: np.ndarray, y: np.ndarray):
    from sklearn.linear_model import LogisticRegression

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X, y)
    return model


def train_knn(X: np.ndarray, y: np.ndarray, n_neighbors: int = 5):
    from sklearn.neighbors import KNeighborsClassifier

    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(X, y)
    return model


def train_decision_tree(X: np.ndarray, y: np.ndarray):
    from sklearn.tree import DecisionTreeClassifier

    model = DecisionTreeClassifier(random_state=42)
    model.fit(X, y)
    return model


def train_naive_bayes(X: np.ndarray, y: np.ndarray):
    from sklearn.naive_bayes import GaussianNB

    model = GaussianNB()
    model.fit(X, y)
    return model


def train_mlp(X: np.ndarray, y: np.ndarray, hidden: Tuple[int, ...] = (100,)):
    from sklearn.neural_network import MLPClassifier

    model = MLPClassifier(hidden_layer_sizes=hidden, max_iter=500, random_state=42)
    model.fit(X, y)
    return model


def train_random_forest_regressor(X: np.ndarray, y: np.ndarray, n_estimators: int = 100):
    from sklearn.ensemble import RandomForestRegressor

    model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
    model.fit(X, y)
    return model


def train_gradient_boosting_regressor(X: np.ndarray, y: np.ndarray, n_estimators: int = 100):
    from sklearn.ensemble import GradientBoostingRegressor

    model = GradientBoostingRegressor(n_estimators=n_estimators, random_state=42)
    model.fit(X, y)
    return model


def save_model(model, path: str) -> None:
    import joblib

    joblib.dump(model, path)


def load_model(path: str):
    import joblib

    return joblib.load(path)


def model_summary(model) -> str:
    return str(model)


def feature_importances(model) -> Optional[List[float]]:
    if hasattr(model, "feature_importances_"):
        return model.feature_importances_.tolist()
    return None


def predict(model, X: np.ndarray) -> np.ndarray:
    return model.predict(X)


def predict_proba(model, X: np.ndarray) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)
    return model.predict(X)


def save_predictions(path: str, preds: np.ndarray) -> None:
    np.save(path, preds)


def load_predictions(path: str) -> np.ndarray:
    return np.load(path)


def compute_confusion_matrix(y_true, y_pred):
    from sklearn.metrics import confusion_matrix

    return confusion_matrix(y_true, y_pred).tolist()


def compute_classification_report(y_true, y_pred):
    from sklearn.metrics import classification_report

    return classification_report(y_true, y_pred, output_dict=True)


def compute_roc_auc(y_true, y_prob):
    from sklearn.metrics import roc_auc_score

    return float(roc_auc_score(y_true, y_prob))


def compute_pr_curve(y_true, y_prob):
    from sklearn.metrics import precision_recall_curve

    p, r, t = precision_recall_curve(y_true, y_prob)
    return {"precision": p.tolist(), "recall": r.tolist(), "thresholds": t.tolist()}


def compute_roc_curve(y_true, y_prob):
    from sklearn.metrics import roc_curve

    fpr, tpr, t = roc_curve(y_true, y_prob)
    return {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "thresholds": t.tolist()}


def compute_calibration(y_true, y_prob, n_bins: int = 10):
    from sklearn.calibration import calibration_curve

    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)
    return {"prob_true": prob_true.tolist(), "prob_pred": prob_pred.tolist()}


def compute_learning_curve(model, X, y, cv: int = 5, train_sizes=None):
    from sklearn.model_selection import learning_curve as lc

    if train_sizes is None:
        train_sizes = [0.1, 0.3, 0.5, 0.7, 1.0]
    sizes, train_scores, test_scores = lc(model, X, y, cv=cv, train_sizes=train_sizes, scoring="accuracy")
    return {
        "train_sizes": sizes.tolist(),
        "train_scores": train_scores.tolist(),
        "test_scores": test_scores.tolist(),
    }


def compute_validation_curve(model, X, y, param_name, param_range, cv: int = 5):
    from sklearn.model_selection import validation_curve

    train_scores, test_scores = validation_curve(model, X, y, param_name=param_name, param_range=param_range, cv=cv, scoring="accuracy")
    return {"train_scores": train_scores.tolist(), "test_scores": test_scores.tolist()}


def compute_permutation_importance(model, X, y, n_repeats: int = 5):
    from sklearn.inspection import permutation_importance

    result = permutation_importance(model, X, y, n_repeats=n_repeats, random_state=42)
    return {"importances_mean": result.importances_mean.tolist(), "importances_std": result.importances_std.tolist()}


def compute_partial_dependence(model, X, features):
    from sklearn.inspection import partial_dependence

    result = partial_dependence(model, X, features=features)
    return {"values": result["values"][0].tolist() if "values" in result else [], "average": result["average"][0].tolist() if "average" in result else []}


def compute_shap_values(model, X):
    try:
        import shap

        explainer = shap.Explainer(model, X)
        sv = explainer(X)
        return sv.values.tolist() if hasattr(sv, "values") else []
    except Exception:
        return []


def create_pipeline_steps(steps: List[Tuple[str, Any]]):
    from sklearn.pipeline import Pipeline

    return Pipeline(steps)


def create_column_transformer(transformers: List[Tuple[str, Any, List[str]]]):
    from sklearn.compose import ColumnTransformer

    return ColumnTransformer(transformers)


def create_feature_union(transformers: List[Tuple[str, Any]]):
    from sklearn.pipeline import FeatureUnion

    return FeatureUnion(transformers)


def create_voting_classifier(estimators: List[Tuple[str, Any]], voting: str = "soft"):
    from sklearn.ensemble import VotingClassifier

    return VotingClassifier(estimators=estimators, voting=voting)


def create_stacking_classifier(estimators: List[Tuple[str, Any]], final_estimator=None):
    from sklearn.ensemble import StackingClassifier

    return StackingClassifier(estimators=estimators, final_estimator=final_estimator)


def create_bagging_classifier(estimator, n_estimators: int = 10):
    from sklearn.ensemble import BaggingClassifier

    return BaggingClassifier(estimator=estimator, n_estimators=n_estimators, random_state=42)


def create_ada_boost(estimator, n_estimators: int = 50):
    from sklearn.ensemble import AdaBoostClassifier

    return AdaBoostClassifier(estimator=estimator, n_estimators=n_estimators, random_state=42)


def create_extra_trees(n_estimators: int = 100):
    from sklearn.ensemble import ExtraTreesClassifier

    return ExtraTreesClassifier(n_estimators=n_estimators, random_state=42)


def create_hist_gradient_boosting():
    from sklearn.ensemble import HistGradientBoostingClassifier

    return HistGradientBoostingClassifier(random_state=42)


def create_xgboost(n_estimators: int = 100):
    try:
        import xgboost as xgb

        return xgb.XGBClassifier(n_estimators=n_estimators, random_state=42, use_label_encoder=False, eval_metric="logloss")
    except Exception:
        return None


def create_lightgbm(n_estimators: int = 100):
    try:
        import lightgbm as lgb

        return lgb.LGBMClassifier(n_estimators=n_estimators, random_state=42)
    except Exception:
        return None


def create_catboost(n_estimators: int = 100):
    try:
        import catboost as cb

        return cb.CatBoostClassifier(n_estimators=n_estimators, random_state=42, verbose=0)
    except Exception:
        return None


def get_available_models() -> List[str]:
    models = ["random_forest", "gradient_boosting", "svm", "logistic", "knn", "decision_tree", "naive_bayes", "mlp"]
    try:

        models.append("xgboost")
    except Exception:
        pass
    try:

        models.append("lightgbm")
    except Exception:
        pass
    try:

        models.append("catboost")
    except Exception:
        pass
    return models


def train_model_by_name(name: str, X, y):
    name = name.lower()
    if name == "random_forest":
        return train_random_forest(X, y)
    if name == "gradient_boosting":
        return train_gradient_boosting(X, y)
    if name == "svm":
        return train_svm(X, y)
    if name == "logistic":
        return train_logistic(X, y)
    if name == "knn":
        return train_knn(X, y)
    if name == "decision_tree":
        return train_decision_tree(X, y)
    if name == "naive_bayes":
        return train_naive_bayes(X, y)
    if name == "mlp":
        return train_mlp(X, y)
    if name == "xgboost":
        m = create_xgboost()
        if m is not None:
            m.fit(X, y)
            return m
    if name == "lightgbm":
        m = create_lightgbm()
        if m is not None:
            m.fit(X, y)
            return m
    if name == "catboost":
        m = create_catboost()
        if m is not None:
            m.fit(X, y)
            return m
    raise ValueError(f"Unknown model: {name}")


def benchmark_models(X, y, model_names: Optional[List[str]] = None, cv: int = 5) -> Dict[str, float]:
    if model_names is None:
        model_names = get_available_models()
    results = {}
    for name in model_names:
        try:
            model = train_model_by_name(name, X, y)
            scores = cross_validate_model(model, X, y, cv=cv)
            results[name] = float(np.mean(scores))
        except Exception:
            results[name] = 0.0
    return results


def select_best_model(results: Dict[str, float]) -> str:
    return max(results, key=results.get) if results else ""


def ensemble_top_k(results: Dict[str, float], k: int = 3) -> List[str]:
    return sorted(results, key=results.get, reverse=True)[:k]


def model_report(results: Dict[str, float]) -> str:
    lines = ["Model Benchmark Report", "=" * 40]
    for name, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"{name:25s} {score:.4f}")
    return "\n".join(lines)


def save_benchmark_report(path: str, results: Dict[str, float]) -> None:
    with open(path, "w") as f:
        f.write(model_report(results))


def load_benchmark_report(path: str) -> str:
    with open(path) as f:
        return f.read()


def compare_benchmarks(a: Dict[str, float], b: Dict[str, float]) -> Dict[str, float]:
    out = {}
    for k in set(a) | set(b):
        out[k] = b.get(k, 0.0) - a.get(k, 0.0)
    return out


def summarize_benchmark(results: Dict[str, float]) -> Dict[str, Any]:
    if not results:
        return {}
    scores = list(results.values())
    return {
        "best": max(results, key=results.get),
        "best_score": max(scores),
        "worst": min(results, key=results.get),
        "worst_score": min(scores),
        "mean": float(np.mean(scores)),
        "std": float(np.std(scores)),
        "n_models": len(results),
    }
