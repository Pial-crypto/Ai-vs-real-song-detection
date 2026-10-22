"""Time series analysis utilities."""

from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def moving_average(series: List[float], window: int = 5) -> List[float]:
    arr = np.asarray(series, dtype=float)
    if arr.size == 0:
        return []
    kernel = np.ones(window) / window
    return np.convolve(arr, kernel, mode="same").tolist()


def exponential_moving_average(series: List[float], alpha: float = 0.3) -> List[float]:
    out = []
    prev = None
    for v in series:
        if prev is None:
            prev = v
        else:
            prev = alpha * v + (1 - alpha) * prev
        out.append(prev)
    return out


def double_exponential_smoothing(series: List[float], alpha: float = 0.3, beta: float = 0.1) -> List[float]:
    if not series:
        return []
    level = series[0]
    trend = 0.0
    out = [level]
    for v in series[1:]:
        new_level = alpha * v + (1 - alpha) * (level + trend)
        new_trend = beta * (new_level - level) + (1 - beta) * trend
        level = new_level
        trend = new_trend
        out.append(level)
    return out


def triple_exponential_smoothing(series: List[float], alpha: float = 0.3, beta: float = 0.1, gamma: float = 0.1, period: int = 7) -> List[float]:
    if len(series) < period * 2:
        return list(series)
    # initialize
    level = sum(series[:period]) / period
    trend = (sum(series[period:2 * period]) - sum(series[:period])) / (period * period)
    seasonal = [series[i] - level for i in range(period)]
    out = []
    for i, v in enumerate(series):
        s = seasonal[i % period]
        new_level = alpha * (v - s) + (1 - alpha) * (level + trend)
        new_trend = beta * (new_level - level) + (1 - beta) * trend
        new_seasonal = gamma * (v - new_level) + (1 - gamma) * s
        level = new_level
        trend = new_trend
        seasonal[i % period] = new_seasonal
        out.append(level + trend + new_seasonal)
    return out


def holt_winters(series: List[float], period: int = 7, forecast: int = 0) -> List[float]:
    smoothed = triple_exponential_smoothing(series, period=period)
    if forecast <= 0:
        return smoothed
    # simple forecast: extend trend
    if len(smoothed) < 2:
        return smoothed
    trend = smoothed[-1] - smoothed[-2]
    out = list(smoothed)
    for i in range(forecast):
        out.append(out[-1] + trend)
    return out


def difference(series: List[float], order: int = 1) -> List[float]:
    arr = np.asarray(series, dtype=float)
    for _ in range(order):
        arr = np.diff(arr)
    return arr.tolist()


def seasonal_difference(series: List[float], period: int = 7) -> List[float]:
    arr = np.asarray(series, dtype=float)
    if len(arr) <= period:
        return []
    return (arr[period:] - arr[:-period]).tolist()


def acf(series: List[float], nlags: int = 20) -> List[float]:
    arr = np.asarray(series, dtype=float)
    arr = arr - arr.mean()
    n = len(arr)
    out = []
    denom = np.dot(arr, arr)
    if denom == 0:
        return [0.0] * nlags
    for lag in range(nlags):
        if lag >= n:
            out.append(0.0)
            continue
        out.append(float(np.dot(arr[lag:], arr[:n - lag]) / denom))
    return out


def pacf(series: List[float], nlags: int = 20) -> List[float]:
    # simplified: use acf
    return acf(series, nlags=nlags)


def adf_test(series: List[float]) -> Dict[str, Any]:
    # simple ADF-like: check if differenced series is stationary via variance
    arr = np.asarray(series, dtype=float)
    diff = np.diff(arr)
    mean_diff = np.mean(diff)
    var_diff = np.var(diff)
    # heuristic stationarity score
    return {
        "statistic": float(mean_diff / (np.std(diff) + 1e-9)),
        "p_value": 0.05 if var_diff < np.var(arr) else 0.5,
        "is_stationary": bool(var_diff < np.var(arr)),
        "n_lags": 1,
    }


def kpss_test(series: List[float]) -> Dict[str, Any]:
    arr = np.asarray(series, dtype=float)
    # heuristic
    trend = np.polyfit(np.arange(len(arr)), arr, 1)[0]
    return {
        "statistic": float(abs(trend)),
        "p_value": 0.05 if abs(trend) < 0.01 else 0.5,
        "is_stationary": bool(abs(trend) < 0.01),
    }


def decompose(series: List[float], period: int = 7) -> Dict[str, List[float]]:
    arr = np.asarray(series, dtype=float)
    n = len(arr)
    if n < 2 * period:
        return {"trend": arr.tolist(), "seasonal": [0.0] * n, "residual": [0.0] * n}
    # trend via moving average
    trend = moving_average(series, window=period)
    # seasonal
    detrended = arr - np.asarray(trend)
    seasonal = np.zeros(n)
    for i in range(period):
        seasonal[i::period] = detrended[i::period].mean()
    residual = arr - np.asarray(trend) - seasonal
    return {"trend": trend, "seasonal": seasonal.tolist(), "residual": residual.tolist()}


def detect_seasonality(series: List[float], max_period: int = 12) -> int:
    acf_vals = acf(series, nlags=max_period + 1)
    # find peak
    best = 0
    best_val = 0.0
    for i in range(1, len(acf_vals)):
        if acf_vals[i] > best_val:
            best_val = acf_vals[i]
            best = i
    return best if best > 0 else 1


def detect_trend(series: List[float]) -> str:
    arr = np.asarray(series, dtype=float)
    if len(arr) < 2:
        return "flat"
    slope = np.polyfit(np.arange(len(arr)), arr, 1)[0]
    if slope > 0.01:
        return "up"
    if slope < -0.01:
        return "down"
    return "flat"


def detect_outliers_ts(series: List[float], z_thresh: float = 3.0) -> List[int]:
    arr = np.asarray(series, dtype=float)
    mu = arr.mean()
    sd = arr.std()
    if sd == 0:
        return []
    z = np.abs((arr - mu) / sd)
    return [i for i in range(len(arr)) if z[i] > z_thresh]


def fill_missing_ts(series: List[Optional[float]], method: str = "linear") -> List[float]:
    arr = np.array(series, dtype=float)
    mask = np.isnan(arr)
    if not mask.any():
        return arr.tolist()
    idx = np.arange(len(arr))
    valid = ~mask
    if method == "linear":
        arr[mask] = np.interp(idx[mask], idx[valid], arr[valid])
    elif method == "forward":
        last = None
        for i in range(len(arr)):
            if not mask[i]:
                last = arr[i]
            elif last is not None:
                arr[i] = last
    elif method == "backward":
        last = None
        for i in range(len(arr) - 1, -1, -1):
            if not mask[i]:
                last = arr[i]
            elif last is not None:
                arr[i] = last
    elif method == "mean":
        arr[mask] = np.nanmean(arr)
    return arr.tolist()


def interpolate(series: List[float], factor: int = 2) -> List[float]:
    arr = np.asarray(series, dtype=float)
    x = np.arange(len(arr))
    x_new = np.linspace(0, len(arr) - 1, len(arr) * factor)
    return np.interp(x_new, x, arr).tolist()


def downsample(series: List[float], factor: int = 2) -> List[float]:
    arr = np.asarray(series, dtype=float)
    return arr[::factor].tolist()


def upsample(series: List[float], factor: int = 2) -> List[float]:
    return interpolate(series, factor=factor)


def resample_ts(series: List[float], target_len: int) -> List[float]:
    arr = np.asarray(series, dtype=float)
    x = np.arange(len(arr))
    x_new = np.linspace(0, len(arr) - 1, target_len)
    return np.interp(x_new, x, arr).tolist()


def normalize_ts(series: List[float], method: str = "minmax") -> List[float]:
    arr = np.asarray(series, dtype=float)
    if method == "minmax":
        mn, mx = arr.min(), arr.max()
        if mx - mn == 0:
            return [0.0] * len(series)
        return ((arr - mn) / (mx - mn)).tolist()
    if method == "zscore":
        mu, sd = arr.mean(), arr.std()
        if sd == 0:
            sd = 1.0
        return ((arr - mu) / sd).tolist()
    if method == "robust":
        med = np.median(arr)
        q75, q25 = np.percentile(arr, [75, 25])
        iqr = q75 - q25
        if iqr == 0:
            iqr = 1.0
        return ((arr - med) / iqr).tolist()
    return arr.tolist()


def denormalize_ts(series: List[float], orig_min: float, orig_max: float) -> List[float]:
    arr = np.asarray(series, dtype=float)
    return (arr * (orig_max - orig_min) + orig_min).tolist()


def sliding_window(series: List[float], window: int, step: int = 1) -> List[List[float]]:
    out = []
    for i in range(0, len(series) - window + 1, step):
        out.append(series[i:i + window])
    return out


def rolling_stats(series: List[float], window: int) -> Dict[str, List[float]]:
    arr = np.asarray(series, dtype=float)
    n = len(arr)
    means = []
    stds = []
    mins = []
    maxs = []
    for i in range(n):
        start = max(0, i - window + 1)
        chunk = arr[start:i + 1]
        means.append(float(chunk.mean()))
        stds.append(float(chunk.std()))
        mins.append(float(chunk.min()))
        maxs.append(float(chunk.max()))
    return {"mean": means, "std": stds, "min": mins, "max": maxs}


def cumulative_stats(series: List[float]) -> Dict[str, List[float]]:
    arr = np.asarray(series, dtype=float)
    return {
        "cumsum": np.cumsum(arr).tolist(),
        "cumprod": np.cumprod(arr).tolist(),
        "cummax": np.maximum.accumulate(arr).tolist(),
        "cummin": np.minimum.accumulate(arr).tolist(),
    }


def change_points(series: List[float], threshold: float = 2.0) -> List[int]:
    arr = np.asarray(series, dtype=float)
    diff = np.abs(np.diff(arr))
    mu = diff.mean()
    sd = diff.std()
    if sd == 0:
        return []
    z = (diff - mu) / sd
    return [i + 1 for i in range(len(diff)) if z[i] > threshold]


def peaks(series: List[float], distance: int = 1) -> List[int]:
    arr = np.asarray(series, dtype=float)
    peaks_idx = []
    for i in range(1, len(arr) - 1):
        if arr[i] > arr[i - 1] and arr[i] > arr[i + 1]:
            if not peaks_idx or i - peaks_idx[-1] >= distance:
                peaks_idx.append(i)
    return peaks_idx


def valleys(series: List[float], distance: int = 1) -> List[int]:
    np.asarray(series, dtype=float)
    return peaks([-x for x in series], distance=distance)


def zero_crossings(series: List[float]) -> List[int]:
    arr = np.asarray(series, dtype=float)
    signs = np.sign(arr)
    # handle zeros
    signs[signs == 0] = 1
    crossings = np.where(np.diff(signs) != 0)[0]
    return crossings.tolist()


def autocorrelation_plot(series: List[float], nlags: int = 20) -> List[float]:
    return acf(series, nlags=nlags)


def partial_autocorrelation(series: List[float], nlags: int = 20) -> List[float]:
    return pacf(series, nlags=nlags)


def fourier_transform(series: List[float]) -> Tuple[List[float], List[float]]:
    arr = np.asarray(series, dtype=float)
    fft = np.fft.rfft(arr)
    freqs = np.fft.rfftfreq(len(arr))
    return freqs.tolist(), np.abs(fft).tolist()


def inverse_fourier_transform(freqs: List[float], mags: List[float]) -> List[float]:
    n = len(mags)
    # reconstruct
    arr = np.array(mags, dtype=complex)
    return np.fft.irfft(arr, n=n * 2 - 1).tolist()[:n]


def power_spectral_density(series: List[float]) -> Tuple[List[float], List[float]]:
    arr = np.asarray(series, dtype=float)
    freqs, psd = None, None
    try:
        from scipy import signal

        freqs, psd = signal.welch(arr)
    except Exception:
        fft = np.fft.rfft(arr)
        freqs = np.fft.rfftfreq(len(arr))
        psd = np.abs(fft) ** 2
    return freqs.tolist(), psd.tolist()


def spectrogram(series: List[float], nperseg: int = 256) -> Tuple[List, List, List]:
    arr = np.asarray(series, dtype=float)
    try:
        from scipy import signal

        f, t, Sxx = signal.spectrogram(arr, nperseg=nperseg)
        return f.tolist(), t.tolist(), Sxx.tolist()
    except Exception:
        return [], [], []


def stft(series: List[float], n_fft: int = 256, hop_length: int = 128) -> np.ndarray:
    arr = np.asarray(series, dtype=float)
    # simple STFT
    frames = []
    for i in range(0, len(arr) - n_fft + 1, hop_length):
        frame = arr[i:i + n_fft]
        frames.append(np.fft.rfft(frame))
    if not frames:
        return np.array([])
    return np.array(frames).T


def istft(stft_matrix: np.ndarray, hop_length: int = 128) -> List[float]:
    if stft_matrix.size == 0:
        return []
    # inverse
    frames = stft_matrix.T
    n = len(frames) * hop_length
    out = np.zeros(n)
    for i, frame in enumerate(frames):
        out[i * hop_length:i * hop_length + len(frame) * 2 - 1] += np.fft.irfft(frame)
    return out.tolist()


def arima_forecast(series: List[float], order: Tuple[int, int, int] = (1, 1, 1), steps: int = 5) -> List[float]:
    # simple: use last value + trend
    arr = np.asarray(series, dtype=float)
    if len(arr) < 2:
        return [float(arr[-1])] * steps if len(arr) else [0.0] * steps
    trend = arr[-1] - arr[-2]
    out = []
    last = arr[-1]
    for i in range(steps):
        last = last + trend
        out.append(float(last))
    return out


def sarima_forecast(series: List[float], seasonal_period: int = 7, steps: int = 5) -> List[float]:
    arr = np.asarray(series, dtype=float)
    if len(arr) < seasonal_period:
        return [float(arr[-1])] * steps if len(arr) else [0.0] * steps
    # seasonal naive: use value from last season
    out = []
    for i in range(steps):
        idx = len(arr) - seasonal_period + (i % seasonal_period)
        if idx < 0:
            idx = 0
        out.append(float(arr[idx]))
    return out


def prophet_like_forecast(series: List[float], steps: int = 5) -> List[float]:
    # linear trend + seasonal
    arr = np.asarray(series, dtype=float)
    if len(arr) < 2:
        return [float(arr[-1] if len(arr) else 0.0)] * steps
    t = np.arange(len(arr))
    slope, intercept = np.polyfit(t, arr, 1)
    out = []
    for i in range(steps):
        out.append(float(intercept + slope * (len(arr) + i)))
    return out


def exponential_smoothing_forecast(series: List[float], alpha: float = 0.3, steps: int = 5) -> List[float]:
    smoothed = exponential_moving_average(series, alpha=alpha)
    last = smoothed[-1] if smoothed else 0.0
    return [float(last)] * steps


def theta_forecast(series: List[float], steps: int = 5) -> List[float]:
    return exponential_smoothing_forecast(series, steps=steps)


def naive_forecast(series: List[float], steps: int = 5) -> List[float]:
    if not series:
        return [0.0] * steps
    return [float(series[-1])] * steps


def seasonal_naive_forecast(series: List[float], period: int = 7, steps: int = 5) -> List[float]:
    if not series:
        return [0.0] * steps
    out = []
    for i in range(steps):
        idx = len(series) - period + (i % period)
        if idx < 0:
            idx = len(series) - 1
        out.append(float(series[idx]))
    return out


def drift_forecast(series: List[float], steps: int = 5) -> List[float]:
    arr = np.asarray(series, dtype=float)
    if len(arr) < 2:
        return [float(arr[-1] if len(arr) else 0.0)] * steps
    drift = (arr[-1] - arr[0]) / (len(arr) - 1)
    out = []
    for i in range(1, steps + 1):
        out.append(float(arr[-1] + drift * i))
    return out


def mean_forecast(series: List[float], steps: int = 5) -> List[float]:
    if not series:
        return [0.0] * steps
    return [float(np.mean(series))] * steps


def median_forecast(series: List[float], steps: int = 5) -> List[float]:
    if not series:
        return [0.0] * steps
    return [float(np.median(series))] * steps


def random_walk_forecast(series: List[float], steps: int = 5, seed: int = 42) -> List[float]:
    rng = np.random.default_rng(seed)
    arr = np.asarray(series, dtype=float)
    if len(arr) < 2:
        return [float(arr[-1] if len(arr) else 0.0)] * steps
    std = np.std(np.diff(arr))
    last = arr[-1]
    out = []
    for _ in range(steps):
        last = last + rng.normal(0, std)
        out.append(float(last))
    return out


def monte_carlo_forecast(series: List[float], steps: int = 5, n_sim: int = 100, seed: int = 42) -> List[float]:
    rng = np.random.default_rng(seed)
    arr = np.asarray(series, dtype=float)
    if len(arr) < 2:
        return [float(arr[-1] if len(arr) else 0.0)] * steps
    std = np.std(np.diff(arr))
    sims = np.zeros((n_sim, steps))
    for i in range(n_sim):
        last = arr[-1]
        for j in range(steps):
            last = last + rng.normal(0, std)
            sims[i, j] = last
    return sims.mean(axis=0).tolist()


def forecast_intervals(series: List[float], steps: int = 5, alpha: float = 0.05) -> Dict[str, List[float]]:
    fc = naive_forecast(series, steps=steps)
    arr = np.asarray(series, dtype=float)
    std = np.std(arr) if arr.size else 1.0
    from scipy.stats import norm

    z = float(norm.ppf(1 - alpha / 2))
    lower = [f - z * std for f in fc]
    upper = [f + z * std for f in fc]
    return {"forecast": fc, "lower": lower, "upper": upper}


def evaluate_forecast(actual: List[float], predicted: List[float]) -> Dict[str, float]:

    n = min(len(actual), len(predicted))
    a = np.asarray(actual[:n], dtype=float)
    p = np.asarray(predicted[:n], dtype=float)
    mae = float(np.mean(np.abs(a - p)))
    rmse = float(np.sqrt(np.mean((a - p) ** 2)))
    mape = float(np.mean(np.abs((a - p) / np.where(a == 0, 1, a))) * 100)
    smape_val = float(np.mean(2 * np.abs(a - p) / (np.abs(a) + np.abs(p) + 1e-9)) * 100)
    return {"mae": mae, "rmse": rmse, "mape": mape, "smape": smape_val}


def mase(actual: List[float], predicted: List[float], train: List[float]) -> float:
    n = min(len(actual), len(predicted))
    a = np.asarray(actual[:n], dtype=float)
    p = np.asarray(predicted[:n], dtype=float)
    mae = np.mean(np.abs(a - p))
    # naive in-sample MAE
    tr = np.asarray(train, dtype=float)
    naive_mae = np.mean(np.abs(tr[1:] - tr[:-1])) if len(tr) > 1 else 1.0
    if naive_mae == 0:
        naive_mae = 1.0
    return float(mae / naive_mae)


def smape_metric(actual: List[float], predicted: List[float]) -> float:
    n = min(len(actual), len(predicted))
    a = np.asarray(actual[:n], dtype=float)
    p = np.asarray(predicted[:n], dtype=float)
    return float(np.mean(2 * np.abs(a - p) / (np.abs(a) + np.abs(p) + 1e-9)) * 100)


def mape_metric(actual: List[float], predicted: List[float]) -> float:
    n = min(len(actual), len(predicted))
    a = np.asarray(actual[:n], dtype=float)
    p = np.asarray(predicted[:n], dtype=float)
    mask = a != 0
    if not mask.any():
        return 0.0
    return float(np.mean(np.abs((a[mask] - p[mask]) / a[mask])) * 100)


def rmse_metric(actual: List[float], predicted: List[float]) -> float:
    n = min(len(actual), len(predicted))
    a = np.asarray(actual[:n], dtype=float)
    p = np.asarray(predicted[:n], dtype=float)
    return float(np.sqrt(np.mean((a - p) ** 2)))


def mae_metric(actual: List[float], predicted: List[float]) -> float:
    n = min(len(actual), len(predicted))
    a = np.asarray(actual[:n], dtype=float)
    p = np.asarray(predicted[:n], dtype=float)
    return float(np.mean(np.abs(a - p)))


def r2_metric(actual: List[float], predicted: List[float]) -> float:
    n = min(len(actual), len(predicted))
    a = np.asarray(actual[:n], dtype=float)
    p = np.asarray(predicted[:n], dtype=float)
    ss_res = np.sum((a - p) ** 2)
    ss_tot = np.sum((a - a.mean()) ** 2)
    if ss_tot == 0:
        return 0.0
    return float(1 - ss_res / ss_tot)


def theil_u(actual: List[float], predicted: List[float]) -> float:
    n = min(len(actual), len(predicted))
    a = np.asarray(actual[:n], dtype=float)
    p = np.asarray(predicted[:n], dtype=float)
    num = np.sqrt(np.mean((a - p) ** 2))
    den = np.sqrt(np.mean(a ** 2)) + np.sqrt(np.mean(p ** 2))
    if den == 0:
        return 0.0
    return float(num / den)


def track_signal_noise(series: List[float]) -> Dict[str, float]:
    arr = np.asarray(series, dtype=float)
    if arr.size < 2:
        return {"signal": 0.0, "noise": 0.0, "snr": 0.0}
    diff = np.diff(arr)
    signal = float(np.std(arr))
    noise = float(np.std(diff))
    snr = signal / noise if noise > 0 else float("inf")
    return {"signal": signal, "noise": noise, "snr": snr}


def detrend(series: List[float], method: str = "linear") -> List[float]:
    arr = np.asarray(series, dtype=float)
    if method == "linear":
        t = np.arange(len(arr))
        slope, intercept = np.polyfit(t, arr, 1)
        return (arr - (slope * t + intercept)).tolist()
    if method == "constant":
        return (arr - arr.mean()).tolist()
    return arr.tolist()


def deseasonalize(series: List[float], period: int = 7) -> List[float]:
    arr = np.asarray(series, dtype=float)
    if len(arr) < period:
        return arr.tolist()
    seasonal = np.zeros(len(arr))
    for i in range(period):
        seasonal[i::period] = arr[i::period].mean()
    return (arr - seasonal).tolist()


def remove_trend(series: List[float]) -> List[float]:
    return detrend(series, method="linear")


def remove_seasonality(series: List[float], period: int = 7) -> List[float]:
    return deseasonalize(series, period=period)


def stationarity_check(series: List[float]) -> Dict[str, Any]:
    return adf_test(series)


def make_stationary(series: List[float], max_diff: int = 2) -> Tuple[List[float], int]:
    arr = np.asarray(series, dtype=float)
    d = 0
    cur = arr.copy()
    for _ in range(max_diff):
        if adf_test(cur.tolist())["is_stationary"]:
            break
        cur = np.diff(cur)
        d += 1
    return cur.tolist(), d


def boxcox_transform(series: List[float], lmbda: Optional[float] = None) -> Tuple[List[float], float]:
    from scipy.stats import boxcox

    arr = np.asarray(series, dtype=float)
    # ensure positive
    mn = arr.min()
    if mn <= 0:
        arr = arr - mn + 1
    transformed, lmbda = boxcox(arr, lmbda=lmbda)
    return transformed.tolist(), float(lmbda)


def yeo_johnson_transform(series: List[float], lmbda: Optional[float] = None) -> Tuple[List[float], float]:
    from sklearn.preprocessing import PowerTransformer

    pt = PowerTransformer(method="yeo-johnson", standardize=False)
    arr = np.asarray(series, dtype=float).reshape(-1, 1)
    out = pt.fit_transform(arr).ravel()
    return out.tolist(), float(pt.lambdas_[0])


def log_transform(series: List[float]) -> List[float]:
    arr = np.asarray(series, dtype=float)
    # shift to positive
    mn = arr.min()
    if mn <= 0:
        arr = arr - mn + 1
    return np.log(arr).tolist()


def sqrt_transform(series: List[float]) -> List[float]:
    arr = np.asarray(series, dtype=float)
    mn = arr.min()
    if mn < 0:
        arr = arr - mn
    return np.sqrt(arr).tolist()


def reciprocal_transform(series: List[float]) -> List[float]:
    arr = np.asarray(series, dtype=float)
    # avoid zeros
    arr = np.where(arr == 0, 1e-9, arr)
    return (1.0 / arr).tolist()


def difference_transform(series: List[float], order: int = 1) -> List[float]:
    return difference(series, order=order)


def seasonal_decompose(series: List[float], period: int = 7) -> Dict[str, List[float]]:
    return decompose(series, period=period)


def trend_decompose(series: List[float]) -> List[float]:
    res = decompose(series, period=max(2, len(series) // 4))
    return res["trend"]


def seasonal_decompose_extract(series: List[float], period: int = 7) -> List[float]:
    res = decompose(series, period=period)
    return res["seasonal"]


def residual_decompose(series: List[float], period: int = 7) -> List[float]:
    res = decompose(series, period=period)
    return res["residual"]


def create_time_series_features(series: List[float], lags: int = 5) -> List[List[float]]:
    arr = np.asarray(series, dtype=float)
    out = []
    for i in range(lags, len(arr)):
        row = [arr[i - j - 1] for j in range(lags)] + [arr[i]]
        out.append(row)
    return out


def create_rolling_features(series: List[float], windows: List[int] = [3, 5, 7]) -> List[Dict[str, float]]:
    arr = np.asarray(series, dtype=float)
    out = []
    for i in range(len(arr)):
        feats = {}
        for w in windows:
            start = max(0, i - w + 1)
            chunk = arr[start:i + 1]
            feats[f"mean_{w}"] = float(chunk.mean())
            feats[f"std_{w}"] = float(chunk.std())
            feats[f"min_{w}"] = float(chunk.min())
            feats[f"max_{w}"] = float(chunk.max())
        out.append(feats)
    return out


def create_lag_features(series: List[float], lags: int = 5) -> List[Dict[str, float]]:
    arr = np.asarray(series, dtype=float)
    out = []
    for i in range(len(arr)):
        feats = {}
        for lag in range(1, lags + 1):
            idx = i - lag
            feats[f"lag_{lag}"] = float(arr[idx]) if idx >= 0 else 0.0
        out.append(feats)
    return out


def create_date_features(dates: List[str]) -> List[Dict[str, int]]:
    from datetime import datetime

    out = []
    for d in dates:
        try:
            dt = datetime.fromisoformat(d)
        except Exception:
            dt = datetime.now()
        out.append({
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "weekday": dt.weekday(),
            "quarter": (dt.month - 1) // 3 + 1,
            "is_weekend": int(dt.weekday() >= 5),
        })
    return out


def create_cyclical_features(values: List[int], period: int) -> List[Tuple[float, float]]:
    out = []
    for v in values:
        angle = 2 * math.pi * v / period
        out.append((math.sin(angle), math.cos(angle)))
    return out


def create_interaction_features(features: List[List[float]]) -> List[List[float]]:
    arr = np.asarray(features, dtype=float)
    n = arr.shape[1]
    out = arr.tolist()
    for i in range(n):
        for j in range(i + 1, n):
            out = [row + [row[i] * row[j]] for row in out]
    return out


def create_polynomial_features(features: List[List[float]], degree: int = 2) -> List[List[float]]:
    from sklearn.preprocessing import PolynomialFeatures

    pf = PolynomialFeatures(degree=degree, include_bias=False)
    return pf.fit_transform(np.asarray(features, dtype=float)).tolist()


def create_binned_features(values: List[float], bins: int = 5) -> List[int]:
    arr = np.asarray(values, dtype=float)
    edges = np.percentile(arr, np.linspace(0, 100, bins + 1))
    return np.digitize(arr, edges[1:-1]).tolist()


def create_quantile_features(values: List[float], q: List[float] = (0.25, 0.5, 0.75)) -> List[float]:
    arr = np.asarray(values, dtype=float)
    return [float(np.percentile(arr, qi * 100)) for qi in q]


def create_rank_features(values: List[float]) -> List[int]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0] * len(values)
    for rank, idx in enumerate(order):
        ranks[idx] = rank
    return ranks


def create_density_features(values: List[float], bandwidth: float = 1.0) -> List[float]:
    from scipy.stats import gaussian_kde

    arr = np.asarray(values, dtype=float)
    if arr.size < 2:
        return [0.0] * len(values)
    try:
        kde = gaussian_kde(arr, bw_method=bandwidth)
        return kde(arr).tolist()
    except Exception:
        return [0.0] * len(values)


def create_outlier_features(values: List[float], z_thresh: float = 3.0) -> List[int]:
    arr = np.asarray(values, dtype=float)
    mu = arr.mean()
    sd = arr.std()
    if sd == 0:
        return [0] * len(values)
    z = np.abs((arr - mu) / sd)
    return [1 if zi > z_thresh else 0 for zi in z]


def create_missing_indicators(values: List[Optional[float]]) -> List[int]:
    return [1 if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) else 0 for v in values]


def create_time_features(timestamps: List[int]) -> List[Dict[str, int]]:
    from datetime import datetime

    out = []
    for ts in timestamps:
        dt = datetime.fromtimestamp(ts)
        out.append({
            "hour": dt.hour,
            "minute": dt.minute,
            "day_of_week": dt.weekday(),
            "day_of_month": dt.day,
            "month": dt.month,
            "year": dt.year,
            "is_weekend": int(dt.weekday() >= 5),
        })
    return out


def create_frequency_features(series: List[float]) -> Dict[str, float]:
    freqs, psd = power_spectral_density(series)
    if not freqs:
        return {}
    idx = int(np.argmax(psd))
    return {
        "dominant_freq": float(freqs[idx]),
        "dominant_power": float(psd[idx]),
        "spectral_centroid": float(np.sum(np.array(freqs) * np.array(psd)) / (np.sum(psd) + 1e-9)),
        "spectral_bandwidth": float(np.sqrt(np.sum(((np.array(freqs) - np.sum(np.array(freqs) * np.array(psd)) / (np.sum(psd) + 1e-9)) ** 2) * np.array(psd)) / (np.sum(psd) + 1e-9))),
    }


def create_entropy_features(series: List[float]) -> Dict[str, float]:
    arr = np.asarray(series, dtype=float)
    # sample entropy
    def _sampen(data, m=2, r=0.2):
        n = len(data)
        if n < m + 1:
            return 0.0
        std = np.std(data)
        if std == 0:
            return 0.0
        r *= std
        # count matches
        def count_matches(m):
            count = 0
            for i in range(n - m):
                for j in range(i + 1, n - m):
                    if np.max(np.abs(data[i:i + m] - data[j:j + m])) <= r:
                        count += 1
            return count
        a = count_matches(m + 1)
        b = count_matches(m)
        if b == 0:
            return 0.0
        return -math.log(a / b) if a > 0 else 0.0
    return {
        "sample_entropy": _sampen(arr.tolist()),
        "approximate_entropy": _sampen(arr.tolist(), m=1),
        "spectral_entropy": 0.0,
    }


def create_complexity_features(series: List[float]) -> Dict[str, float]:
    arr = np.asarray(series, dtype=float)
    # Higuchi fractal dimension
    def higuchi_fd(data, kmax=10):
        n = len(data)
        lk = []
        for k in range(1, kmax + 1):
            lmk = []
            for m in range(k):
                # length
                idx = np.arange(m, n, k)
                if len(idx) < 2:
                    continue
                diffs = np.abs(np.diff(data[idx]))
                lm = (np.sum(diffs) * (n - 1)) / (len(idx) * k)
                lmk.append(lm)
            if lmk:
                lk.append(np.mean(lmk))
        if len(lk) < 2:
            return 1.0
        # slope of log(L(k)) vs log(1/k)
        x = np.log(1.0 / np.arange(1, len(lk) + 1))
        y = np.log(lk)
        return float(np.polyfit(x, y, 1)[0])
    return {
        "higuchi_fd": higuchi_fd(arr.tolist()),
        "hurst": 0.5,  # placeholder
        "dfa": 0.5,
    }


def create_statistical_features(series: List[float]) -> Dict[str, float]:
    arr = np.asarray(series, dtype=float)
    if arr.size == 0:
        return {}
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "var": float(arr.var()),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "median": float(np.median(arr)),
        "skew": float(np.mean(((arr - arr.mean()) / (arr.std() + 1e-9)) ** 3)),
        "kurtosis": float(np.mean(((arr - arr.mean()) / (arr.std() + 1e-9)) ** 4) - 3),
        "q25": float(np.percentile(arr, 25)),
        "q75": float(np.percentile(arr, 75)),
        "iqr": float(np.percentile(arr, 75) - np.percentile(arr, 25)),
        "range": float(arr.max() - arr.min()),
        "sum": float(arr.sum()),
        "abs_mean": float(np.mean(np.abs(arr))),
        "rms": float(np.sqrt(np.mean(arr ** 2))),
    }


def create_all_features(series: List[float]) -> Dict[str, Any]:
    return {
        "statistical": create_statistical_features(series),
        "rolling": create_rolling_features(series, windows=[3, 5, 7])[-1] if series else {},
        "entropy": create_entropy_features(series),
        "complexity": create_complexity_features(series),
        "frequency": create_frequency_features(series),
    }


def flatten_features(features: Dict[str, Any]) -> List[float]:
    out = []
    for v in features.values():
        if isinstance(v, dict):
            out.extend(flatten_features(v))
        elif isinstance(v, (list, tuple)):
            out.extend([float(x) for x in v])
        elif isinstance(v, (int, float, np.integer, np.floating)):
            out.append(float(v))
    return out


def feature_vector(series: List[float]) -> List[float]:
    return flatten_features(create_all_features(series))


def batch_feature_vectors(series_list: List[List[float]]) -> List[List[float]]:
    return [feature_vector(s) for s in series_list]


def save_feature_vectors(path: str, vectors: List[List[float]]) -> None:
    import json

    with open(path, "w") as f:
        json.dump(vectors, f)


def load_feature_vectors(path: str) -> List[List[float]]:
    import json

    with open(path) as f:
        return json.load(f)


def normalize_feature_vectors(vectors: List[List[float]]) -> List[List[float]]:
    arr = np.asarray(vectors, dtype=float)
    if arr.size == 0:
        return vectors
    mu = arr.mean(axis=0)
    sd = arr.std(axis=0)
    sd = np.where(sd == 0, 1.0, sd)
    return ((arr - mu) / sd).tolist()


def scale_feature_vectors(vectors: List[List[float]], method: str = "standard") -> List[List[float]]:
    arr = np.asarray(vectors, dtype=float)
    if method == "minmax":
        mn = arr.min(axis=0)
        mx = arr.max(axis=0)
        rng = np.where(mx - mn == 0, 1.0, mx - mn)
        return ((arr - mn) / rng).tolist()
    mu = arr.mean(axis=0)
    sd = arr.std(axis=0)
    sd = np.where(sd == 0, 1.0, sd)
    return ((arr - mu) / sd).tolist()


def reduce_feature_vectors(vectors: List[List[float]], n_components: int = 2) -> List[List[float]]:
    from sklearn.decomposition import PCA

    arr = np.asarray(vectors, dtype=float)
    if arr.shape[0] < 2:
        return vectors
    pca = PCA(n_components=min(n_components, arr.shape[1]))
    return pca.fit_transform(arr).tolist()


def cluster_feature_vectors(vectors: List[List[float]], n_clusters: int = 3) -> List[int]:
    from sklearn.cluster import KMeans

    arr = np.asarray(vectors, dtype=float)
    km = KMeans(n_clusters=min(n_clusters, arr.shape[0]), random_state=42, n_init=10)
    return km.fit_predict(arr).tolist()


def detect_anomalies(vectors: List[List[float]], contamination: float = 0.1) -> List[int]:
    from sklearn.ensemble import IsolationForest

    arr = np.asarray(vectors, dtype=float)
    iso = IsolationForest(contamination=contamination, random_state=42)
    return iso.fit_predict(arr).tolist()


def compute_similarity_matrix(vectors: List[List[float]]) -> List[List[float]]:
    arr = np.asarray(vectors, dtype=float)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    normed = arr / norms
    return (normed @ normed.T).tolist()


def find_nearest_neighbors(vectors: List[List[float]], query: List[float], k: int = 5) -> List[int]:
    arr = np.asarray(vectors, dtype=float)
    q = np.asarray(query, dtype=float)
    dists = np.linalg.norm(arr - q, axis=1)
    return np.argsort(dists)[:k].tolist()


def compute_distance_matrix(vectors: List[List[float]], metric: str = "euclidean") -> List[List[float]]:
    arr = np.asarray(vectors, dtype=float)
    n = arr.shape[0]
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if metric == "euclidean":
                out[i][j] = float(np.linalg.norm(arr[i] - arr[j]))
            elif metric == "manhattan":
                out[i][j] = float(np.sum(np.abs(arr[i] - arr[j])))
            elif metric == "cosine":
                denom = np.linalg.norm(arr[i]) * np.linalg.norm(arr[j])
                out[i][j] = float(1 - np.dot(arr[i], arr[j]) / denom) if denom > 0 else 0.0
    return out


def create_time_series_dataset(series: List[float], window: int = 5, horizon: int = 1) -> Tuple[List[List[float]], List[float]]:
    X, y = [], []
    for i in range(window, len(series) - horizon + 1):
        X.append(series[i - window:i])
        y.append(series[i + horizon - 1])
    return X, y


def train_time_series_model(X, y, model_type: str = "linear"):
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import LinearRegression

    if model_type == "linear":
        m = LinearRegression()
    elif model_type == "rf":
        m = RandomForestRegressor(random_state=42)
    elif model_type == "gb":
        m = GradientBoostingRegressor(random_state=42)
    else:
        m = LinearRegression()
    m.fit(X, y)
    return m


def forecast_time_series(model, last_window: List[float], steps: int = 5) -> List[float]:
    window = list(last_window)
    out = []
    for _ in range(steps):
        pred = model.predict([window])[0]
        out.append(float(pred))
        window = window[1:] + [pred]
    return out


def evaluate_time_series(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    return evaluate_forecast(actual, predicted)


def backtest_time_series(series: List[float], window: int = 5, horizon: int = 1, model_type: str = "linear", test_size: float = 0.2):
    X, y = create_time_series_dataset(series, window=window, horizon=horizon)
    n_test = int(len(X) * test_size)
    Xtr, Xte = X[:-n_test], X[-n_test:]
    ytr, yte = y[:-n_test], y[-n_test:]
    model = train_time_series_model(Xtr, ytr, model_type=model_type)
    preds = model.predict(Xte)
    metrics = evaluate_time_series(yte, preds.tolist())
    return {"model": model, "metrics": metrics, "predictions": preds.tolist(), "actual": yte}


def cross_validate_time_series(series: List[float], window: int = 5, horizon: int = 1, k: int = 5, model_type: str = "linear") -> List[float]:
    X, y = create_time_series_dataset(series, window=window, horizon=horizon)
    from sklearn.model_selection import TimeSeriesSplit

    tscv = TimeSeriesSplit(n_splits=k)
    scores = []
    for train_idx, test_idx in tscv.split(X):
        Xtr = [X[i] for i in train_idx]
        ytr = [y[i] for i in train_idx]
        Xte = [X[i] for i in test_idx]
        yte = [y[i] for i in test_idx]
        model = train_time_series_model(Xtr, ytr, model_type=model_type)
        preds = model.predict(Xte)
        scores.append(float(np.mean(np.abs(np.asarray(yte) - preds))))
    return scores


def grid_search_time_series(series: List[float], window: int = 5, param_grid: Optional[Dict[str, List]] = None) -> Dict[str, Any]:
    if param_grid is None:
        param_grid = {"model_type": ["linear", "rf"]}
    best = None
    best_score = float("inf")
    for mt in param_grid.get("model_type", ["linear"]):
        scores = cross_validate_time_series(series, window=window, model_type=mt)
        mean_score = float(np.mean(scores))
        if mean_score < best_score:
            best_score = mean_score
            best = mt
    return {"best_model_type": best, "best_score": best_score}


def ensemble_time_series_forecast(series: List[float], steps: int = 5, models: Optional[List[str]] = None) -> List[float]:
    if models is None:
        models = ["naive", "mean", "drift"]
    forecasts = []
    for m in models:
        if m == "naive":
            forecasts.append(naive_forecast(series, steps=steps))
        elif m == "mean":
            forecasts.append(mean_forecast(series, steps=steps))
        elif m == "drift":
            forecasts.append(drift_forecast(series, steps=steps))
        elif m == "seasonal_naive":
            forecasts.append(seasonal_naive_forecast(series, steps=steps))
    if not forecasts:
        return [0.0] * steps
    arr = np.asarray(forecasts, dtype=float)
    return arr.mean(axis=0).tolist()


def weighted_ensemble_forecast(series: List[float], steps: int = 5, weights: Optional[List[float]] = None) -> List[float]:
    forecasts = [
        naive_forecast(series, steps=steps),
        mean_forecast(series, steps=steps),
        drift_forecast(series, steps=steps),
    ]
    if weights is None:
        weights = [1.0 / len(forecasts)] * len(forecasts)
    arr = np.asarray(forecasts, dtype=float)
    w = np.asarray(weights, dtype=float)
    return (arr.T @ w).tolist()


def stacking_forecast(series: List[float], steps: int = 5) -> List[float]:
    return ensemble_time_series_forecast(series, steps=steps)


def blending_forecast(series: List[float], steps: int = 5) -> List[float]:
    return weighted_ensemble_forecast(series, steps=steps)


def create_forecast_report(series: List[float], steps: int = 5) -> Dict[str, Any]:
    forecasts = {
        "naive": naive_forecast(series, steps=steps),
        "mean": mean_forecast(series, steps=steps),
        "drift": drift_forecast(series, steps=steps),
        "seasonal_naive": seasonal_naive_forecast(series, steps=steps),
        "exponential_smoothing": exponential_smoothing_forecast(series, steps=steps),
        "monte_carlo": monte_carlo_forecast(series, steps=steps),
    }
    return {
        "series_length": len(series),
        "steps": steps,
        "forecasts": forecasts,
        "ensemble": ensemble_time_series_forecast(series, steps=steps),
    }


def save_forecast_report(path: str, report: Dict[str, Any]) -> None:
    with open(path, "w") as f:
        json.dump(report, f, default=str, indent=2)


def load_forecast_report(path: str) -> Dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def format_forecast_report(report: Dict[str, Any]) -> str:
    lines = ["Forecast Report", "=" * 40]
    lines.append(f"Series length: {report.get('series_length')}")
    lines.append(f"Steps: {report.get('steps')}")
    for name, fc in report.get("forecasts", {}).items():
        lines.append(f"{name}: {fc}")
    lines.append(f"Ensemble: {report.get('ensemble')}")
    return "\n".join(lines)


def print_forecast_report(report: Dict[str, Any]) -> None:
    print(format_forecast_report(report))


def export_forecast_csv(path: str, report: Dict[str, Any]) -> None:
    import csv

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["model", "step", "value"])
        for name, fc in report.get("forecasts", {}).items():
            for i, v in enumerate(fc):
                writer.writerow([name, i, v])


def import_forecast_csv(path: str) -> Dict[str, Any]:
    import csv

    forecasts = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            forecasts.setdefault(row["model"], []).append(float(row["value"]))
    return {"forecasts": forecasts}


def validate_series(series: List[float]) -> bool:
    if not series:
        return False
    arr = np.asarray(series, dtype=float)
    if not np.all(np.isfinite(arr)):
        return False
    return True


def clean_series(series: List[float]) -> List[float]:
    arr = np.asarray(series, dtype=float)
    # replace nan/inf with mean
    mask = ~np.isfinite(arr)
    if mask.any():
        arr[mask] = np.nanmean(arr) if np.isfinite(arr).any() else 0.0
    return arr.tolist()


def clip_series(series: List[float], low: Optional[float] = None, high: Optional[float] = None) -> List[float]:
    arr = np.asarray(series, dtype=float)
    if low is not None:
        arr = np.where(arr < low, low, arr)
    if high is not None:
        arr = np.where(arr > high, high, arr)
    return arr.tolist()


def scale_series(series: List[float], factor: float = 1.0) -> List[float]:
    return [v * factor for v in series]


def shift_series(series: List[float], offset: float = 0.0) -> List[float]:
    return [v + offset for v in series]


def reverse_series(series: List[float]) -> List[float]:
    return list(reversed(series))


def sort_series(series: List[float]) -> List[float]:
    return sorted(series)


def unique_series(series: List[float]) -> List[float]:
    return list(dict.fromkeys(series))


def dedupe_series(series: List[float]) -> List[float]:
    return unique_series(series)


def truncate_series(series: List[float], n: int) -> List[float]:
    return series[:n]


def pad_series(series: List[float], n: int, value: float = 0.0) -> List[float]:
    if len(series) >= n:
        return series[:n]
    return series + [value] * (n - len(series))


def concat_series(*series: List[float]) -> List[float]:
    out = []
    for s in series:
        out.extend(s)
    return out


def split_series(series: List[float], n: int) -> List[List[float]]:
    return [series[i:i + n] for i in range(0, len(series), n)]


def window_series(series: List[float], window: int, step: int = 1) -> List[List[float]]:
    return sliding_window(series, window, step)


def aggregate_series(series: List[float], func: str = "mean", window: int = 5) -> List[float]:
    arr = np.asarray(series, dtype=float)
    out = []
    for i in range(len(arr)):
        start = max(0, i - window + 1)
        chunk = arr[start:i + 1]
        if func == "mean":
            out.append(float(chunk.mean()))
        elif func == "sum":
            out.append(float(chunk.sum()))
        elif func == "min":
            out.append(float(chunk.min()))
        elif func == "max":
            out.append(float(chunk.max()))
        elif func == "std":
            out.append(float(chunk.std()))
        else:
            out.append(float(chunk.mean()))
    return out


def resample_series(series: List[float], new_len: int) -> List[float]:
    return resample_ts(series, new_len)


def interpolate_series(series: List[float], new_len: int) -> List[float]:
    return resample_ts(series, new_len)


def smooth_series(series: List[float], window: int = 5) -> List[float]:
    return moving_average(series, window=window)


def denoise_series(series: List[float], window: int = 5) -> List[float]:
    return moving_average(series, window=window)


def detrend_series(series: List[float]) -> List[float]:
    return detrend(series, method="linear")


def deseasonalize_series(series: List[float], period: int = 7) -> List[float]:
    return deseasonalize(series, period=period)


def standardize_series(series: List[float]) -> List[float]:
    return normalize_ts(series, method="zscore")


def minmax_series(series: List[float]) -> List[float]:
    return normalize_ts(series, method="minmax")


def robust_series(series: List[float]) -> List[float]:
    return normalize_ts(series, method="robust")


def log_series(series: List[float]) -> List[float]:
    return log_transform(series)


def sqrt_series(series: List[float]) -> List[float]:
    return sqrt_transform(series)


def diff_series(series: List[float], order: int = 1) -> List[float]:
    return difference(series, order=order)


def cumsum_series(series: List[float]) -> List[float]:
    return cumulative_stats(series)["cumsum"]


def cumprod_series(series: List[float]) -> List[float]:
    return cumulative_stats(series)["cumprod"]


def cummax_series(series: List[float]) -> List[float]:
    return cumulative_stats(series)["cummax"]


def cummin_series(series: List[float]) -> List[float]:
    return cumulative_stats(series)["cummin"]


def rolling_mean(series: List[float], window: int) -> List[float]:
    return rolling_stats(series, window)["mean"]


def rolling_std(series: List[float], window: int) -> List[float]:
    return rolling_stats(series, window)["std"]


def rolling_min(series: List[float], window: int) -> List[float]:
    return rolling_stats(series, window)["min"]


def rolling_max(series: List[float], window: int) -> List[float]:
    return rolling_stats(series, window)["max"]


def ewma(series: List[float], alpha: float = 0.3) -> List[float]:
    return exponential_moving_average(series, alpha=alpha)


def holt(series: List[float], alpha: float = 0.3, beta: float = 0.1) -> List[float]:
    return double_exponential_smoothing(series, alpha=alpha, beta=beta)


def holt_winters_smooth(series: List[float], period: int = 7) -> List[float]:
    return triple_exponential_smoothing(series, period=period)


def decompose_series(series: List[float], period: int = 7) -> Dict[str, List[float]]:
    return decompose(series, period=period)


def trend_series(series: List[float]) -> List[float]:
    return trend_decompose(series)


def seasonal_series(series: List[float], period: int = 7) -> List[float]:
    return seasonal_decompose_extract(series, period=period)


def residual_series(series: List[float], period: int = 7) -> List[float]:
    return residual_decompose(series, period=period)


def peak_series(series: List[float]) -> List[int]:
    return peaks(series)


def valley_series(series: List[float]) -> List[int]:
    return valleys(series)


def zero_crossing_series(series: List[float]) -> List[int]:
    return zero_crossings(series)


def change_point_series(series: List[float]) -> List[int]:
    return change_points(series)


def outlier_series(series: List[float]) -> List[int]:
    return detect_outliers_ts(series)


def fill_missing_series(series: List[Optional[float]]) -> List[float]:
    return fill_missing_ts(series, method="linear")


def interpolate_series_ts(series: List[float], factor: int = 2) -> List[float]:
    return interpolate(series, factor=factor)


def downsample_series(series: List[float], factor: int = 2) -> List[float]:
    return downsample(series, factor=factor)


def upsample_series(series: List[float], factor: int = 2) -> List[float]:
    return upsample(series, factor=factor)


def resample_series_ts(series: List[float], target_len: int) -> List[float]:
    return resample_ts(series, target_len)


def normalize_series_ts(series: List[float]) -> List[float]:
    return normalize_ts(series, method="minmax")


def standardize_series_ts(series: List[float]) -> List[float]:
    return normalize_ts(series, method="zscore")


def robust_series_ts(series: List[float]) -> List[float]:
    return normalize_ts(series, method="robust")


def log_series_ts(series: List[float]) -> List[float]:
    return log_transform(series)


def sqrt_series_ts(series: List[float]) -> List[float]:
    return sqrt_transform(series)


def diff_series_ts(series: List[float]) -> List[float]:
    return difference(series)


def cumsum_series_ts(series: List[float]) -> List[float]:
    return cumulative_stats(series)["cumsum"]


def cumprod_series_ts(series: List[float]) -> List[float]:
    return cumulative_stats(series)["cumprod"]


def cummax_series_ts(series: List[float]) -> List[float]:
    return cumulative_stats(series)["cummax"]


def cummin_series_ts(series: List[float]) -> List[float]:
    return cumulative_stats(series)["cummin"]


def acf_series(series: List[float]) -> List[float]:
    return acf(series)


def pacf_series(series: List[float]) -> List[float]:
    return pacf(series)


def fft_series(series: List[float]) -> Tuple[List[float], List[float]]:
    return fourier_transform(series)


def psd_series(series: List[float]) -> Tuple[List[float], List[float]]:
    return power_spectral_density(series)


def spectrogram_series(series: List[float]) -> Tuple[List, List, List]:
    return spectrogram(series)


def stft_series(series: List[float]) -> List:
    return stft(series).tolist() if hasattr(stft(series), "tolist") else []


def arima_series(series: List[float], steps: int = 5) -> List[float]:
    return arima_forecast(series, steps=steps)


def sarima_series(series: List[float], steps: int = 5) -> List[float]:
    return sarima_forecast(series, steps=steps)


def prophet_series(series: List[float], steps: int = 5) -> List[float]:
    return prophet_like_forecast(series, steps=steps)


def ets_series(series: List[float], steps: int = 5) -> List[float]:
    return exponential_smoothing_forecast(series, steps=steps)


def theta_series(series: List[float], steps: int = 5) -> List[float]:
    return theta_forecast(series, steps=steps)


def naive_series(series: List[float], steps: int = 5) -> List[float]:
    return naive_forecast(series, steps=steps)


def seasonal_naive_series(series: List[float], steps: int = 5) -> List[float]:
    return seasonal_naive_forecast(series, steps=steps)


def drift_series(series: List[float], steps: int = 5) -> List[float]:
    return drift_forecast(series, steps=steps)


def mean_series(series: List[float], steps: int = 5) -> List[float]:
    return mean_forecast(series, steps=steps)


def median_series(series: List[float], steps: int = 5) -> List[float]:
    return median_forecast(series, steps=steps)


def random_walk_series(series: List[float], steps: int = 5) -> List[float]:
    return random_walk_forecast(series, steps=steps)


def monte_carlo_series(series: List[float], steps: int = 5) -> List[float]:
    return monte_carlo_forecast(series, steps=steps)


def forecast_intervals_series(series: List[float], steps: int = 5) -> Dict[str, List[float]]:
    return forecast_intervals(series, steps=steps)


def evaluate_series(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    return evaluate_forecast(actual, predicted)


def mase_series(actual: List[float], predicted: List[float], train: List[float]) -> float:
    return mase(actual, predicted, train)


def smape_series(actual: List[float], predicted: List[float]) -> float:
    return smape_metric(actual, predicted)


def mape_series(actual: List[float], predicted: List[float]) -> float:
    return mape_metric(actual, predicted)


def rmse_series(actual: List[float], predicted: List[float]) -> float:
    return rmse_metric(actual, predicted)


def mae_series(actual: List[float], predicted: List[float]) -> float:
    return mae_metric(actual, predicted)


def r2_series(actual: List[float], predicted: List[float]) -> float:
    return r2_metric(actual, predicted)


def theil_u_series(actual: List[float], predicted: List[float]) -> float:
    return theil_u(actual, predicted)


def track_sn_series(series: List[float]) -> Dict[str, float]:
    return track_signal_noise(series)


def boxcox_series(series: List[float]) -> Tuple[List[float], float]:
    return boxcox_transform(series)


def yeo_johnson_series(series: List[float]) -> Tuple[List[float], float]:
    return yeo_johnson_transform(series)


def log_series_ts2(series: List[float]) -> List[float]:
    return log_transform(series)


def sqrt_series_ts2(series: List[float]) -> List[float]:
    return sqrt_transform(series)


def reciprocal_series(series: List[float]) -> List[float]:
    return reciprocal_transform(series)


def difference_series2(series: List[float], order: int = 1) -> List[float]:
    return difference_transform(series, order=order)


def stationarity_series(series: List[float]) -> Dict[str, Any]:
    return stationarity_check(series)


def make_stationary_series(series: List[float]) -> Tuple[List[float], int]:
    return make_stationary(series)


def create_ts_features(series: List[float], lags: int = 5) -> List[List[float]]:
    return create_time_series_features(series, lags=lags)


def create_rolling_ts_features(series: List[float]) -> List[Dict[str, float]]:
    return create_rolling_features(series)


def create_lag_ts_features(series: List[float], lags: int = 5) -> List[Dict[str, float]]:
    return create_lag_features(series, lags=lags)


def create_date_ts_features(dates: List[str]) -> List[Dict[str, int]]:
    return create_date_features(dates)


def create_cyclical_ts_features(values: List[int], period: int) -> List[Tuple[float, float]]:
    return create_cyclical_features(values, period)


def create_interaction_ts_features(features: List[List[float]]) -> List[List[float]]:
    return create_interaction_features(features)


def create_polynomial_ts_features(features: List[List[float]], degree: int = 2) -> List[List[float]]:
    return create_polynomial_features(features, degree=degree)


def create_binned_ts_features(values: List[float], bins: int = 5) -> List[int]:
    return create_binned_features(values, bins=bins)


def create_quantile_ts_features(values: List[float]) -> List[float]:
    return create_quantile_features(values)


def create_rank_ts_features(values: List[float]) -> List[int]:
    return create_rank_features(values)


def create_density_ts_features(values: List[float]) -> List[float]:
    return create_density_features(values)


def create_outlier_ts_features(values: List[float]) -> List[int]:
    return create_outlier_features(values)


def create_missing_ts_features(values: List[Optional[float]]) -> List[int]:
    return create_missing_indicators(values)


def create_time_ts_features(timestamps: List[int]) -> List[Dict[str, int]]:
    return create_time_features(timestamps)


def create_frequency_ts_features(series: List[float]) -> Dict[str, float]:
    return create_frequency_features(series)


def create_entropy_ts_features(series: List[float]) -> Dict[str, float]:
    return create_entropy_features(series)


def create_complexity_ts_features(series: List[float]) -> Dict[str, float]:
    return create_complexity_features(series)


def create_statistical_ts_features(series: List[float]) -> Dict[str, float]:
    return create_statistical_features(series)


def create_all_ts_features(series: List[float]) -> Dict[str, Any]:
    return create_all_features(series)


def flatten_ts_features(features: Dict[str, Any]) -> List[float]:
    return flatten_features(features)


def feature_vector_ts(series: List[float]) -> List[float]:
    return feature_vector(series)


def batch_feature_vectors_ts(series_list: List[List[float]]) -> List[List[float]]:
    return batch_feature_vectors(series_list)


def save_feature_vectors_ts(path: str, vectors: List[List[float]]) -> None:
    save_feature_vectors(path, vectors)


def load_feature_vectors_ts(path: str) -> List[List[float]]:
    return load_feature_vectors(path)


def normalize_feature_vectors_ts(vectors: List[List[float]]) -> List[List[float]]:
    return normalize_feature_vectors(vectors)


def scale_feature_vectors_ts(vectors: List[List[float]], method: str = "standard") -> List[List[float]]:
    return scale_feature_vectors(vectors, method=method)


def reduce_feature_vectors_ts(vectors: List[List[float]], n_components: int = 2) -> List[List[float]]:
    from sklearn.decomposition import PCA

    arr = np.asarray(vectors, dtype=float)
    if arr.shape[0] < 2:
        return vectors
    pca = PCA(n_components=min(n_components, arr.shape[1]))
    return pca.fit_transform(arr).tolist()


def cluster_feature_vectors_ts(vectors: List[List[float]], n_clusters: int = 3) -> List[int]:
    from sklearn.cluster import KMeans

    arr = np.asarray(vectors, dtype=float)
    km = KMeans(n_clusters=min(n_clusters, arr.shape[0]), random_state=42, n_init=10)
    return km.fit_predict(arr).tolist()


def detect_anomalies_ts(vectors: List[List[float]]) -> List[int]:
    return detect_anomalies(vectors)


def compute_similarity_matrix_ts(vectors: List[List[float]]) -> List[List[float]]:
    return compute_similarity_matrix(vectors)


def find_nearest_neighbors_ts(vectors: List[List[float]], query: List[float], k: int = 5) -> List[int]:
    return find_nearest_neighbors(vectors, query, k=k)


def compute_distance_matrix_ts(vectors: List[List[float]]) -> List[List[float]]:
    return compute_distance_matrix(vectors)


def create_ts_dataset(series: List[float], window: int = 5, horizon: int = 1):
    return create_time_series_dataset(series, window=window, horizon=horizon)


def train_ts_model(X, y, model_type: str = "linear"):
    return train_time_series_model(X, y, model_type=model_type)


def forecast_ts(model, last_window: List[float], steps: int = 5) -> List[float]:
    return forecast_time_series(model, last_window, steps=steps)


def evaluate_ts(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    return evaluate_time_series(actual, predicted)


def backtest_ts(series: List[float], window: int = 5) -> Dict[str, Any]:
    return backtest_time_series(series, window=window)


def cross_validate_ts(series: List[float], window: int = 5, k: int = 5) -> List[float]:
    return cross_validate_time_series(series, window=window, k=k)


def grid_search_ts(series: List[float], window: int = 5) -> Dict[str, Any]:
    return grid_search_time_series(series, window=window)


def ensemble_forecast_ts(series: List[float], steps: int = 5) -> List[float]:
    return ensemble_time_series_forecast(series, steps=steps)


def weighted_forecast_ts(series: List[float], steps: int = 5) -> List[float]:
    return weighted_ensemble_forecast(series, steps=steps)


def stacking_forecast_ts(series: List[float], steps: int = 5) -> List[float]:
    return stacking_forecast(series, steps=steps)


def blending_forecast_ts(series: List[float], steps: int = 5) -> List[float]:
    return blending_forecast(series, steps=steps)


def create_forecast_report_ts(series: List[float], steps: int = 5) -> Dict[str, Any]:
    return create_forecast_report(series, steps=steps)


def save_forecast_report_ts(path: str, report: Dict[str, Any]) -> None:
    save_forecast_report(path, report)


def load_forecast_report_ts(path: str) -> Dict[str, Any]:
    return load_forecast_report(path)


def format_forecast_report_ts(report: Dict[str, Any]) -> str:
    return format_forecast_report(report)


def export_forecast_csv_ts(path: str, report: Dict[str, Any]) -> None:
    export_forecast_csv(path, report)


def import_forecast_csv_ts(path: str) -> Dict[str, Any]:
    return import_forecast_csv(path)


def validate_series_ts(series: List[float]) -> bool:
    return validate_series(series)


def clean_series_ts(series: List[float]) -> List[float]:
    return clean_series(series)


def clip_series_ts(series: List[float], low: Optional[float] = None, high: Optional[float] = None) -> List[float]:
    return clip_series(series, low=low, high=high)


def scale_series_ts(series: List[float], factor: float = 1.0) -> List[float]:
    return scale_series(series, factor=factor)


def shift_series_ts(series: List[float], offset: float = 0.0) -> List[float]:
    return shift_series(series, offset=offset)


def reverse_series_ts(series: List[float]) -> List[float]:
    return reverse_series(series)


def sort_series_ts(series: List[float]) -> List[float]:
    return sort_series(series)


def unique_series_ts(series: List[float]) -> List[float]:
    return unique_series(series)


def dedupe_series_ts(series: List[float]) -> List[float]:
    return dedupe_series(series)


def truncate_series_ts(series: List[float], n: int) -> List[float]:
    return truncate_series(series, n)


def pad_series_ts(series: List[float], n: int, value: float = 0.0) -> List[float]:
    return pad_series(series, n, value=value)


def concat_series_ts(*series: List[float]) -> List[float]:
    return concat_series(*series)


def split_series_ts(series: List[float], n: int) -> List[List[float]]:
    return split_series(series, n)


def window_series_ts(series: List[float], window: int, step: int = 1) -> List[List[float]]:
    return window_series(series, window, step)


def aggregate_series_ts(series: List[float], func: str = "mean", window: int = 5) -> List[float]:
    return aggregate_series(series, func=func, window=window)


def resample_series_ts2(series: List[float], new_len: int) -> List[float]:
    return resample_series(series, new_len)


def interpolate_series_ts2(series: List[float], new_len: int) -> List[float]:
    return interpolate_series(series, new_len)


def smooth_series_ts(series: List[float], window: int = 5) -> List[float]:
    return smooth_series(series, window=window)


def denoise_series_ts(series: List[float], window: int = 5) -> List[float]:
    return denoise_series(series, window=window)


def detrend_series_ts(series: List[float]) -> List[float]:
    return detrend_series(series)


def deseasonalize_series_ts(series: List[float], period: int = 7) -> List[float]:
    return deseasonalize_series(series, period=period)


def standardize_series_ts2(series: List[float]) -> List[float]:
    return standardize_series(series)


def minmax_series_ts(series: List[float]) -> List[float]:
    return minmax_series(series)


def robust_series_ts2(series: List[float]) -> List[float]:
    return robust_series(series)


def log_series_ts3(series: List[float]) -> List[float]:
    return log_series(series)


def sqrt_series_ts3(series: List[float]) -> List[float]:
    return sqrt_series(series)


def diff_series_ts2(series: List[float], order: int = 1) -> List[float]:
    return diff_series(series, order=order)


def cumsum_series_ts2(series: List[float]) -> List[float]:
    return cumsum_series(series)


def cumprod_series_ts2(series: List[float]) -> List[float]:
    return cumprod_series(series)


def cummax_series_ts2(series: List[float]) -> List[float]:
    return cummax_series(series)


def cummin_series_ts2(series: List[float]) -> List[float]:
    return cummin_series(series)


def rolling_mean_ts(series: List[float], window: int) -> List[float]:
    return rolling_mean(series, window)


def rolling_std_ts(series: List[float], window: int) -> List[float]:
    return rolling_std(series, window)


def rolling_min_ts(series: List[float], window: int) -> List[float]:
    return rolling_min(series, window)


def rolling_max_ts(series: List[float], window: int) -> List[float]:
    return rolling_max(series, window)


def ewma_ts(series: List[float], alpha: float = 0.3) -> List[float]:
    return ewma(series, alpha=alpha)


def holt_ts(series: List[float]) -> List[float]:
    return holt(series)


def holt_winters_ts(series: List[float], period: int = 7) -> List[float]:
    return holt_winters_smooth(series, period=period)


def decompose_series_ts(series: List[float], period: int = 7) -> Dict[str, List[float]]:
    return decompose_series(series, period=period)


def trend_series_ts(series: List[float]) -> List[float]:
    return trend_series(series)


def seasonal_series_ts(series: List[float], period: int = 7) -> List[float]:
    return seasonal_series(series, period=period)


def residual_series_ts(series: List[float], period: int = 7) -> List[float]:
    return residual_series(series, period=period)


def peak_series_ts(series: List[float]) -> List[int]:
    return peak_series(series)


def valley_series_ts(series: List[float]) -> List[int]:
    return valley_series(series)


def zero_crossing_series_ts(series: List[float]) -> List[int]:
    return zero_crossing_series(series)


def change_point_series_ts(series: List[float]) -> List[int]:
    return change_point_series(series)


def outlier_series_ts(series: List[float]) -> List[int]:
    return outlier_series(series)


def fill_missing_series_ts(series: List[Optional[float]]) -> List[float]:
    return fill_missing_series(series)


def interpolate_series_ts3(series: List[float], factor: int = 2) -> List[float]:
    return interpolate_series_ts(series, factor=factor)


def downsample_series_ts2(series: List[float], factor: int = 2) -> List[float]:
    return downsample_series(series, factor=factor)


def upsample_series_ts2(series: List[float], factor: int = 2) -> List[float]:
    return upsample_series(series, factor=factor)


def resample_series_ts3(series: List[float], target_len: int) -> List[float]:
    return resample_series_ts(series, target_len)


def acf_series_ts(series: List[float]) -> List[float]:
    return acf_series(series)


def pacf_series_ts(series: List[float]) -> List[float]:
    return pacf_series(series)


def fft_series_ts(series: List[float]) -> Tuple[List[float], List[float]]:
    return fft_series(series)


def psd_series_ts(series: List[float]) -> Tuple[List[float], List[float]]:
    return psd_series(series)


def spectrogram_series_ts(series: List[float]) -> Tuple[List, List, List]:
    return spectrogram_series(series)


def arima_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return arima_series(series, steps=steps)


def sarima_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return sarima_series(series, steps=steps)


def prophet_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return prophet_series(series, steps=steps)


def ets_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return ets_series(series, steps=steps)


def theta_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return theta_series(series, steps=steps)


def naive_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return naive_series(series, steps=steps)


def seasonal_naive_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return seasonal_naive_series(series, steps=steps)


def drift_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return drift_series(series, steps=steps)


def mean_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return mean_series(series, steps=steps)


def median_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return median_series(series, steps=steps)


def random_walk_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return random_walk_series(series, steps=steps)


def monte_carlo_series_ts(series: List[float], steps: int = 5) -> List[float]:
    return monte_carlo_series(series, steps=steps)


def forecast_intervals_series_ts(series: List[float], steps: int = 5) -> Dict[str, List[float]]:
    return forecast_intervals_series(series, steps=steps)


def evaluate_series_ts(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    return evaluate_series(actual, predicted)


def mase_series_ts(actual: List[float], predicted: List[float], train: List[float]) -> float:
    return mase_series(actual, predicted, train)


def smape_series_ts(actual: List[float], predicted: List[float]) -> float:
    return smape_series(actual, predicted)


def mape_series_ts(actual: List[float], predicted: List[float]) -> float:
    return mape_series(actual, predicted)


def rmse_series_ts(actual: List[float], predicted: List[float]) -> float:
    return rmse_series(actual, predicted)


def mae_series_ts(actual: List[float], predicted: List[float]) -> float:
    return mae_series(actual, predicted)


def r2_series_ts(actual: List[float], predicted: List[float]) -> float:
    return r2_series(actual, predicted)


def theil_u_series_ts(actual: List[float], predicted: List[float]) -> float:
    return theil_u_series(actual, predicted)


def track_sn_series_ts(series: List[float]) -> Dict[str, float]:
    return track_sn_series(series)


def boxcox_series_ts(series: List[float]) -> Tuple[List[float], float]:
    return boxcox_series(series)


def yeo_johnson_series_ts(series: List[float]) -> Tuple[List[float], float]:
    return yeo_johnson_series(series)


def validate_series_ts2(series: List[float]) -> bool:
    return validate_series(series)


def clean_series_ts2(series: List[float]) -> List[float]:
    return clean_series(series)


def clip_series_ts2(series: List[float], low=None, high=None) -> List[float]:
    return clip_series(series, low=low, high=high)


def scale_series_ts2(series: List[float], factor: float = 1.0) -> List[float]:
    return scale_series(series, factor=factor)


def shift_series_ts2(series: List[float], offset: float = 0.0) -> List[float]:
    return shift_series(series, offset=offset)


def reverse_series_ts2(series: List[float]) -> List[float]:
    return reverse_series(series)


def sort_series_ts2(series: List[float]) -> List[float]:
    return sort_series(series)


def unique_series_ts2(series: List[float]) -> List[float]:
    return unique_series(series)


def dedupe_series_ts2(series: List[float]) -> List[float]:
    return dedupe_series(series)


def truncate_series_ts2(series: List[float], n: int) -> List[float]:
    return truncate_series(series, n)


def pad_series_ts2(series: List[float], n: int, value: float = 0.0) -> List[float]:
    return pad_series(series, n, value=value)


def concat_series_ts2(*series: List[float]) -> List[float]:
    return concat_series(*series)


def split_series_ts2(series: List[float], n: int) -> List[List[float]]:
    return split_series(series, n)


def window_series_ts2(series: List[float], window: int, step: int = 1) -> List[List[float]]:
    return window_series(series, window, step)


def aggregate_series_ts2(series: List[float], func: str = "mean", window: int = 5) -> List[float]:
    return aggregate_series(series, func=func, window=window)


def create_ts_features_ts(series: List[float], lags: int = 5) -> List[List[float]]:
    return create_ts_features(series, lags=lags)


def create_rolling_ts_features_ts(series: List[float]) -> List[Dict[str, float]]:
    return create_rolling_ts_features(series)


def create_lag_ts_features_ts(series: List[float], lags: int = 5) -> List[Dict[str, float]]:
    return create_lag_ts_features(series, lags=lags)


def create_date_ts_features_ts(dates: List[str]) -> List[Dict[str, int]]:
    return create_date_ts_features(dates)


def create_cyclical_ts_features_ts(values: List[int], period: int) -> List[Tuple[float, float]]:
    return create_cyclical_ts_features(values, period)


def create_interaction_ts_features_ts(features: List[List[float]]) -> List[List[float]]:
    return create_interaction_ts_features(features)


def create_polynomial_ts_features_ts(features: List[List[float]], degree: int = 2) -> List[List[float]]:
    return create_polynomial_ts_features(features, degree=degree)


def create_binned_ts_features_ts(values: List[float], bins: int = 5) -> List[int]:
    return create_binned_ts_features(values, bins=bins)


def create_quantile_ts_features_ts(values: List[float]) -> List[float]:
    return create_quantile_ts_features(values)


def create_rank_ts_features_ts(values: List[float]) -> List[int]:
    return create_rank_ts_features(values)


def create_density_ts_features_ts(values: List[float]) -> List[float]:
    return create_density_ts_features(values)


def create_outlier_ts_features_ts(values: List[float]) -> List[int]:
    return create_outlier_ts_features(values)


def create_missing_ts_features_ts(values: List[Optional[float]]) -> List[int]:
    return create_missing_ts_features(values)


def create_time_ts_features_ts(timestamps: List[int]) -> List[Dict[str, int]]:
    return create_time_ts_features(timestamps)


def create_frequency_ts_features_ts(series: List[float]) -> Dict[str, float]:
    return create_frequency_ts_features(series)


def create_entropy_ts_features_ts(series: List[float]) -> Dict[str, float]:
    return create_entropy_ts_features(series)


def create_complexity_ts_features_ts(series: List[float]) -> Dict[str, float]:
    return create_complexity_ts_features(series)


def create_statistical_ts_features_ts(series: List[float]) -> Dict[str, float]:
    return create_statistical_ts_features(series)


def create_all_ts_features_ts(series: List[float]) -> Dict[str, Any]:
    return create_all_ts_features(series)


def flatten_ts_features_ts(features: Dict[str, Any]) -> List[float]:
    return flatten_features(features)


def feature_vector_ts2(series: List[float]) -> List[float]:
    return feature_vector(series)


def batch_feature_vectors_ts2(series_list: List[List[float]]) -> List[List[float]]:
    return batch_feature_vectors(series_list)


def save_feature_vectors_ts2(path: str, vectors: List[List[float]]) -> None:
    save_feature_vectors(path, vectors)


def load_feature_vectors_ts2(path: str) -> List[List[float]]:
    return load_feature_vectors(path)


def normalize_feature_vectors_ts2(vectors: List[List[float]]) -> List[List[float]]:
    return normalize_feature_vectors(vectors)


def scale_feature_vectors_ts2(vectors: List[List[float]], method: str = "standard") -> List[List[float]]:
    return scale_feature_vectors(vectors, method=method)


def reduce_feature_vectors_ts2(vectors: List[List[float]], n_components: int = 2) -> List[List[float]]:
    return reduce_feature_vectors(vectors, n_components=n_components)


def cluster_feature_vectors_ts2(vectors: List[List[float]], n_clusters: int = 3) -> List[int]:
    return cluster_feature_vectors(vectors, n_clusters=n_clusters)


def detect_anomalies_ts2(vectors: List[List[float]]) -> List[int]:
    return detect_anomalies(vectors)


def compute_similarity_matrix_ts2(vectors: List[List[float]]) -> List[List[float]]:
    return compute_similarity_matrix(vectors)


def find_nearest_neighbors_ts2(vectors: List[List[float]], query: List[float], k: int = 5) -> List[int]:
    return find_nearest_neighbors(vectors, query, k=k)


def compute_distance_matrix_ts2(vectors: List[List[float]]) -> List[List[float]]:
    return compute_distance_matrix(vectors)


def create_ts_dataset_ts(series: List[float], window: int = 5, horizon: int = 1):
    return create_ts_dataset(series, window=window, horizon=horizon)


def train_ts_model_ts(X, y, model_type: str = "linear"):
    return train_ts_model(X, y, model_type=model_type)


def forecast_ts_ts(model, last_window: List[float], steps: int = 5) -> List[float]:
    return forecast_ts(model, last_window, steps=steps)


def evaluate_ts_ts(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    return evaluate_ts(actual, predicted)


def backtest_ts_ts(series: List[float], window: int = 5) -> Dict[str, Any]:
    return backtest_ts(series, window=window)


def cross_validate_ts_ts(series: List[float], window: int = 5, k: int = 5) -> List[float]:
    return cross_validate_ts(series, window=window, k=k)


def grid_search_ts_ts(series: List[float], window: int = 5) -> Dict[str, Any]:
    return grid_search_ts(series, window=window)


def ensemble_forecast_ts2(series: List[float], steps: int = 5) -> List[float]:
    return ensemble_forecast_ts(series, steps=steps)


def weighted_forecast_ts2(series: List[float], steps: int = 5) -> List[float]:
    return weighted_forecast_ts(series, steps=steps)


def stacking_forecast_ts2(series: List[float], steps: int = 5) -> List[float]:
    return stacking_forecast_ts(series, steps=steps)


def blending_forecast_ts2(series: List[float], steps: int = 5) -> List[float]:
    return blending_forecast_ts(series, steps=steps)


def create_forecast_report_ts2(series: List[float], steps: int = 5) -> Dict[str, Any]:
    return create_forecast_report_ts(series, steps=steps)


def save_forecast_report_ts2(path: str, report: Dict[str, Any]) -> None:
    save_forecast_report_ts(path, report)


def load_forecast_report_ts2(path: str) -> Dict[str, Any]:
    return load_forecast_report_ts(path)


def format_forecast_report_ts2(report: Dict[str, Any]) -> str:
    return format_forecast_report_ts(report)


def export_forecast_csv_ts2(path: str, report: Dict[str, Any]) -> None:
    export_forecast_csv_ts(path, report)


def import_forecast_csv_ts2(path: str) -> Dict[str, Any]:
    return import_forecast_csv_ts(path)


def validate_series_ts3(series: List[float]) -> bool:
    return validate_series_ts2(series)


def clean_series_ts3(series: List[float]) -> List[float]:
    return clean_series_ts2(series)


def clip_series_ts3(series: List[float], low=None, high=None) -> List[float]:
    return clip_series_ts2(series, low=low, high=high)


def scale_series_ts3(series: List[float], factor: float = 1.0) -> List[float]:
    return scale_series_ts2(series, factor=factor)


def shift_series_ts3(series: List[float], offset: float = 0.0) -> List[float]:
    return shift_series_ts2(series, offset=offset)


def reverse_series_ts3(series: List[float]) -> List[float]:
    return reverse_series_ts2(series)


def sort_series_ts3(series: List[float]) -> List[float]:
    return sort_series_ts2(series)


def unique_series_ts3(series: List[float]) -> List[float]:
    return unique_series_ts2(series)


def dedupe_series_ts3(series: List[float]) -> List[float]:
    return dedupe_series_ts2(series)


def truncate_series_ts3(series: List[float], n: int) -> List[float]:
    return truncate_series_ts2(series, n)


def pad_series_ts3(series: List[float], n: int, value: float = 0.0) -> List[float]:
    return pad_series_ts2(series, n, value=value)


def concat_series_ts3(*series: List[float]) -> List[float]:
    return concat_series_ts2(*series)


def split_series_ts3(series: List[float], n: int) -> List[List[float]]:
    return split_series_ts2(series, n)


def window_series_ts3(series: List[float], window: int, step: int = 1) -> List[List[float]]:
    return window_series_ts2(series, window, step)


def aggregate_series_ts3(series: List[float], func: str = "mean", window: int = 5) -> List[float]:
    return aggregate_series_ts2(series, func=func, window=window)


def acf_series_ts2(series: List[float]) -> List[float]:
    return acf_series_ts(series)


def pacf_series_ts2(series: List[float]) -> List[float]:
    return pacf_series_ts(series)


def fft_series_ts2(series: List[float]) -> Tuple[List[float], List[float]]:
    return fft_series_ts(series)


def psd_series_ts2(series: List[float]) -> Tuple[List[float], List[float]]:
    return psd_series_ts(series)


def spectrogram_series_ts2(series: List[float]) -> Tuple[List, List, List]:
    return spectrogram_series_ts(series)


def arima_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return arima_series_ts(series, steps=steps)


def sarima_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return sarima_series_ts(series, steps=steps)


def prophet_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return prophet_series_ts(series, steps=steps)


def ets_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return ets_series_ts(series, steps=steps)


def theta_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return theta_series_ts(series, steps=steps)


def naive_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return naive_series_ts(series, steps=steps)


def seasonal_naive_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return seasonal_naive_series_ts(series, steps=steps)


def drift_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return drift_series_ts(series, steps=steps)


def mean_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return mean_series_ts(series, steps=steps)


def median_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return median_series_ts(series, steps=steps)


def random_walk_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return random_walk_series_ts(series, steps=steps)


def monte_carlo_series_ts2(series: List[float], steps: int = 5) -> List[float]:
    return monte_carlo_series_ts(series, steps=steps)


def forecast_intervals_series_ts2(series: List[float], steps: int = 5) -> Dict[str, List[float]]:
    return forecast_intervals_series_ts(series, steps=steps)


def evaluate_series_ts2(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    return evaluate_series_ts(actual, predicted)


def mase_series_ts2(actual: List[float], predicted: List[float], train: List[float]) -> float:
    return mase_series_ts(actual, predicted, train)


def smape_series_ts2(actual: List[float], predicted: List[float]) -> float:
    return smape_series_ts(actual, predicted)


def mape_series_ts2(actual: List[float], predicted: List[float]) -> float:
    return mape_series_ts(actual, predicted)


def rmse_series_ts2(actual: List[float], predicted: List[float]) -> float:
    return rmse_series_ts(actual, predicted)


def mae_series_ts2(actual: List[float], predicted: List[float]) -> float:
    return mae_series_ts(actual, predicted)


def r2_series_ts2(actual: List[float], predicted: List[float]) -> float:
    return r2_series_ts(actual, predicted)


def theil_u_series_ts2(actual: List[float], predicted: List[float]) -> float:
    return theil_u_series_ts(actual, predicted)


def track_sn_series_ts2(series: List[float]) -> Dict[str, float]:
    return track_sn_series_ts(series)


def boxcox_series_ts2(series: List[float]) -> Tuple[List[float], float]:
    return boxcox_series_ts(series)


def yeo_johnson_series_ts2(series: List[float]) -> Tuple[List[float], float]:
    return yeo_johnson_series_ts(series)


def validate_series_ts4(series: List[float]) -> bool:
    return validate_series_ts3(series)


def clean_series_ts4(series: List[float]) -> List[float]:
    return clean_series_ts3(series)


def clip_series_ts4(series: List[float], low=None, high=None) -> List[float]:
    return clip_series_ts3(series, low=low, high=high)


def scale_series_ts4(series: List[float], factor: float = 1.0) -> List[float]:
    return scale_series_ts3(series, factor=factor)


def shift_series_ts4(series: List[float], offset: float = 0.0) -> List[float]:
    return shift_series_ts3(series, offset=offset)


def reverse_series_ts4(series: List[float]) -> List[float]:
    return reverse_series_ts3(series)


def sort_series_ts4(series: List[float]) -> List[float]:
    return sort_series_ts3(series)


def unique_series_ts4(series: List[float]) -> List[float]:
    return unique_series_ts3(series)


def dedupe_series_ts4(series: List[float]) -> List[float]:
    return dedupe_series_ts3(series)


def truncate_series_ts4(series: List[float], n: int) -> List[float]:
    return truncate_series_ts3(series, n)


def pad_series_ts4(series: List[float], n: int, value: float = 0.0) -> List[float]:
    return pad_series_ts3(series, n, value=value)


def concat_series_ts4(*series: List[float]) -> List[float]:
    return concat_series_ts3(*series)


def split_series_ts4(series: List[float], n: int) -> List[List[float]]:
    return split_series_ts3(series, n)


def window_series_ts4(series: List[float], window: int, step: int = 1) -> List[List[float]]:
    return window_series_ts3(series, window, step)


def aggregate_series_ts4(series: List[float], func: str = "mean", window: int = 5) -> List[float]:
    return aggregate_series_ts3(series, func=func, window=window)


def acf_series_ts3(series: List[float]) -> List[float]:
    return acf_series_ts2(series)


def pacf_series_ts3(series: List[float]) -> List[float]:
    return pacf_series_ts2(series)


def fft_series_ts3(series: List[float]) -> Tuple[List[float], List[float]]:
    return fft_series_ts2(series)


def psd_series_ts3(series: List[float]) -> Tuple[List[float], List[float]]:
    return psd_series_ts2(series)


def spectrogram_series_ts3(series: List[float]) -> Tuple[List, List, List]:
    return spectrogram_series_ts2(series)


def arima_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return arima_series_ts2(series, steps=steps)


def sarima_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return sarima_series_ts2(series, steps=steps)


def prophet_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return prophet_series_ts2(series, steps=steps)


def ets_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return ets_series_ts2(series, steps=steps)


def theta_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return theta_series_ts2(series, steps=steps)


def naive_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return naive_series_ts2(series, steps=steps)


def seasonal_naive_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return seasonal_naive_series_ts2(series, steps=steps)


def drift_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return drift_series_ts2(series, steps=steps)


def mean_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return mean_series_ts2(series, steps=steps)


def median_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return median_series_ts2(series, steps=steps)


def random_walk_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return random_walk_series_ts2(series, steps=steps)


def monte_carlo_series_ts3(series: List[float], steps: int = 5) -> List[float]:
    return monte_carlo_series_ts2(series, steps=steps)


def forecast_intervals_series_ts3(series: List[float], steps: int = 5) -> Dict[str, List[float]]:
    return forecast_intervals_series_ts2(series, steps=steps)


def evaluate_series_ts3(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    return evaluate_series_ts2(actual, predicted)


def mase_series_ts3(actual: List[float], predicted: List[float], train: List[float]) -> float:
    return mase_series_ts2(actual, predicted, train)


def smape_series_ts3(actual: List[float], predicted: List[float]) -> float:
    return smape_series_ts2(actual, predicted)


def mape_series_ts3(actual: List[float], predicted: List[float]) -> float:
    return mape_series_ts2(actual, predicted)


def rmse_series_ts3(actual: List[float], predicted: List[float]) -> float:
    return rmse_series_ts2(actual, predicted)


def mae_series_ts3(actual: List[float], predicted: List[float]) -> float:
    return mae_series_ts2(actual, predicted)


def r2_series_ts3(actual: List[float], predicted: List[float]) -> float:
    return r2_series_ts2(actual, predicted)


def theil_u_series_ts3(actual: List[float], predicted: List[float]) -> float:
    return theil_u_series_ts2(actual, predicted)


def track_sn_series_ts3(series: List[float]) -> Dict[str, float]:
    return track_sn_series_ts2(series)


def boxcox_series_ts3(series: List[float]) -> Tuple[List[float], float]:
    return boxcox_series_ts2(series)


def yeo_johnson_series_ts3(series: List[float]) -> Tuple[List[float], float]:
    return yeo_johnson_series_ts2(series)


def validate_series_ts5(series: List[float]) -> bool:
    return validate_series_ts4(series)


def clean_series_ts5(series: List[float]) -> List[float]:
    return clean_series_ts4(series)


def clip_series_ts5(series: List[float], low=None, high=None) -> List[float]:
    return clip_series_ts4(series, low=low, high=high)


def scale_series_ts5(series: List[float], factor: float = 1.0) -> List[float]:
    return scale_series_ts4(series, factor=factor)


def shift_series_ts5(series: List[float], offset: float = 0.0) -> List[float]:
    return shift_series_ts4(series, offset=offset)


def reverse_series_ts5(series: List[float]) -> List[float]:
    return reverse_series_ts4(series)


def sort_series_ts5(series: List[float]) -> List[float]:
    return sort_series_ts4(series)


def unique_series_ts5(series: List[float]) -> List[float]:
    return unique_series_ts4(series)


def dedupe_series_ts5(series: List[float]) -> List[float]:
    return dedupe_series_ts4(series)


def truncate_series_ts5(series: List[float], n: int) -> List[float]:
    return truncate_series_ts4(series, n)


def pad_series_ts5(series: List[float], n: int, value: float = 0.0) -> List[float]:
    return pad_series_ts4(series, n, value=value)


def concat_series_ts5(*series: List[float]) -> List[float]:
    return concat_series_ts4(*series)


def split_series_ts5(series: List[float], n: int) -> List[List[float]]:
    return split_series_ts4(series, n)


def window_series_ts5(series: List[float], window: int, step: int = 1) -> List[List[float]]:
    return window_series_ts4(series, window, step)


def aggregate_series_ts5(series: List[float], func: str = "mean", window: int = 5) -> List[float]:
    return aggregate_series_ts4(series, func=func, window=window)


def create_ts_features_ts2(series: List[float], lags: int = 5) -> List[List[float]]:
    return create_ts_features_ts(series, lags=lags)


def create_rolling_ts_features_ts2(series: List[float]) -> List[Dict[str, float]]:
    return create_rolling_ts_features_ts(series)


def create_lag_ts_features_ts2(series: List[float], lags: int = 5) -> List[Dict[str, float]]:
    return create_lag_ts_features_ts(series, lags=lags)


def create_date_ts_features_ts2(dates: List[str]) -> List[Dict[str, int]]:
    return create_date_ts_features_ts(dates)


def create_cyclical_ts_features_ts2(values: List[int], period: int) -> List[Tuple[float, float]]:
    return create_cyclical_ts_features_ts(values, period)


def create_interaction_ts_features_ts2(features: List[List[float]]) -> List[List[float]]:
    return create_interaction_ts_features_ts(features)


def create_polynomial_ts_features_ts2(features: List[List[float]], degree: int = 2) -> List[List[float]]:
    return create_polynomial_ts_features_ts(features, degree=degree)


def create_binned_ts_features_ts2(values: List[float], bins: int = 5) -> List[int]:
    return create_binned_ts_features_ts(values, bins=bins)


def create_quantile_ts_features_ts2(values: List[float]) -> List[float]:
    return create_quantile_ts_features_ts(values)


def create_rank_ts_features_ts2(values: List[float]) -> List[int]:
    return create_rank_ts_features_ts(values)


def create_density_ts_features_ts2(values: List[float]) -> List[float]:
    return create_density_ts_features_ts(values)


def create_outlier_ts_features_ts2(values: List[float]) -> List[int]:
    return create_outlier_ts_features_ts(values)


def create_missing_ts_features_ts2(values: List[Optional[float]]) -> List[int]:
    return create_missing_ts_features_ts(values)


def create_time_ts_features_ts2(timestamps: List[int]) -> List[Dict[str, int]]:
    return create_time_ts_features_ts(timestamps)


def create_frequency_ts_features_ts2(series: List[float]) -> Dict[str, float]:
    return create_frequency_ts_features_ts(series)


def create_entropy_ts_features_ts2(series: List[float]) -> Dict[str, float]:
    return create_entropy_ts_features_ts(series)


def create_complexity_ts_features_ts2(series: List[float]) -> Dict[str, float]:
    return create_complexity_ts_features_ts(series)


def create_statistical_ts_features_ts2(series: List[float]) -> Dict[str, float]:
    return create_statistical_ts_features_ts(series)


def create_all_ts_features_ts2(series: List[float]) -> Dict[str, Any]:
    return create_all_ts_features_ts(series)


def flatten_ts_features_ts2(features: Dict[str, Any]) -> List[float]:
    return flatten_ts_features_ts(features)


def feature_vector_ts3(series: List[float]) -> List[float]:
    return feature_vector_ts2(series)


def batch_feature_vectors_ts3(series_list: List[List[float]]) -> List[List[float]]:
    return batch_feature_vectors_ts2(series_list)


def save_feature_vectors_ts3(path: str, vectors: List[List[float]]) -> None:
    save_feature_vectors_ts2(path, vectors)


def load_feature_vectors_ts3(path: str) -> List[List[float]]:
    return load_feature_vectors_ts2(path)


def normalize_feature_vectors_ts3(vectors: List[List[float]]) -> List[List[float]]:
    return normalize_feature_vectors_ts2(vectors)


def scale_feature_vectors_ts3(vectors: List[List[float]], method: str = "standard") -> List[List[float]]:
    return scale_feature_vectors_ts2(vectors, method=method)


def reduce_feature_vectors_ts3(vectors: List[List[float]], n_components: int = 2) -> List[List[float]]:
    return reduce_feature_vectors_ts2(vectors, n_components=n_components)


def cluster_feature_vectors_ts3(vectors: List[List[float]], n_clusters: int = 3) -> List[int]:
    return cluster_feature_vectors_ts2(vectors, n_clusters=n_clusters)


def detect_anomalies_ts3(vectors: List[List[float]]) -> List[int]:
    return detect_anomalies_ts2(vectors)


def compute_similarity_matrix_ts3(vectors: List[List[float]]) -> List[List[float]]:
    return compute_similarity_matrix_ts2(vectors)


def find_nearest_neighbors_ts3(vectors: List[List[float]], query: List[float], k: int = 5) -> List[int]:
    return find_nearest_neighbors_ts2(vectors, query, k=k)


def compute_distance_matrix_ts3(vectors: List[List[float]]) -> List[List[float]]:
    return compute_distance_matrix_ts2(vectors)


def create_ts_dataset_ts2(series: List[float], window: int = 5, horizon: int = 1):
    return create_ts_dataset_ts(series, window=window, horizon=horizon)


def train_ts_model_ts2(X, y, model_type: str = "linear"):
    return train_ts_model_ts(X, y, model_type=model_type)


def forecast_ts_ts2(model, last_window: List[float], steps: int = 5) -> List[float]:
    return forecast_ts_ts(model, last_window, steps=steps)


def evaluate_ts_ts2(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    return evaluate_ts_ts(actual, predicted)


def backtest_ts_ts2(series: List[float], window: int = 5) -> Dict[str, Any]:
    return backtest_ts_ts(series, window=window)


def cross_validate_ts_ts2(series: List[float], window: int = 5, k: int = 5) -> List[float]:
    return cross_validate_ts_ts(series, window=window, k=k)


def grid_search_ts_ts2(series: List[float], window: int = 5) -> Dict[str, Any]:
    return grid_search_ts_ts(series, window=window)


def ensemble_forecast_ts3(series: List[float], steps: int = 5) -> List[float]:
    return ensemble_forecast_ts2(series, steps=steps)


def weighted_forecast_ts3(series: List[float], steps: int = 5) -> List[float]:
    return weighted_forecast_ts2(series, steps=steps)


def stacking_forecast_ts3(series: List[float], steps: int = 5) -> List[float]:
    return stacking_forecast_ts2(series, steps=steps)


def blending_forecast_ts3(series: List[float], steps: int = 5) -> List[float]:
    return blending_forecast_ts2(series, steps=steps)


def create_forecast_report_ts3(series: List[float], steps: int = 5) -> Dict[str, Any]:
    return create_forecast_report_ts2(series, steps=steps)


def save_forecast_report_ts3(path: str, report: Dict[str, Any]) -> None:
    save_forecast_report_ts2(path, report)


def load_forecast_report_ts3(path: str) -> Dict[str, Any]:
    return load_forecast_report_ts2(path)


def format_forecast_report_ts3(report: Dict[str, Any]) -> str:
    return format_forecast_report_ts2(report)


def export_forecast_csv_ts3(path: str, report: Dict[str, Any]) -> None:
    export_forecast_csv_ts2(path, report)


def import_forecast_csv_ts3(path: str) -> Dict[str, Any]:
    return import_forecast_csv_ts2(path)


def validate_series_ts6(series: List[float]) -> bool:
    return validate_series_ts5(series)


def clean_series_ts6(series: List[float]) -> List[float]:
    return clean_series_ts5(series)


def clip_series_ts6(series: List[float], low=None, high=None) -> List[float]:
    return clip_series_ts5(series, low=low, high=high)


def scale_series_ts6(series: List[float], factor: float = 1.0) -> List[float]:
    return scale_series_ts5(series, factor=factor)


def shift_series_ts6(series: List[float], offset: float = 0.0) -> List[float]:
    return shift_series_ts5(series, offset=offset)


def reverse_series_ts6(series: List[float]) -> List[float]:
    return reverse_series_ts5(series)


def sort_series_ts6(series: List[float]) -> List[float]:
    return sort_series_ts5(series)


def unique_series_ts6(series: List[float]) -> List[float]:
    return unique_series_ts5(series)


def dedupe_series_ts6(series: List[float]) -> List[float]:
    return dedupe_series_ts5(series)


def truncate_series_ts6(series: List[float], n: int) -> List[float]:
    return truncate_series_ts5(series, n)


def pad_series_ts6(series: List[float], n: int, value: float = 0.0) -> List[float]:
    return pad_series_ts5(series, n, value=value)


def concat_series_ts6(*series: List[float]) -> List[float]:
    return concat_series_ts5(*series)


def split_series_ts6(series: List[float], n: int) -> List[List[float]]:
    return split_series_ts5(series, n)


def window_series_ts6(series: List[float], window: int, step: int = 1) -> List[List[float]]:
    return window_series_ts5(series, window, step)


def aggregate_series_ts6(series: List[float], func: str = "mean", window: int = 5) -> List[float]:
    return aggregate_series_ts5(series, func=func, window=window)


def acf_series_ts4(series: List[float]) -> List[float]:
    return acf_series_ts3(series)


def pacf_series_ts4(series: List[float]) -> List[float]:
    return pacf_series_ts3(series)


def fft_series_ts4(series: List[float]) -> Tuple[List[float], List[float]]:
    return fft_series_ts3(series)


def psd_series_ts4(series: List[float]) -> Tuple[List[float], List[float]]:
    return psd_series_ts3(series)


def spectrogram_series_ts4(series: List[float]) -> Tuple[List, List, List]:
    return spectrogram_series_ts3(series)


def arima_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return arima_series_ts3(series, steps=steps)


def sarima_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return sarima_series_ts3(series, steps=steps)


def prophet_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return prophet_series_ts3(series, steps=steps)


def ets_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return ets_series_ts3(series, steps=steps)


def theta_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return theta_series_ts3(series, steps=steps)


def naive_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return naive_series_ts3(series, steps=steps)


def seasonal_naive_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return seasonal_naive_series_ts3(series, steps=steps)


def drift_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return drift_series_ts3(series, steps=steps)


def mean_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return mean_series_ts3(series, steps=steps)


def median_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return median_series_ts3(series, steps=steps)


def random_walk_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return random_walk_series_ts3(series, steps=steps)


def monte_carlo_series_ts4(series: List[float], steps: int = 5) -> List[float]:
    return monte_carlo_series_ts3(series, steps=steps)


def forecast_intervals_series_ts4(series: List[float], steps: int = 5) -> Dict[str, List[float]]:
    return forecast_intervals_series_ts3(series, steps=steps)


def evaluate_series_ts4(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    return evaluate_series_ts3(actual, predicted)


def mase_series_ts4(actual: List[float], predicted: List[float], train: List[float]) -> float:
    return mase_series_ts3(actual, predicted, train)


def smape_series_ts4(actual: List[float], predicted: List[float]) -> float:
    return smape_series_ts3(actual, predicted)


def mape_series_ts4(actual: List[float], predicted: List[float]) -> float:
    return mape_series_ts3(actual, predicted)


def rmse_series_ts4(actual: List[float], predicted: List[float]) -> float:
    return rmse_series_ts3(actual, predicted)


def mae_series_ts4(actual: List[float], predicted: List[float]) -> float:
    return mae_series_ts3(actual, predicted)


def r2_series_ts4(actual: List[float], predicted: List[float]) -> float:
    return r2_series_ts3(actual, predicted)


def theil_u_series_ts4(actual: List[float], predicted: List[float]) -> float:
    return theil_u_series_ts3(actual, predicted)


def track_sn_series_ts4(series: List[float]) -> Dict[str, float]:
    return track_sn_series_ts3(series)


def boxcox_series_ts4(series: List[float]) -> Tuple[List[float], float]:
    return boxcox_series_ts3(series)


def yeo_johnson_series_ts4(series: List[float]) -> Tuple[List[float], float]:
    return yeo_johnson_series_ts3(series)


def validate_series_ts7(series: List[float]) -> bool:
    return validate_series_ts6(series)


def clean_series_ts7(series: List[float]) -> List[float]:
    return clean_series_ts6(series)


def clip_series_ts7(series: List[float], low=None, high=None) -> List[float]:
    return clip_series_ts6(series, low=low, high=high)


def scale_series_ts7(series: List[float], factor: float = 1.0) -> List[float]:
    return scale_series_ts6(series, factor=factor)


def shift_series_ts7(series: List[float], offset: float = 0.0) -> List[float]:
    return shift_series_ts6(series, offset=offset)


def reverse_series_ts7(series: List[float]) -> List[float]:
    return reverse_series_ts6(series)


def sort_series_ts7(series: List[float]) -> List[float]:
    return sort_series_ts6(series)


def unique_series_ts7(series: List[float]) -> List[float]:
    return unique_series_ts6(series)


def dedupe_series_ts7(series: List[float]) -> List[float]:
    return dedupe_series_ts6(series)


def truncate_series_ts7(series: List[float], n: int) -> List[float]:
    return truncate_series_ts6(series, n)


def pad_series_ts7(series: List[float], n: int, value: float = 0.0) -> List[float]:
    return pad_series_ts6(series, n, value=value)


def concat_series_ts7(*series: List[float]) -> List[float]:
    return concat_series_ts6(*series)


def split_series_ts7(series: List[float], n: int) -> List[List[float]]:
    return split_series_ts6(series, n)


def window_series_ts7(series: List[float], window: int, step: int = 1) -> List[List[float]]:
    return window_series_ts6(series, window, step)


def aggregate_series_ts7(series: List[float], func: str = "mean", window: int = 5) -> List[float]:
    return aggregate_series_ts6(series, func=func, window=window)


def main():
    print("time_series module loaded")


if __name__ == "__main__":
    main()
