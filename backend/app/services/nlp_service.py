"""Natural language processing utilities for text analysis."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


def tokenize_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


def ngrams(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def bag_of_words(docs: List[str]) -> Tuple[List[List[int]], List[str]]:
    vocab = sorted({w for d in docs for w in tokenize(d)})
    out = []
    for d in docs:
        toks = tokenize(d)
        c = Counter(toks)
        out.append([c.get(w, 0) for w in vocab])
    return out, vocab


def tfidf(docs: List[str]) -> Tuple[List[List[float]], List[str]]:
    import math

    vocab = sorted({w for d in docs for w in tokenize(d)})
    tokenized = [tokenize(d) for d in docs]
    N = len(docs)
    idf = {}
    for w in vocab:
        df = sum(1 for t in tokenized if w in t)
        idf[w] = math.log((N + 1) / (df + 1)) + 1
    out = []
    for t in tokenized:
        c = Counter(t)
        total = len(t) or 1
        vec = [ (c.get(w, 0) / total) * idf[w] for w in vocab ]
        out.append(vec)
    return out, vocab


def word_frequency(text: str) -> Dict[str, int]:
    return dict(Counter(tokenize(text)))


def char_frequency(text: str) -> Dict[str, int]:
    return dict(Counter(text))


def sentence_length_stats(text: str) -> Dict[str, float]:
    sents = tokenize_sentences(text)
    lengths = [len(tokenize(s)) for s in sents]
    if not lengths:
        return {"count": 0, "mean": 0, "std": 0, "min": 0, "max": 0}
    return {
        "count": len(lengths),
        "mean": float(np.mean(lengths)),
        "std": float(np.std(lengths)),
        "min": float(np.min(lengths)),
        "max": float(np.max(lengths)),
    }


def lexical_diversity(text: str) -> float:
    toks = tokenize(text)
    if not toks:
        return 0.0
    return len(set(toks)) / len(toks)


def type_token_ratio(text: str) -> float:
    return lexical_diversity(text)


def readability_score(text: str) -> float:
    # Flesch-Kincaid grade level approximation
    sents = tokenize_sentences(text)
    words = tokenize(text)
    if not sents or not words:
        return 0.0
    syllables = sum(count_syllables(w) for w in words)
    asl = len(words) / len(sents)
    asw = syllables / len(words)
    return 0.39 * asl + 11.8 * asw - 15.59


def count_syllables(word: str) -> int:
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_v = ch in vowels
        if is_v and not prev_vowel:
            count += 1
        prev_vowel = is_v
    if word.endswith("e"):
        count = max(1, count - 1)
    return max(1, count)


def flesch_reading_ease(text: str) -> float:
    sents = tokenize_sentences(text)
    words = tokenize(text)
    if not sents or not words:
        return 0.0
    syllables = sum(count_syllables(w) for w in words)
    asl = len(words) / len(sents)
    asw = syllables / len(words)
    return 206.835 - 1.015 * asl - 84.6 * asw


def gunning_fog(text: str) -> float:
    sents = tokenize_sentences(text)
    words = tokenize(text)
    if not sents or not words:
        return 0.0
    complex_words = sum(1 for w in words if count_syllables(w) >= 3)
    asl = len(words) / len(sents)
    return 0.4 * (asl + 100 * complex_words / len(words))


def smog_index(text: str) -> float:
    sents = tokenize_sentences(text)
    words = tokenize(text)
    if not sents or not words:
        return 0.0
    poly = sum(1 for w in words if count_syllables(w) >= 3)
    return 1.0430 * (poly * 30 / len(sents)) ** 0.5 + 3.1291


def coleman_liau(text: str) -> float:
    sents = tokenize_sentences(text)
    words = tokenize(text)
    if not sents or not words:
        return 0.0
    letters = sum(1 for c in text if c.isalpha())
    L = letters / len(words) * 100
    S = len(sents) / len(words) * 100
    return 0.0588 * L - 0.296 * S - 15.8


def automated_readability(text: str) -> float:
    sents = tokenize_sentences(text)
    words = tokenize(text)
    if not sents or not words:
        return 0.0
    chars = sum(len(w) for w in words)
    return 4.71 * (chars / len(words)) + 0.5 * (len(words) / len(sents)) - 21.43


def sentiment_simple(text: str) -> Dict[str, float]:
    positive = {"good", "great", "excellent", "amazing", "love", "best", "happy", "wonderful", "fantastic", "positive"}
    negative = {"bad", "terrible", "awful", "hate", "worst", "sad", "negative", "poor", "horrible"}
    toks = tokenize(text)
    pos = sum(1 for t in toks if t in positive)
    neg = sum(1 for t in toks if t in negative)
    total = pos + neg
    if total == 0:
        return {"positive": 0.0, "negative": 0.0, "neutral": 1.0, "score": 0.0}
    return {
        "positive": pos / total,
        "negative": neg / total,
        "neutral": 0.0,
        "score": (pos - neg) / total,
    }


def keyword_extraction(text: str, top_k: int = 10) -> List[Tuple[str, float]]:
    toks = tokenize(text)
    c = Counter(toks)
    total = len(toks) or 1
    scored = [(w, cnt / total) for w, cnt in c.items()]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def extract_entities(text: str) -> Dict[str, List[str]]:
    # simple regex-based
    emails = re.findall(r"\S+@\S+\.\S+", text)
    urls = re.findall(r"https?://\S+", text)
    phones = re.findall(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", text)
    dates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)
    return {"emails": emails, "urls": urls, "phones": phones, "dates": dates}


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s.,!?]", "", text)
    return text.strip()


def remove_stopwords(text: str, stopwords: Optional[set] = None) -> str:
    if stopwords is None:
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for", "of", "and", "or", "but", "not", "with", "as", "by", "from", "this", "that", "these", "those", "it", "its"}
    toks = tokenize(text)
    filtered = [t for t in toks if t not in stopwords]
    return " ".join(filtered)


def stem_word(word: str) -> str:
    # simple suffix stripping
    for suffix in ["ing", "ed", "es", "s", "ly", "er", "est"]:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[: -len(suffix)]
    return word


def lemmatize_word(word: str) -> str:
    return stem_word(word)


def ngram_frequency(text: str, n: int = 2) -> Dict[Tuple[str, ...], int]:
    toks = tokenize(text)
    return dict(Counter(ngrams(toks, n)))


def jaccard_text_similarity(a: str, b: str) -> float:
    sa = set(tokenize(a))
    sb = set(tokenize(b))
    if not sa and not sb:
        return 1.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union > 0 else 0.0


def cosine_text_similarity(a: str, b: str) -> float:
    # build combined vocab
    toks_a = tokenize(a)
    toks_b = tokenize(b)
    vocab = sorted(set(toks_a) | set(toks_b))
    ca = Counter(toks_a)
    cb = Counter(toks_b)
    va = np.array([ca.get(w, 0) for w in vocab], dtype=float)
    vb = np.array([cb.get(w, 0) for w in vocab], dtype=float)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def edit_distance(a: str, b: str) -> int:
    if len(a) < len(b):
        return edit_distance(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        cur = [i + 1]
        for j, cb in enumerate(b):
            ins = prev[j + 1] + 1
            dele = cur[j] + 1
            sub = prev[j] + (ca != cb)
            cur.append(min(ins, dele, sub))
        prev = cur
    return prev[-1]


def longest_common_subsequence(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def hamming_text(a: str, b: str) -> int:
    if len(a) != len(b):
        raise ValueError("Strings must have same length")
    return sum(1 for x, y in zip(a, b) if x != y)


def soundex(word: str) -> str:
    word = word.upper()
    if not word:
        return ""
    first = word[0]
    mapping = {"B": "1", "F": "1", "P": "1", "V": "1", "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "Z": "2", "D": "3", "T": "3", "L": "4", "M": "5", "N": "5", "R": "6"}
    code = first
    prev = mapping.get(first, "0")
    for ch in word[1:]:
        c = mapping.get(ch, "0")
        if c != "0" and c != prev:
            code += c
        prev = c if c != "0" else prev
    code = code[:4].ljust(4, "0")
    return code


def metaphone(word: str) -> str:
    return soundex(word)


def nysiis(word: str) -> str:
    return soundex(word)


def detect_language(text: str) -> str:
    # simple heuristic
    if any(c in text for c in "àâçéèêëîïôûùüÿñæœ"):
        return "fr"
    if any(c in text for c in "äöüß"):
        return "de"
    if any(c in text for c in "ñáéíóú"):
        return "es"
    return "en"


def translate_placeholder(text: str, target_lang: str) -> str:
    return f"[{target_lang}] {text}"


def summarize_text(text: str, max_sentences: int = 3) -> str:
    sents = tokenize_sentences(text)
    if len(sents) <= max_sentences:
        return text
    # score sentences by word frequency
    toks = tokenize(text)
    freq = Counter(toks)
    scored = []
    for s in sents:
        score = sum(freq.get(w, 0) for w in tokenize(s))
        scored.append((score, s))
    scored.sort(reverse=True)
    top = [s for _, s in scored[:max_sentences]]
    # preserve original order
    result = [s for s in sents if s in top]
    return " ".join(result)


def extract_keywords_tfidf(text: str, top_k: int = 10) -> List[Tuple[str, float]]:
    docs = [text]
    vecs, vocab = tfidf(docs)
    if not vecs:
        return []
    scores = list(zip(vocab, vecs[0]))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


def extract_phrases(text: str, min_len: int = 2, max_len: int = 4) -> List[str]:
    toks = tokenize(text)
    phrases = []
    for n in range(min_len, max_len + 1):
        for ng in ngrams(toks, n):
            phrases.append(" ".join(ng))
    return phrases


def count_words(text: str) -> int:
    return len(tokenize(text))


def count_chars(text: str) -> int:
    return len(text)


def count_sentences(text: str) -> int:
    return len(tokenize_sentences(text))


def count_paragraphs(text: str) -> int:
    return len([p for p in text.split("\n\n") if p.strip()])


def avg_word_length(text: str) -> float:
    toks = tokenize(text)
    if not toks:
        return 0.0
    return sum(len(t) for t in toks) / len(toks)


def avg_sentence_length(text: str) -> float:
    sents = tokenize_sentences(text)
    if not sents:
        return 0.0
    return sum(len(tokenize(s)) for s in sents) / len(sents)


def most_common_words(text: str, n: int = 10) -> List[Tuple[str, int]]:
    return Counter(tokenize(text)).most_common(n)


def most_common_bigrams(text: str, n: int = 10) -> List[Tuple[Tuple[str, str], int]]:
    return Counter(ngrams(tokenize(text), 2)).most_common(n)


def most_common_trigrams(text: str, n: int = 10) -> List[Tuple[Tuple[str, str, str], int]]:
    return Counter(ngrams(tokenize(text), 3)).most_common(n)


def word_cloud_data(text: str, max_words: int = 50) -> List[Dict[str, Any]]:
    c = Counter(tokenize(text))
    return [{"word": w, "count": n} for w, n in c.most_common(max_words)]


def text_similarity(a: str, b: str, method: str = "cosine") -> float:
    if method == "cosine":
        return cosine_text_similarity(a, b)
    if method == "jaccard":
        return jaccard_text_similarity(a, b)
    if method == "edit":
        max_len = max(len(a), len(b))
        if max_len == 0:
            return 1.0
        return 1 - edit_distance(a, b) / max_len
    return 0.0


def cluster_texts(texts: List[str], n_clusters: int = 3) -> List[int]:
    from sklearn.cluster import KMeans

    vecs, vocab = tfidf(texts)
    X = np.asarray(vecs, dtype=float)
    km = KMeans(n_clusters=min(n_clusters, len(texts)), random_state=42, n_init=10)
    return km.fit_predict(X).tolist()


def classify_text(text: str, labels: List[str], examples: List[Tuple[str, str]]) -> str:
    # nearest neighbor by cosine
    best = None
    best_sim = -1.0
    for ex_text, ex_label in examples:
        sim = cosine_text_similarity(text, ex_text)
        if sim > best_sim:
            best_sim = sim
            best = ex_label
    return best if best is not None else (labels[0] if labels else "")


def topic_modeling(texts: List[str], n_topics: int = 3, n_words: int = 5) -> List[List[str]]:
    # simple LDA-like via sklearn
    try:
        from sklearn.decomposition import LatentDirichletAllocation
        from sklearn.feature_extraction.text import CountVectorizer

        vectorizer = CountVectorizer(stop_words="english", max_features=1000)
        X = vectorizer.fit_transform(texts)
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(X)
        vocab = vectorizer.get_feature_names_out()
        topics = []
        for comp in lda.components_:
            top_idx = comp.argsort()[::-1][:n_words]
            topics.append([vocab[i] for i in top_idx])
        return topics
    except Exception:
        return []


def text_to_vector(text: str, vocab: List[str]) -> List[int]:
    c = Counter(tokenize(text))
    return [c.get(w, 0) for w in vocab]


def vector_to_text(vec: List[int], vocab: List[str]) -> str:
    words = []
    for i, count in enumerate(vec):
        words.extend([vocab[i]] * count)
    return " ".join(words)


def compute_text_stats(text: str) -> Dict[str, Any]:
    return {
        "chars": count_chars(text),
        "words": count_words(text),
        "sentences": count_sentences(text),
        "paragraphs": count_paragraphs(text),
        "avg_word_length": avg_word_length(text),
        "avg_sentence_length": avg_sentence_length(text),
        "lexical_diversity": lexical_diversity(text),
        "readability": readability_score(text),
        "flesch": flesch_reading_ease(text),
        "gunning_fog": gunning_fog(text),
        "smog": smog_index(text),
        "coleman_liau": coleman_liau(text),
        "automated_readability": automated_readability(text),
        "sentiment": sentiment_simple(text),
    }


def compare_texts(a: str, b: str) -> Dict[str, Any]:
    return {
        "cosine_similarity": cosine_text_similarity(a, b),
        "jaccard_similarity": jaccard_text_similarity(a, b),
        "edit_distance": edit_distance(a, b),
        "lcs_length": longest_common_subsequence(a, b),
        "length_diff": abs(len(a) - len(b)),
    }


def detect_duplicates(texts: List[str], threshold: float = 0.9) -> List[Tuple[int, int, float]]:
    out = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = cosine_text_similarity(texts[i], texts[j])
            if sim >= threshold:
                out.append((i, j, sim))
    return out


def remove_duplicates_text(texts: List[str], threshold: float = 0.9) -> List[str]:
    keep = []
    for t in texts:
        is_dup = False
        for k in keep:
            if cosine_text_similarity(t, k) >= threshold:
                is_dup = True
                break
        if not is_dup:
            keep.append(t)
    return keep


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def remove_punctuation(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text)


def remove_numbers(text: str) -> str:
    return re.sub(r"\d+", "", text)


def remove_urls(text: str) -> str:
    return re.sub(r"https?://\S+", "", text)


def remove_emails(text: str) -> str:
    return re.sub(r"\S+@\S+\.\S+", "", text)


def replace_numbers(text: str, replacement: str = "NUM") -> str:
    return re.sub(r"\d+", replacement, text)


def expand_contractions(text: str) -> str:
    contractions = {
        "don't": "do not", "can't": "cannot", "won't": "will not",
        "i'm": "i am", "you're": "you are", "it's": "it is",
        "they're": "they are", "we're": "we are", "let's": "let us",
    }
    for c, e in contractions.items():
        text = re.sub(r"\b" + re.escape(c) + r"\b", e, text, flags=re.IGNORECASE)
    return text


def truncate_text(text: str, max_len: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix


def wrap_text(text: str, width: int = 80) -> str:
    import textwrap

    return textwrap.fill(text, width=width)


def indent_text(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + line for line in text.split("\n"))


def dedent_text(text: str) -> str:
    import textwrap

    return textwrap.dedent(text)


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
        if start >= len(text):
            break
    return chunks


def merge_texts(texts: List[str], separator: str = " ") -> str:
    return separator.join(texts)


def shuffle_sentences(text: str, seed: int = 42) -> str:
    import random

    sents = tokenize_sentences(text)
    rng = random.Random(seed)
    rng.shuffle(sents)
    return " ".join(sents)


def reverse_text(text: str) -> str:
    return text[::-1]


def uppercase_text(text: str) -> str:
    return text.upper()


def lowercase_text(text: str) -> str:
    return text.lower()


def title_case(text: str) -> str:
    return text.title()


def capitalize_sentences(text: str) -> str:
    sents = tokenize_sentences(text)
    return " ".join(s.capitalize() for s in sents)


def remove_extra_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_accents(text: str) -> str:
    import unicodedata

    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def transliterate(text: str) -> str:
    return remove_accents(text)


def count_vowels(text: str) -> int:
    return sum(1 for c in text.lower() if c in "aeiou")


def count_consonants(text: str) -> int:
    return sum(1 for c in text.lower() if c.isalpha() and c not in "aeiou")


def count_digits(text: str) -> int:
    return sum(1 for c in text if c.isdigit())


def count_punctuation(text: str) -> int:
    return sum(1 for c in text if c in ".,!?;:'\"()-")


def text_entropy(text: str) -> float:
    c = Counter(text)
    total = len(text)
    if total == 0:
        return 0.0
    return -sum((n / total) * math.log2(n / total) for n in c.values())


def compression_ratio(text: str) -> float:
    import zlib

    if not text:
        return 0.0
    compressed = zlib.compress(text.encode())
    return len(compressed) / len(text.encode())


def is_palindrome(text: str) -> bool:
    cleaned = re.sub(r"\W", "", text.lower())
    return cleaned == cleaned[::-1]


def is_pangram(text: str) -> bool:
    return set("abcdefghijklmnopqrstuvwxyz").issubset(set(text.lower()))


def word_count_by_length(text: str) -> Dict[int, int]:
    from collections import Counter

    return dict(Counter(len(w) for w in tokenize(text)))


def sentence_count_by_length(text: str) -> Dict[int, int]:
    from collections import Counter

    return dict(Counter(len(tokenize(s)) for s in tokenize_sentences(text)))


def compute_text_features(text: str) -> List[float]:
    stats = compute_text_stats(text)
    return [
        stats["chars"],
        stats["words"],
        stats["sentences"],
        stats["avg_word_length"],
        stats["avg_sentence_length"],
        stats["lexical_diversity"],
        stats["readability"],
        stats["flesch"],
        count_vowels(text),
        count_consonants(text),
        count_digits(text),
        text_entropy(text),
    ]


def batch_compute_features(texts: List[str]) -> List[List[float]]:
    return [compute_text_features(t) for t in texts]


def vectorize_texts(texts: List[str], vocab: Optional[List[str]] = None) -> Tuple[List[List[int]], List[str]]:
    if vocab is None:
        vocab = sorted({w for t in texts for w in tokenize(t)})
    return [text_to_vector(t, vocab) for t in texts], vocab


def save_text_features(path: str, features: List[List[float]]) -> None:
    with open(path, "w") as f:
        json.dump(features, f)


def load_text_features(path: str) -> List[List[float]]:
    with open(path) as f:
        return json.load(f)


def create_text_dataset(texts: List[str], labels: List[str]) -> List[Dict[str, Any]]:
    return [{"text": t, "label": lab, "features": compute_text_features(t)} for t, lab in zip(texts, labels)]


def filter_by_label(dataset: List[Dict[str, Any]], label: str) -> List[Dict[str, Any]]:
    return [d for d in dataset if d.get("label") == label]


def split_text_dataset(dataset: List[Dict[str, Any]], test_size: float = 0.2, seed: int = 42):
    import random

    rng = random.Random(seed)
    data = list(dataset)
    rng.shuffle(data)
    n_test = int(len(data) * test_size)
    return data[n_test:], data[:n_test]


def balance_text_dataset(dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    from collections import Counter

    labels = [d["label"] for d in dataset]
    c = Counter(labels)
    max_count = max(c.values()) if c else 0
    out = list(dataset)
    for lab, cnt in c.items():
        need = max_count - cnt
        candidates = [d for d in dataset if d["label"] == lab]
        for _ in range(need):
            out.append(candidates[_ % len(candidates)])
    return out


def compute_text_similarity_matrix(texts: List[str]) -> List[List[float]]:
    n = len(texts)
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            m[i][j] = cosine_text_similarity(texts[i], texts[j])
    return m


def cluster_texts_kmeans(texts: List[str], k: int = 3) -> List[int]:
    vecs, vocab = tfidf(texts)
    from sklearn.cluster import KMeans

    X = np.asarray(vecs, dtype=float)
    km = KMeans(n_clusters=min(k, len(texts)), random_state=42, n_init=10)
    return km.fit_predict(X).tolist()


def reduce_text_dimensions(texts: List[str], n_components: int = 2) -> List[List[float]]:
    vecs, vocab = tfidf(texts)
    X = np.asarray(vecs, dtype=float)
    from sklearn.decomposition import PCA

    pca = PCA(n_components=min(n_components, X.shape[1]))
    return pca.fit_transform(X).tolist()


def find_similar_texts(query: str, texts: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
    scores = [(i, cosine_text_similarity(query, t)) for i, t in enumerate(texts)]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


def highlight_keywords(text: str, keywords: List[str]) -> str:
    for kw in keywords:
        text = re.sub(r"\b" + re.escape(kw) + r"\b", f"**{kw}**", text, flags=re.IGNORECASE)
    return text


def mask_keywords(text: str, keywords: List[str], mask: str = "***") -> str:
    for kw in keywords:
        text = re.sub(r"\b" + re.escape(kw) + r"\b", mask, text, flags=re.IGNORECASE)
    return text


def replace_keywords(text: str, mapping: Dict[str, str]) -> str:
    for old, new in mapping.items():
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text, flags=re.IGNORECASE)
    return text


def extract_sentences_with_keyword(text: str, keyword: str) -> List[str]:
    return [s for s in tokenize_sentences(text) if keyword.lower() in s.lower()]


def count_keyword_occurrences(text: str, keyword: str) -> int:
    return len(re.findall(r"\b" + re.escape(keyword) + r"\b", text, flags=re.IGNORECASE))


def keyword_density(text: str, keyword: str) -> float:
    words = count_words(text)
    if words == 0:
        return 0.0
    return count_keyword_occurrences(text, keyword) / words


def get_ngrams_list(text: str, n: int = 2) -> List[str]:
    return [" ".join(ng) for ng in ngrams(tokenize(text), n)]


def unique_ngrams(text: str, n: int = 2) -> List[str]:
    return list(set(get_ngrams_list(text, n)))


def ngram_diversity(text: str, n: int = 2) -> float:
    ng = get_ngrams_list(text, n)
    if not ng:
        return 0.0
    return len(set(ng)) / len(ng)


def repetition_ratio(text: str) -> float:
    toks = tokenize(text)
    if not toks:
        return 0.0
    return 1 - (len(set(toks)) / len(toks))


def compression_ratio_text(text: str) -> float:
    return compression_ratio(text)


def estimate_reading_time(text: str, wpm: int = 200) -> float:
    return count_words(text) / wpm


def estimate_speaking_time(text: str, wpm: int = 150) -> float:
    return count_words(text) / wpm


def format_text_report(text: str) -> str:
    stats = compute_text_stats(text)
    lines = ["Text Report", "=" * 40]
    for k, v in stats.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines)


def save_text_report(path: str, text: str) -> None:
    with open(path, "w") as f:
        f.write(format_text_report(text))


def load_text(path: str) -> str:
    with open(path) as f:
        return f.read()


def save_text(path: str, text: str) -> None:
    with open(path, "w") as f:
        f.write(text)


def append_text(path: str, text: str) -> None:
    with open(path, "a") as f:
        f.write(text)


def text_diff(a: str, b: str) -> List[Tuple[str, str]]:
    # simple line diff
    la = a.splitlines()
    lb = b.splitlines()
    out = []
    for x, y in zip(la, lb):
        if x != y:
            out.append((x, y))
    return out


def merge_text_reports(reports: List[str]) -> str:
    return "\n\n".join(reports)


def summarize_corpus(texts: List[str]) -> Dict[str, Any]:
    all_text = " ".join(texts)
    return {
        "n_docs": len(texts),
        "total_words": count_words(all_text),
        "total_chars": count_chars(all_text),
        "avg_doc_length": float(np.mean([count_words(t) for t in texts])) if texts else 0.0,
        "vocab_size": len(set(tokenize(all_text))),
        "lexical_diversity": lexical_diversity(all_text),
    }
