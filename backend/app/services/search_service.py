"""Full-text-ish search helpers for predictions and users."""

from __future__ import annotations

from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app import models


def search_predictions(db: Session, user_id: int, query: str, limit: int = 50) -> List[models.PredictionHistory]:
    q = db.query(models.PredictionHistory).filter(models.PredictionHistory.user_id == user_id)
    if query:
        like = f"%{query}%"
        q = q.filter(
            or_(
                models.PredictionHistory.file_name.ilike(like),
            )
        )
    return q.order_by(models.PredictionHistory.id.desc()).limit(limit).all()


def search_users(db: Session, query: str, limit: int = 50) -> List[models.User]:
    if not query:
        return []
    like = f"%{query}%"
    return (
        db.query(models.User)
        .filter(or_(models.User.username.ilike(like), models.User.email.ilike(like)))
        .order_by(models.User.id)
        .limit(limit)
        .all()
    )


class SearchIndex:
    """Simple in-memory inverted index for quick lookups."""

    def __init__(self) -> None:
        self._index: dict = {}

    def add(self, doc_id: str, text: str) -> None:
        tokens = set(text.lower().split())
        for tok in tokens:
            self._index.setdefault(tok, set()).add(doc_id)

    def search(self, query: str) -> set:
        tokens = query.lower().split()
        if not tokens:
            return set()
        result = self._index.get(tokens[0], set()).copy()
        for tok in tokens[1:]:
            result &= self._index.get(tok, set())
        return result

    def remove(self, doc_id: str) -> None:
        for tok in list(self._index.keys()):
            self._index[tok].discard(doc_id)
            if not self._index[tok]:
                del self._index[tok]

    def clear(self) -> None:
        self._index.clear()
