from __future__ import annotations

from backend.app.services.recommendation.engine import (
    ABTestManager,
    CollaborativeFilteringRecommender,
    ContentBasedRecommender,
    FeatureStore,
    PopularityRecommender,
    SongProfile,
)


def test_content_based():
    songs = [
        SongProfile(id="a", features=[1.0, 0.0, 0.5]),
        SongProfile(id="b", features=[0.9, 0.1, 0.4]),
        SongProfile(id="c", features=[0.0, 1.0, 0.0]),
    ]
    rec = ContentBasedRecommender(songs)
    rec.fit()
    res = rec.recommend("a", top_k=1)
    assert res[0][0] == "b"


def test_collaborative():
    cf = CollaborativeFilteringRecommender()
    cf.add_interaction("u1", "i1", 5)
    cf.add_interaction("u1", "i2", 3)
    cf.add_interaction("u2", "i1", 4)
    cf.add_interaction("u2", "i3", 5)
    res = cf.recommend("u1", top_k=2)
    assert any(r[0] == "i3" for r in res)


def test_popularity():
    pop = PopularityRecommender()
    pop.record("i1", 5)
    pop.record("i1", 4)
    pop.record("i2", 3)
    top = pop.top(k=2)
    assert top[0][0] == "i1"


def test_ab_test():
    ab = ABTestManager()
    ab.create_experiment("exp1", ["A", "B"], [0.5, 0.5])
    v = ab.assign("exp1", "user1")
    assert v in {"A", "B"}
    ab.record_impression("exp1", v)
    ab.record_conversion("exp1", v)
    res = ab.results("exp1")
    assert res[v]["impressions"] == 1
    assert ab.winner("exp1") in {"A", "B"}


def test_feature_store():
    fs = FeatureStore()
    fs.set("e1", {"a": 1})
    assert fs.get("e1") == {"a": 1}
    fs.update("e1", {"b": 2})
    assert fs.get("e1") == {"a": 1, "b": 2}
    assert "e1" in fs.query(lambda f: f.get("a") == 1)
    assert fs.delete("e1") is True
