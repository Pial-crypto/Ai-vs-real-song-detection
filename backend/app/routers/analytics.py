"""Analytics routes."""

from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.crud import count_predictions, get_dashboards, list_users
from backend.app.database import get_db
from backend.app.deps import require_role

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), _admin=Depends(require_role("admin"))):
    users, total_users = list_users(db, skip=0, limit=1)
    total_users = total_users
    total_predictions = count_predictions(db)
    dashboards, total_dashboards = get_dashboards(db, skip=0, limit=1000)
    model_counter: Counter = Counter()
    for d in dashboards:
        if d.model_wise_majority_prediction:
            model_counter[d.model_wise_majority_prediction] += 1
    return {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "total_dashboards": total_dashboards,
        "model_majority_distribution": dict(model_counter),
    }
