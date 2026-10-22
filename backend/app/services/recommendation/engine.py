"""Recommendation engine for songs and model suggestions."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class SongProfile:
    id: str
    features: List[float]
    label: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    id: str
    history: List[str] = field(default_factory=list)
    preferences: Dict[str, float] = field(default_factory=dict)


class SimilarityCalculator:
    @staticmethod
    def cosine(a: List[float], b: List[float]) -> float:
        va = np.asarray(a, dtype=float)
        vb = np.asarray(b, dtype=float)
        denom = np.linalg.norm(va) * np.linalg.norm(vb)
        if denom == 0:
            return 0.0
        return float(np.dot(va, vb) / denom)

    @staticmethod
    def euclidean(a: List[float], b: List[float]) -> float:
        return float(np.linalg.norm(np.asarray(a) - np.asarray(b)))

    @staticmethod
    def manhattan(a: List[float], b: List[float]) -> float:
        return float(np.sum(np.abs(np.asarray(a) - np.asarray(b))))

    @staticmethod
    def pearson(a: List[float], b: List[float]) -> float:
        va = np.asarray(a, dtype=float)
        vb = np.asarray(b, dtype=float)
        va = va - va.mean()
        vb = vb - vb.mean()
        denom = np.linalg.norm(va) * np.linalg.norm(vb)
        if denom == 0:
            return 0.0
        return float(np.dot(va, vb) / denom)


class ContentBasedRecommender:
    def __init__(self, songs: List[SongProfile]) -> None:
        self.songs = {s.id: s for s in songs}
        self._index: Dict[str, List[Tuple[str, float]]] = {}

    def fit(self) -> None:
        ids = list(self.songs.keys())
        for i, sid in enumerate(ids):
            sims = []
            for oid in ids:
                if oid == sid:
                    continue
                sim = SimilarityCalculator.cosine(self.songs[sid].features, self.songs[oid].features)
                sims.append((oid, sim))
            sims.sort(key=lambda x: x[1], reverse=True)
            self._index[sid] = sims

    def recommend(self, song_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if song_id not in self._index:
            self.fit()
        return self._index.get(song_id, [])[:top_k]

    def recommend_for_features(self, features: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        sims = []
        for sid, song in self.songs.items():
            sim = SimilarityCalculator.cosine(features, song.features)
            sims.append((sid, sim))
        sims.sort(key=lambda x: x[1], reverse=True)
        return sims[:top_k]


class CollaborativeFilteringRecommender:
    def __init__(self) -> None:
        self.user_item: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.item_users: Dict[str, set] = defaultdict(set)

    def add_interaction(self, user_id: str, item_id: str, rating: float) -> None:
        self.user_item[user_id][item_id] = rating
        self.item_users[item_id].add(user_id)

    def user_similarity(self, u1: str, u2: str) -> float:
        items1 = set(self.user_item[u1].keys())
        items2 = set(self.user_item[u2].keys())
        common = items1 & items2
        if not common:
            return 0.0
        v1 = np.array([self.user_item[u1][i] for i in common])
        v2 = np.array([self.user_item[u2][i] for i in common])
        return SimilarityCalculator.cosine(v1.tolist(), v2.tolist())

    def recommend(self, user_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if user_id not in self.user_item:
            return []
        scores: Dict[str, float] = defaultdict(float)
        sim_sums: Dict[str, float] = defaultdict(float)
        for other, items in self.user_item.items():
            if other == user_id:
                continue
            sim = self.user_similarity(user_id, other)
            if sim <= 0:
                continue
            for item, rating in items.items():
                if item in self.user_item[user_id]:
                    continue
                scores[item] += sim * rating
                sim_sums[item] += sim
        ranked = []
        for item, score in scores.items():
            denom = sim_sums[item] if sim_sums[item] > 0 else 1.0
            ranked.append((item, score / denom))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


class HybridRecommender:
    def __init__(self, content: ContentBasedRecommender, collab: CollaborativeFilteringRecommender, alpha: float = 0.5) -> None:
        self.content = content
        self.collab = collab
        self.alpha = alpha

    def recommend(self, user_id: str, seed_song_id: Optional[str] = None, top_k: int = 5) -> List[Tuple[str, float]]:
        content_scores: Dict[str, float] = {}
        if seed_song_id is not None:
            for sid, sim in self.content.recommend(seed_song_id, top_k=top_k * 2):
                content_scores[sid] = sim
        collab_scores: Dict[str, float] = {}
        for sid, score in self.collab.recommend(user_id, top_k=top_k * 2):
            collab_scores[sid] = score

        all_items = set(content_scores) | set(collab_scores)
        combined = []
        for item in all_items:
            cs = content_scores.get(item, 0.0)
            ls = collab_scores.get(item, 0.0)
            combined.append((item, self.alpha * cs + (1 - self.alpha) * ls))
        combined.sort(key=lambda x: x[1], reverse=True)
        return combined[:top_k]


class PopularityRecommender:
    def __init__(self) -> None:
        self.counts: Dict[str, int] = defaultdict(int)
        self.ratings: Dict[str, List[float]] = defaultdict(list)

    def record(self, item_id: str, rating: float = 1.0) -> None:
        self.counts[item_id] += 1
        self.ratings[item_id].append(rating)

    def top(self, k: int = 10, min_count: int = 1) -> List[Tuple[str, float]]:
        scored = []
        for item, cnt in self.counts.items():
            if cnt < min_count:
                continue
            avg = sum(self.ratings[item]) / len(self.ratings[item])
            score = avg * math.log1p(cnt)
            scored.append((item, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]


class ABTestManager:
    def __init__(self) -> None:
        self.experiments: Dict[str, Dict[str, Any]] = {}
        self.assignments: Dict[str, Dict[str, str]] = defaultdict(dict)

    def create_experiment(self, name: str, variants: List[str], traffic_split: Optional[List[float]] = None) -> None:
        if traffic_split is None:
            traffic_split = [1.0 / len(variants)] * len(variants)
        self.experiments[name] = {"variants": variants, "split": traffic_split, "results": {v: {"impressions": 0, "conversions": 0} for v in variants}}

    def assign(self, experiment: str, user_id: str) -> str:
        if experiment not in self.experiments:
            raise ValueError("Unknown experiment")
        if user_id in self.assignments[experiment]:
            return self.assignments[experiment][user_id]
        exp = self.experiments[experiment]
        r = random.random()
        cumulative = 0.0
        chosen = exp["variants"][-1]
        for v, s in zip(exp["variants"], exp["split"]):
            cumulative += s
            if r < cumulative:
                chosen = v
                break
        self.assignments[experiment][user_id] = chosen
        return chosen

    def record_impression(self, experiment: str, variant: str) -> None:
        if experiment in self.experiments and variant in self.experiments[experiment]["results"]:
            self.experiments[experiment]["results"][variant]["impressions"] += 1

    def record_conversion(self, experiment: str, variant: str) -> None:
        if experiment in self.experiments and variant in self.experiments[experiment]["results"]:
            self.experiments[experiment]["results"][variant]["conversions"] += 1

    def results(self, experiment: str) -> Dict[str, Any]:
        if experiment not in self.experiments:
            raise ValueError("Unknown experiment")
        out = {}
        for v, r in self.experiments[experiment]["results"].items():
            imp = r["impressions"]
            conv = r["conversions"]
            rate = conv / imp if imp > 0 else 0.0
            out[v] = {"impressions": imp, "conversions": conv, "conversion_rate": rate}
        return out

    def winner(self, experiment: str) -> Optional[str]:
        res = self.results(experiment)
        if not res:
            return None
        return max(res, key=lambda v: res[v]["conversion_rate"])


class FeatureStore:
    def __init__(self) -> None:
        self._features: Dict[str, Dict[str, Any]] = {}

    def set(self, entity_id: str, features: Dict[str, Any]) -> None:
        self._features[entity_id] = dict(features)

    def get(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self._features.get(entity_id)

    def update(self, entity_id: str, updates: Dict[str, Any]) -> None:
        if entity_id not in self._features:
            self._features[entity_id] = {}
        self._features[entity_id].update(updates)

    def delete(self, entity_id: str) -> bool:
        return self._features.pop(entity_id, None) is not None

    def list_entities(self) -> List[str]:
        return list(self._features.keys())

    def query(self, predicate: Callable[[Dict[str, Any]], bool]) -> List[str]:
        return [eid for eid, f in self._features.items() if predicate(f)]


_recommender_instance: Optional[ContentBasedRecommender] = None


def get_recommendation_engine(songs: Optional[List[SongProfile]] = None) -> ContentBasedRecommender:
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = ContentBasedRecommender(songs or [])
        _recommender_instance.fit()
    return _recommender_instance
