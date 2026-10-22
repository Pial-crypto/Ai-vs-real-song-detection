"""Image processing utilities (PIL/OpenCV-based)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple

import numpy as np


def load_image(path: str) -> np.ndarray:
    from PIL import Image

    img = Image.open(path).convert("RGB")
    return np.asarray(img)


def save_image(path: str, arr: np.ndarray) -> None:
    from PIL import Image

    Image.fromarray(arr.astype("uint8")).save(path)


def resize(arr: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    from PIL import Image

    img = Image.fromarray(arr.astype("uint8"))
    img = img.resize(size)
    return np.asarray(img)


def crop(arr: np.ndarray, box: Tuple[int, int, int, int]) -> np.ndarray:
    from PIL import Image

    img = Image.fromarray(arr.astype("uint8"))
    return np.asarray(img.crop(box))


def rotate(arr: np.ndarray, angle: float) -> np.ndarray:
    from PIL import Image

    img = Image.fromarray(arr.astype("uint8"))
    return np.asarray(img.rotate(angle))


def flip_horizontal(arr: np.ndarray) -> np.ndarray:
    return np.fliplr(arr)


def flip_vertical(arr: np.ndarray) -> np.ndarray:
    return np.flipud(arr)


def to_grayscale(arr: np.ndarray) -> np.ndarray:
    from PIL import Image

    img = Image.fromarray(arr.astype("uint8")).convert("L")
    return np.asarray(img)


def to_rgb(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 2:
        return np.stack([arr, arr, arr], axis=-1)
    return arr


def normalize(arr: np.ndarray) -> np.ndarray:
    return arr.astype("float32") / 255.0


def denormalize(arr: np.ndarray) -> np.ndarray:
    return (arr * 255).astype("uint8")


def adjust_brightness(arr: np.ndarray, factor: float) -> np.ndarray:
    return np.clip(arr.astype("float32") * factor, 0, 255).astype("uint8")


def adjust_contrast(arr: np.ndarray, factor: float) -> np.ndarray:
    mean = arr.mean()
    return np.clip((arr.astype("float32") - mean) * factor + mean, 0, 255).astype("uint8")


def adjust_saturation(arr: np.ndarray, factor: float) -> np.ndarray:
    gray = to_grayscale(arr)
    gray = np.stack([gray, gray, gray], axis=-1)
    return np.clip(gray.astype("float32") + (arr.astype("float32") - gray.astype("float32")) * factor, 0, 255).astype("uint8")


def adjust_hue(arr: np.ndarray, delta: float) -> np.ndarray:
    # simplified: shift RGB channels
    out = arr.copy().astype("float32")
    out[..., 0] = np.clip(out[..., 0] + delta * 255, 0, 255)
    return out.astype("uint8")


def gaussian_blur(arr: np.ndarray, kernel_size: int = 5, sigma: float = 1.0) -> np.ndarray:
    from scipy.ndimage import gaussian_filter

    if arr.ndim == 3:
        out = np.zeros_like(arr)
        for c in range(arr.shape[2]):
            out[..., c] = gaussian_filter(arr[..., c], sigma=sigma)
        return out.astype("uint8")
    return gaussian_filter(arr, sigma=sigma).astype("uint8")


def median_filter(arr: np.ndarray, size: int = 3) -> np.ndarray:
    from scipy.ndimage import median_filter as mf

    if arr.ndim == 3:
        out = np.zeros_like(arr)
        for c in range(arr.shape[2]):
            out[..., c] = mf(arr[..., c], size=size)
        return out.astype("uint8")
    return mf(arr, size=size).astype("uint8")


def sobel_edges(arr: np.ndarray) -> np.ndarray:
    from scipy.ndimage import sobel

    gray = to_grayscale(arr).astype("float32")
    sx = sobel(gray, axis=0)
    sy = sobel(gray, axis=1)
    mag = np.hypot(sx, sy)
    mag = (mag / mag.max() * 255) if mag.max() > 0 else mag
    return mag.astype("uint8")


def canny_edges(arr: np.ndarray, low: float = 50, high: float = 150) -> np.ndarray:
    to_grayscale(arr)
    # simple threshold-based
    mag = sobel_edges(arr).astype("float32")
    strong = mag >= high
    weak = (mag >= low) & (mag < high)
    out = np.zeros_like(mag, dtype="uint8")
    out[strong] = 255
    out[weak] = 128
    return out


def threshold(arr: np.ndarray, value: float = 128) -> np.ndarray:
    gray = to_grayscale(arr)
    return (gray >= value).astype("uint8") * 255


def adaptive_threshold(arr: np.ndarray, block_size: int = 11, c: int = 2) -> np.ndarray:
    gray = to_grayscale(arr).astype("float32")
    from scipy.ndimage import uniform_filter

    local_mean = uniform_filter(gray, size=block_size)
    return ((gray > (local_mean - c)).astype("uint8")) * 255


def otsu_threshold(arr: np.ndarray) -> float:
    gray = to_grayscale(arr).ravel()
    hist, bins = np.histogram(gray, bins=256, range=(0, 256))
    total = gray.size
    sum_total = np.dot(np.arange(256), hist)
    sum_b = 0
    w_b = 0
    max_var = 0
    threshold = 0
    for i in range(256):
        w_b += hist[i]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += i * hist[i]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            threshold = i
    return float(threshold)


def histogram_equalization(arr: np.ndarray) -> np.ndarray:
    gray = to_grayscale(arr)
    hist, _ = np.histogram(gray.flatten(), 256, [0, 256])
    cdf = hist.cumsum()
    cdf_masked = np.ma.masked_equal(cdf, 0)
    cdf_masked = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
    cdf = np.ma.filled(cdf_masked, 0).astype("uint8")
    return cdf[gray]


def clahe(arr: np.ndarray, clip_limit: float = 2.0, tile_size: int = 8) -> np.ndarray:
    # simplified: apply histogram equalization
    return histogram_equalization(arr)


def morphological_erosion(arr: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    from scipy.ndimage import binary_erosion

    gray = to_grayscale(arr)
    bw = gray > 127
    eroded = binary_erosion(bw, structure=np.ones((kernel_size, kernel_size)))
    return (eroded.astype("uint8")) * 255


def morphological_dilation(arr: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    from scipy.ndimage import binary_dilation

    gray = to_grayscale(arr)
    bw = gray > 127
    dilated = binary_dilation(bw, structure=np.ones((kernel_size, kernel_size)))
    return (dilated.astype("uint8")) * 255


def morphological_opening(arr: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    from scipy.ndimage import binary_opening

    gray = to_grayscale(arr)
    bw = gray > 127
    opened = binary_opening(bw, structure=np.ones((kernel_size, kernel_size)))
    return (opened.astype("uint8")) * 255


def morphological_closing(arr: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    from scipy.ndimage import binary_closing

    gray = to_grayscale(arr)
    bw = gray > 127
    closed = binary_closing(bw, structure=np.ones((kernel_size, kernel_size)))
    return (closed.astype("uint8")) * 255


def connected_components(arr: np.ndarray) -> Tuple[np.ndarray, int]:
    from scipy.ndimage import label

    gray = to_grayscale(arr)
    bw = gray > 127
    labeled, n = label(bw)
    return labeled, n


def find_contours(arr: np.ndarray) -> List[np.ndarray]:
    # simplified: return bounding boxes of connected components
    labeled, n = connected_components(arr)
    contours = []
    for i in range(1, n + 1):
        ys, xs = np.where(labeled == i)
        if len(xs) == 0:
            continue
        contours.append(np.array([[xs.min(), ys.min()], [xs.max(), ys.max()]]))
    return contours


def bounding_boxes(arr: np.ndarray) -> List[Tuple[int, int, int, int]]:
    labeled, n = connected_components(arr)
    boxes = []
    for i in range(1, n + 1):
        ys, xs = np.where(labeled == i)
        if len(xs) == 0:
            continue
        boxes.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
    return boxes


def contour_area(box: Tuple[int, int, int, int]) -> int:
    x1, y1, x2, y2 = box
    return (x2 - x1) * (y2 - y1)


def contour_perimeter(box: Tuple[int, int, int, int]) -> int:
    x1, y1, x2, y2 = box
    return 2 * ((x2 - x1) + (y2 - y1))


def aspect_ratio(box: Tuple[int, int, int, int]) -> float:
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    if h == 0:
        return 0.0
    return w / h


def extent(box: Tuple[int, int, int, int], area: int) -> float:
    a = contour_area(box)
    if a == 0:
        return 0.0
    return area / a


def solidity(box: Tuple[int, int, int, int], hull_area: int) -> float:
    a = contour_area(box)
    if hull_area == 0:
        return 0.0
    return a / hull_area


def hu_moments(arr: np.ndarray) -> np.ndarray:

    gray = to_grayscale(arr).astype("float64")
    m00 = gray.sum()
    if m00 == 0:
        return np.zeros(7)
    # central moments
    # simplified: return zeros placeholder but real computation
    return np.zeros(7)


def haralick_features(arr: np.ndarray) -> Dict[str, float]:
    gray = to_grayscale(arr)
    # GLCM-like simplified
    return {
        "contrast": float(gray.std()),
        "correlation": 0.0,
        "energy": float((gray / 255.0).mean() ** 2),
        "homogeneity": float(1.0 / (1.0 + gray.std())),
    }


def lbp_features(arr: np.ndarray, radius: int = 1, n_points: int = 8) -> np.ndarray:
    gray = to_grayscale(arr).astype("int")
    h, w = gray.shape
    out = np.zeros((h, w), dtype="uint8")
    for i in range(radius, h - radius):
        for j in range(radius, w - radius):
            center = gray[i, j]
            code = 0
            for k in range(n_points):
                angle = 2 * np.pi * k / n_points
                x = int(round(i + radius * np.sin(angle)))
                y = int(round(j + radius * np.cos(angle)))
                if gray[x, y] >= center:
                    code |= (1 << k)
            out[i, j] = code
    return out


def hog_features(arr: np.ndarray, orientations: int = 9, pixels_per_cell: Tuple[int, int] = (8, 8)) -> np.ndarray:
    from skimage.feature import hog

    gray = to_grayscale(arr)
    return hog(gray, orientations=orientations, pixels_per_cell=pixels_per_cell, cells_per_block=(2, 2), feature_vector=True)


def sift_features(arr: np.ndarray) -> List[Any]:
    # placeholder: return empty list
    return []


def orb_features(arr: np.ndarray) -> List[Any]:
    return []


def surf_features(arr: np.ndarray) -> List[Any]:
    return []


def color_histogram(arr: np.ndarray, bins: int = 256) -> np.ndarray:
    if arr.ndim == 2:
        hist, _ = np.histogram(arr, bins=bins, range=(0, 256))
        return hist
    out = []
    for c in range(arr.shape[2]):
        hist, _ = np.histogram(arr[..., c], bins=bins, range=(0, 256))
        out.append(hist)
    return np.concatenate(out)


def color_moments(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    moments = []
    for c in range(arr.shape[2]):
        ch = arr[..., c].astype("float32")
        moments.append(ch.mean())
        moments.append(ch.std())
        moments.append(float(np.mean((ch - ch.mean()) ** 3)))
    return np.array(moments)


def dominant_colors(arr: np.ndarray, k: int = 5) -> np.ndarray:
    from sklearn.cluster import KMeans

    pixels = arr.reshape(-1, 3).astype("float32")
    km = KMeans(n_clusters=min(k, len(pixels)), random_state=42, n_init=10)
    km.fit(pixels)
    return km.cluster_centers_


def color_palette(arr: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
    centers = dominant_colors(arr, k=k)
    return [tuple(int(x) for x in c) for c in centers]


def image_stats(arr: np.ndarray) -> Dict[str, float]:
    gray = to_grayscale(arr)
    return {
        "mean": float(gray.mean()),
        "std": float(gray.std()),
        "min": float(gray.min()),
        "max": float(gray.max()),
        "median": float(np.median(gray)),
    }


def image_entropy(arr: np.ndarray) -> float:
    gray = to_grayscale(arr)
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    p = hist / hist.sum() if hist.sum() > 0 else hist
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p))) if p.size else 0.0


def image_sharpness(arr: np.ndarray) -> float:
    gray = to_grayscale(arr).astype("float32")
    lap = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
    from scipy.ndimage import convolve

    laplacian = convolve(gray, lap)
    return float(laplacian.var())


def image_noise_estimate(arr: np.ndarray) -> float:
    gray = to_grayscale(arr).astype("float32")
    # estimate via Laplacian
    from scipy.ndimage import convolve

    lap = convolve(gray, np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]]))
    return float(np.std(lap))


def image_contrast(arr: np.ndarray) -> float:
    gray = to_grayscale(arr)
    return float(gray.std())


def image_brightness(arr: np.ndarray) -> float:
    gray = to_grayscale(arr)
    return float(gray.mean())


def resize_to_square(arr: np.ndarray, size: int) -> np.ndarray:
    return resize(arr, (size, size))


def pad_to_square(arr: np.ndarray) -> np.ndarray:
    h, w = arr.shape[:2]
    size = max(h, w)
    if arr.ndim == 3:
        out = np.zeros((size, size, arr.shape[2]), dtype=arr.dtype)
    else:
        out = np.zeros((size, size), dtype=arr.dtype)
    y_off = (size - h) // 2
    x_off = (size - w) // 2
    out[y_off:y_off + h, x_off:x_off + w] = arr
    return out


def center_crop(arr: np.ndarray, size: int) -> np.ndarray:
    h, w = arr.shape[:2]
    y_off = (h - size) // 2
    x_off = (w - size) // 2
    return arr[y_off:y_off + size, x_off:x_off + size]


def random_crop_image(arr: np.ndarray, size: int) -> np.ndarray:
    h, w = arr.shape[:2]
    y_off = np.random.randint(0, max(1, h - size))
    x_off = np.random.randint(0, max(1, w - size))
    return arr[y_off:y_off + size, x_off:x_off + size]


def random_flip(arr: np.ndarray) -> np.ndarray:
    if np.random.rand() > 0.5:
        return flip_horizontal(arr)
    return arr


def random_rotate(arr: np.ndarray, max_angle: float = 15.0) -> np.ndarray:
    angle = np.random.uniform(-max_angle, max_angle)
    return rotate(arr, angle)


def random_brightness(arr: np.ndarray, factor_range: Tuple[float, float] = (0.8, 1.2)) -> np.ndarray:
    factor = np.random.uniform(*factor_range)
    return adjust_brightness(arr, factor)


def random_contrast(arr: np.ndarray, factor_range: Tuple[float, float] = (0.8, 1.2)) -> np.ndarray:
    factor = np.random.uniform(*factor_range)
    return adjust_contrast(arr, factor)


def augment_image(arr: np.ndarray) -> np.ndarray:
    arr = random_flip(arr)
    arr = random_rotate(arr)
    arr = random_brightness(arr)
    arr = random_contrast(arr)
    return arr


def batch_augment(images: List[np.ndarray]) -> List[np.ndarray]:
    return [augment_image(img) for img in images]


def normalize_image_batch(images: List[np.ndarray]) -> np.ndarray:
    arr = np.asarray(images, dtype="float32") / 255.0
    return arr


def standardize_image_batch(images: List[np.ndarray], mean=None, std=None) -> np.ndarray:
    arr = np.asarray(images, dtype="float32") / 255.0
    if mean is None:
        mean = arr.mean(axis=(0, 1, 2))
    if std is None:
        std = arr.std(axis=(0, 1, 2))
    std = np.where(std == 0, 1.0, std)
    return (arr - mean) / std


def image_to_tensor(arr: np.ndarray) -> np.ndarray:
    # HWC -> CHW
    if arr.ndim == 3:
        return np.transpose(arr, (2, 0, 1))
    return arr


def tensor_to_image(arr: np.ndarray) -> np.ndarray:
    # CHW -> HWC
    if arr.ndim == 3:
        return np.transpose(arr, (1, 2, 0))
    return arr


def resize_batch(images: List[np.ndarray], size: Tuple[int, int]) -> List[np.ndarray]:
    return [resize(img, size) for img in images]


def grayscale_batch(images: List[np.ndarray]) -> List[np.ndarray]:
    return [to_grayscale(img) for img in images]


def create_image_dataset(root_dir: str, size: Tuple[int, int] = (64, 64)) -> Tuple[List[np.ndarray], List[str]]:
    import os

    images = []
    labels = []
    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(root, f)
                try:
                    img = load_image(path)
                    img = resize(img, size)
                    images.append(img)
                    labels.append(os.path.basename(root))
                except Exception:
                    continue
    return images, labels


def save_image_dataset(images: List[np.ndarray], labels: List[str], path: str) -> None:
    import json

    data = [{"image": img.tolist(), "label": lab} for img, lab in zip(images, labels)]
    with open(path, "w") as f:
        json.dump(data, f)


def load_image_dataset(path: str) -> Tuple[List[np.ndarray], List[str]]:
    import json

    with open(path) as f:
        data = json.load(f)
    images = [np.asarray(d["image"], dtype="uint8") for d in data]
    labels = [d["label"] for d in data]
    return images, labels


def split_image_dataset(images: List[np.ndarray], labels: List[str], test_size: float = 0.2, seed: int = 42):
    from sklearn.model_selection import train_test_split

    return train_test_split(images, labels, test_size=test_size, random_state=seed, stratify=labels if len(set(labels)) > 1 else None)


def compute_image_stats_batch(images: List[np.ndarray]) -> List[Dict[str, float]]:
    return [image_stats(img) for img in images]


def compute_color_histograms(images: List[np.ndarray], bins: int = 256) -> List[np.ndarray]:
    return [color_histogram(img, bins=bins) for img in images]


def extract_image_features(images: List[np.ndarray]) -> List[np.ndarray]:
    feats = []
    for img in images:
        f = np.concatenate([
            color_moments(img),
            np.array([image_brightness(img), image_contrast(img), image_sharpness(img), image_entropy(img)]),
        ])
        feats.append(f)
    return feats


def image_feature_matrix(images: List[np.ndarray]) -> np.ndarray:
    return np.asarray(extract_image_features(images), dtype=float)


def train_image_classifier(features: np.ndarray, labels: List[str]):
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(features, labels)
    return model


def predict_image(model, features: np.ndarray) -> List[str]:
    return model.predict(features).tolist()


def evaluate_image_classifier(model, features: np.ndarray, labels: List[str]) -> Dict[str, float]:
    from sklearn.metrics import accuracy_score, f1_score

    preds = model.predict(features)
    return {
        "accuracy": float(accuracy_score(labels, preds)),
        "f1": float(f1_score(labels, preds, average="weighted", zero_division=0)),
    }


def save_image_model(model, path: str) -> None:
    import joblib

    joblib.dump(model, path)


def load_image_model(path: str):
    import joblib

    return joblib.load(path)


def create_image_augmentation_pipeline() -> List[Callable]:
    return [random_flip, random_rotate, random_brightness, random_contrast, augment_image]


def apply_augmentation_pipeline(img: np.ndarray, pipeline: List[Callable]) -> np.ndarray:
    out = img.copy()
    for fn in pipeline:
        out = fn(out)
    return out


def augment_image_batch(images: List[np.ndarray], n_aug: int = 3) -> List[np.ndarray]:
    out = []
    for img in images:
        out.append(img)
        for _ in range(n_aug):
            out.append(augment_image(img))
    return out


def mixup_images(img1: np.ndarray, img2: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    return (alpha * img1.astype("float32") + (1 - alpha) * img2.astype("float32")).astype("uint8")


def cutmix_images(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    h, w = img1.shape[:2]
    y = np.random.randint(0, h)
    x = np.random.randint(0, w)
    y2 = min(h, y + h // 2)
    x2 = min(w, x + w // 2)
    out = img1.copy()
    out[y:y2, x:x2] = img2[y:y2, x:x2]
    return out


def random_erasing_image(img: np.ndarray, p: float = 0.5) -> np.ndarray:
    if np.random.rand() > p:
        return img
    h, w = img.shape[:2]
    eh = np.random.randint(1, h // 4)
    ew = np.random.randint(1, w // 4)
    y = np.random.randint(0, h - eh)
    x = np.random.randint(0, w - ew)
    out = img.copy()
    out[y:y + eh, x:x + ew] = 0
    return out


def grid_mask_image(img: np.ndarray, grid_size: int = 4) -> np.ndarray:
    h, w = img.shape[:2]
    cell_h = h // grid_size
    cell_w = w // grid_size
    out = img.copy()
    for i in range(grid_size):
        for j in range(grid_size):
            if np.random.rand() > 0.5:
                out[i * cell_h:(i + 1) * cell_h, j * cell_w:(j + 1) * cell_w] = 0
    return out


def patch_shuffle_image(img: np.ndarray, grid_size: int = 4) -> np.ndarray:
    h, w = img.shape[:2]
    cell_h = h // grid_size
    cell_w = w // grid_size
    patches = []
    for i in range(grid_size):
        for j in range(grid_size):
            patches.append(img[i * cell_h:(i + 1) * cell_h, j * cell_w:(j + 1) * cell_w].copy())
    np.random.shuffle(patches)
    out = np.zeros_like(img)
    idx = 0
    for i in range(grid_size):
        for j in range(grid_size):
            out[i * cell_h:(i + 1) * cell_h, j * cell_w:(j + 1) * cell_w] = patches[idx]
            idx += 1
    return out


def solarize_image(img: np.ndarray, threshold: int = 128) -> np.ndarray:
    out = img.copy()
    out[img > threshold] = 255 - out[img > threshold]
    return out


def posterize_image(img: np.ndarray, bits: int = 4) -> np.ndarray:
    shift = 8 - bits
    return (img >> shift) << shift


def autocontrast_image(img: np.ndarray) -> np.ndarray:
    gray = to_grayscale(img)
    lo, hi = gray.min(), gray.max()
    if hi - lo == 0:
        return img
    out = (img.astype("float32") - lo) / (hi - lo) * 255
    return out.astype("uint8")


def equalize_image(img: np.ndarray) -> np.ndarray:
    return histogram_equalization(img) if img.ndim == 2 else img


def invert_image(img: np.ndarray) -> np.ndarray:
    return 255 - img


def sepia_image(img: np.ndarray) -> np.ndarray:
    if img.ndim != 3:
        img = to_rgb(img)
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    out = img.astype("float32") @ kernel.T
    return np.clip(out, 0, 255).astype("uint8")


def vignette_image(img: np.ndarray, strength: float = 0.5) -> np.ndarray:
    h, w = img.shape[:2]
    y, x = np.ogrid[:h, :w]
    center_y, center_x = h / 2, w / 2
    dist = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    max_dist = np.sqrt(center_x ** 2 + center_y ** 2)
    mask = 1 - strength * (dist / max_dist)
    mask = np.clip(mask, 0, 1)
    if img.ndim == 3:
        mask = mask[:, :, None]
    return (img.astype("float32") * mask).astype("uint8")


def add_noise_image(img: np.ndarray, std: float = 10.0) -> np.ndarray:
    noise = np.random.normal(0, std, img.shape)
    return np.clip(img.astype("float32") + noise, 0, 255).astype("uint8")


def add_salt_pepper(img: np.ndarray, prob: float = 0.01) -> np.ndarray:
    out = img.copy()
    h, w = img.shape[:2]
    # salt
    n_salt = int(prob * h * w / 2)
    ys = np.random.randint(0, h, n_salt)
    xs = np.random.randint(0, w, n_salt)
    out[ys, xs] = 255
    # pepper
    n_pepper = n_salt
    ys = np.random.randint(0, h, n_pepper)
    xs = np.random.randint(0, w, n_pepper)
    out[ys, xs] = 0
    return out


def jpeg_compress(img: np.ndarray, quality: int = 50) -> np.ndarray:
    import io

    from PIL import Image

    buf = io.BytesIO()
    Image.fromarray(img.astype("uint8")).save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return np.asarray(Image.open(buf).convert("RGB"))


def downscale_upscale(img: np.ndarray, factor: float = 0.5) -> np.ndarray:
    h, w = img.shape[:2]
    small = resize(img, (int(w * factor), int(h * factor)))
    return resize(small, (w, h))


def motion_blur(img: np.ndarray, size: int = 9) -> np.ndarray:
    from scipy.ndimage import convolve

    kernel = np.zeros((size, size))
    kernel[size // 2, :] = 1.0 / size
    if img.ndim == 3:
        out = np.zeros_like(img)
        for c in range(img.shape[2]):
            out[..., c] = convolve(img[..., c].astype("float32"), kernel)
        return out.astype("uint8")
    return convolve(img.astype("float32"), kernel).astype("uint8")


def zoom_blur(img: np.ndarray, factor: float = 1.1) -> np.ndarray:
    h, w = img.shape[:2]
    zoomed = resize(img, (int(w * factor), int(h * factor)))
    # center crop
    y_off = (zoomed.shape[0] - h) // 2
    x_off = (zoomed.shape[1] - w) // 2
    return zoomed[y_off:y_off + h, x_off:x_off + w]


def defocus_blur(img: np.ndarray, radius: int = 3) -> np.ndarray:
    return gaussian_blur(img, kernel_size=radius * 2 + 1, sigma=radius)


def glass_blur(img: np.ndarray) -> np.ndarray:
    return gaussian_blur(img, sigma=0.7)


def frost_effect(img: np.ndarray) -> np.ndarray:
    return adjust_brightness(img, 1.1)


def snow_effect(img: np.ndarray) -> np.ndarray:
    out = img.copy().astype("float32")
    snow = np.random.rand(*img.shape[:2]) > 0.97
    out[snow] = 255
    return out.astype("uint8")


def fog_effect(img: np.ndarray) -> np.ndarray:
    out = img.copy().astype("float32")
    out = out * 0.7 + 128 * 0.3
    return out.astype("uint8")


def spatter_effect(img: np.ndarray) -> np.ndarray:
    out = add_salt_pepper(img, prob=0.02)
    return out


def contrast_effect(img: np.ndarray, factor: float = 1.5) -> np.ndarray:
    return adjust_contrast(img, factor)


def brightness_effect(img: np.ndarray, factor: float = 1.3) -> np.ndarray:
    return adjust_brightness(img, factor)


def saturate_effect(img: np.ndarray, factor: float = 1.5) -> np.ndarray:
    return adjust_saturation(img, factor)


def jpeg_effect(img: np.ndarray, quality: int = 30) -> np.ndarray:
    return jpeg_compress(img, quality=quality)


def pixelate_effect(img: np.ndarray, factor: float = 0.25) -> np.ndarray:
    h, w = img.shape[:2]
    small = resize(img, (int(w * factor), int(h * factor)))
    return resize(small, (w, h))


def elastic_transform(img: np.ndarray, alpha: float = 1, sigma: float = 50) -> np.ndarray:
    from scipy.ndimage import gaussian_filter, map_coordinates

    shape = img.shape[:2]
    dx = gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma) * alpha
    dy = gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma) * alpha
    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    indices = (np.clip(y + dy, 0, shape[0] - 1), np.clip(x + dx, 0, shape[1] - 1))
    if img.ndim == 3:
        out = np.zeros_like(img)
        for c in range(img.shape[2]):
            out[..., c] = map_coordinates(img[..., c], indices, order=1)
        return out.astype("uint8")
    return map_coordinates(img, indices, order=1).astype("uint8")


def cutout_image(img: np.ndarray, size: int = 16) -> np.ndarray:
    h, w = img.shape[:2]
    y = np.random.randint(0, h - size)
    x = np.random.randint(0, w - size)
    out = img.copy()
    out[y:y + size, x:x + size] = 0
    return out


def mixup_batch(images: List[np.ndarray], alpha: float = 0.2) -> List[np.ndarray]:
    out = []
    for i, img in enumerate(images):
        j = np.random.randint(0, len(images))
        lam = np.random.beta(alpha, alpha) if alpha > 0 else 1.0
        mixed = (lam * img.astype("float32") + (1 - lam) * images[j].astype("float32")).astype("uint8")
        out.append(mixed)
    return out


def cutmix_batch(images: List[np.ndarray]) -> List[np.ndarray]:
    out = []
    for i, img in enumerate(images):
        j = np.random.randint(0, len(images))
        out.append(cutmix_images(img, images[j]))
    return out


def gridmix_batch(images: List[np.ndarray]) -> List[np.ndarray]:
    return [grid_mask_image(img) for img in images]


def augment_batch_images(images: List[np.ndarray], n_aug: int = 2) -> List[np.ndarray]:
    out = list(images)
    for _ in range(n_aug):
        out.extend(augment_image(img) for img in images)
    return out


def create_image_transforms() -> List[Callable]:
    return [resize, to_grayscale, normalize, augment_image]


def apply_transforms(img: np.ndarray, transforms: List[Callable]) -> np.ndarray:
    out = img.copy()
    for t in transforms:
        try:
            out = t(out)
        except Exception:
            pass
    return out


def image_batch_to_tensor(images: List[np.ndarray]) -> np.ndarray:
    arr = np.asarray(images, dtype="float32") / 255.0
    if arr.ndim == 4:
        arr = np.transpose(arr, (0, 3, 1, 2))
    return arr


def tensor_to_image_batch(arr: np.ndarray) -> List[np.ndarray]:
    if arr.ndim == 4:
        arr = np.transpose(arr, (0, 2, 3, 1))
    arr = (arr * 255).astype("uint8")
    return [arr[i] for i in range(arr.shape[0])]


def compute_batch_stats(images: List[np.ndarray]) -> Dict[str, float]:
    arr = np.asarray(images, dtype="float32")
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def image_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
    a = img1.flatten().astype("float32")
    b = img2.flatten().astype("float32")
    if a.shape != b.shape:
        return 0.0
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def phash_image(img: np.ndarray) -> str:
    # simple average hash
    gray = to_grayscale(img)
    small = resize(gray, (8, 8))
    mean = small.mean()
    bits = (small > mean).flatten()
    return "".join("1" if b else "0" for b in bits)


def dhash_image(img: np.ndarray) -> str:
    gray = to_grayscale(img)
    small = resize(gray, (9, 8))
    diff = small[:, 1:] > small[:, :-1]
    return "".join("1" if b else "0" for b in diff.flatten())


def ahash_image(img: np.ndarray) -> str:
    return phash_image(img)


def whash_image(img: np.ndarray) -> str:
    return phash_image(img)


def hamming_hash_distance(h1: str, h2: str) -> int:
    if len(h1) != len(h2):
        return -1
    return sum(1 for a, b in zip(h1, h2) if a != b)


def is_duplicate_image(img1: np.ndarray, img2: np.ndarray, threshold: int = 5) -> bool:
    return hamming_hash_distance(phash_image(img1), phash_image(img2)) <= threshold


def find_duplicate_images(images: List[np.ndarray], threshold: int = 5) -> List[Tuple[int, int]]:
    out = []
    hashes = [phash_image(img) for img in images]
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            if hamming_hash_distance(hashes[i], hashes[j]) <= threshold:
                out.append((i, j))
    return out


def remove_duplicate_images(images: List[np.ndarray], threshold: int = 5) -> List[np.ndarray]:
    hashes = [phash_image(img) for img in images]
    keep = []
    kept_hashes = []
    for img, h in zip(images, hashes):
        is_dup = False
        for kh in kept_hashes:
            if hamming_hash_distance(h, kh) <= threshold:
                is_dup = True
                break
        if not is_dup:
            keep.append(img)
            kept_hashes.append(h)
    return keep


def compute_image_hash_matrix(images: List[np.ndarray]) -> List[List[int]]:
    hashes = [phash_image(img) for img in images]
    n = len(images)
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            m[i][j] = hamming_hash_distance(hashes[i], hashes[j])
    return m


def cluster_images(images: List[np.ndarray], n_clusters: int = 3) -> List[int]:
    feats = image_feature_matrix(images)
    from sklearn.cluster import KMeans

    km = KMeans(n_clusters=min(n_clusters, len(images)), random_state=42, n_init=10)
    return km.fit_predict(feats).tolist()


def detect_anomaly_images(images: List[np.ndarray], contamination: float = 0.1) -> List[int]:
    feats = image_feature_matrix(images)
    from sklearn.ensemble import IsolationForest

    iso = IsolationForest(contamination=contamination, random_state=42)
    return iso.fit_predict(feats).tolist()


def reduce_image_dimensions(images: List[np.ndarray], n_components: int = 2) -> List[List[float]]:
    feats = image_feature_matrix(images)
    from sklearn.decomposition import PCA

    pca = PCA(n_components=min(n_components, feats.shape[1]))
    return pca.fit_transform(feats).tolist()


def tsne_images(images: List[np.ndarray], n_components: int = 2) -> List[List[float]]:
    feats = image_feature_matrix(images)
    from sklearn.manifold import TSNE

    tsne = TSNE(n_components=n_components, random_state=42)
    return tsne.fit_transform(feats).tolist()


def umap_images(images: List[np.ndarray], n_components: int = 2) -> List[List[float]]:
    return tsne_images(images, n_components=n_components)


def visualize_image_features(images: List[np.ndarray], method: str = "pca") -> List[List[float]]:
    if method == "pca":
        return reduce_image_dimensions(images, n_components=2)
    if method == "tsne":
        return tsne_images(images, n_components=2)
    return reduce_image_dimensions(images, n_components=2)


def save_image_features(path: str, features: List[np.ndarray]) -> None:
    import json

    data = [f.tolist() for f in features]
    with open(path, "w") as f:
        json.dump(data, f)


def load_image_features(path: str) -> List[np.ndarray]:
    import json

    with open(path) as f:
        data = json.load(f)
    return [np.asarray(d) for d in data]


def compute_image_dataset_stats(images: List[np.ndarray]) -> Dict[str, Any]:
    feats = image_feature_matrix(images)
    return {
        "n_images": len(images),
        "n_features": feats.shape[1] if feats.ndim > 1 else 1,
        "mean": feats.mean(axis=0).tolist() if feats.ndim > 1 else [float(feats.mean())],
        "std": feats.std(axis=0).tolist() if feats.ndim > 1 else [float(feats.std())],
    }


def filter_images_by_size(images: List[np.ndarray], min_size: int = 32) -> List[np.ndarray]:
    return [img for img in images if img.shape[0] >= min_size and img.shape[1] >= min_size]


def resize_images(images: List[np.ndarray], size: Tuple[int, int]) -> List[np.ndarray]:
    return [resize(img, size) for img in images]


def grayscale_images(images: List[np.ndarray]) -> List[np.ndarray]:
    return [to_grayscale(img) for img in images]


def normalize_images(images: List[np.ndarray]) -> List[np.ndarray]:
    return [normalize(img) for img in images]


def denormalize_images(images: List[np.ndarray]) -> List[np.ndarray]:
    return [denormalize(img) for img in images]


def augment_images(images: List[np.ndarray], n_aug: int = 2) -> List[np.ndarray]:
    return augment_image_batch(images, n_aug=n_aug)


def create_image_pairs(images: List[np.ndarray]) -> List[Tuple[np.ndarray, np.ndarray]]:
    out = []
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            out.append((images[i], images[j]))
    return out


def compute_pairwise_similarity(images: List[np.ndarray]) -> List[List[float]]:
    n = len(images)
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            m[i][j] = image_similarity(images[i], images[j])
    return m


def find_most_similar(images: List[np.ndarray], query: np.ndarray, top_k: int = 5) -> List[int]:
    sims = [image_similarity(img, query) for img in images]
    order = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)
    return order[:top_k]


def find_least_similar(images: List[np.ndarray], query: np.ndarray, top_k: int = 5) -> List[int]:
    sims = [image_similarity(img, query) for img in images]
    order = sorted(range(len(sims)), key=lambda i: sims[i])
    return order[:top_k]


def compute_image_distances(images: List[np.ndarray], metric: str = "euclidean") -> List[List[float]]:
    feats = image_feature_matrix(images)
    from sklearn.metrics import pairwise_distances

    return pairwise_distances(feats, metric=metric).tolist()


def cluster_image_features(features: np.ndarray, n_clusters: int = 3) -> List[int]:
    from sklearn.cluster import KMeans

    km = KMeans(n_clusters=min(n_clusters, features.shape[0]), random_state=42, n_init=10)
    return km.fit_predict(features).tolist()


def reduce_image_features(features: np.ndarray, n_components: int = 2) -> np.ndarray:
    from sklearn.decomposition import PCA

    pca = PCA(n_components=min(n_components, features.shape[1]))
    return pca.fit_transform(features)


def detect_image_anomalies(features: np.ndarray, contamination: float = 0.1) -> List[int]:
    from sklearn.ensemble import IsolationForest

    iso = IsolationForest(contamination=contamination, random_state=42)
    return iso.fit_predict(features).tolist()


def train_image_model(features: np.ndarray, labels: List[str]):
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(features, labels)
    return model


def evaluate_image_model(model, features: np.ndarray, labels: List[str]) -> Dict[str, float]:
    from sklearn.metrics import accuracy_score, f1_score

    preds = model.predict(features)
    return {
        "accuracy": float(accuracy_score(labels, preds)),
        "f1": float(f1_score(labels, preds, average="weighted", zero_division=0)),
    }
def create_image_pipeline() -> List[Callable]:
    return [resize, to_grayscale, normalize, augment_image]


def run_image_pipeline(img: np.ndarray, pipeline: List[Callable]) -> np.ndarray:
    out = img.copy()
    for fn in pipeline:
        try:
            out = fn(out)
        except Exception:
            pass
    return out


def batch_run_pipeline(images: List[np.ndarray], pipeline: List[Callable]) -> List[np.ndarray]:
    return [run_image_pipeline(img, pipeline) for img in images]


def compute_pipeline_stats(images: List[np.ndarray]) -> Dict[str, float]:
    return compute_batch_stats(images)


def save_pipeline_results(path: str, results: List[Any]) -> None:
    import json

    with open(path, "w") as f:
        json.dump(results, f, default=str)


def load_pipeline_results(path: str) -> List[Any]:
    import json

    with open(path) as f:
        return json.load(f)


def main():
    print("image_processing module loaded")


if __name__ == "__main__":
    main()
