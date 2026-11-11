from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from src.config.database import db_session
from src.controllers.auth import current_user, writer
from src.models import DecompositionRun, PeriodComparison, ConsumptionDataset
from src.schemas.run import RunInput
from src.services import runs as service
from src.utils.serialization import serialize

router = APIRouter(prefix="/runs")


def _with_version(db, item):
    payload = serialize(item)
    comparison = db.get(PeriodComparison, item.comparison_id)
    dataset = db.get(ConsumptionDataset, comparison.dataset_id) if comparison else None
    current_version = dataset.current_version if dataset else item.dataset_version
    payload["current_dataset_version"] = current_version
    payload["is_stale"] = item.dataset_version != current_version
    return payload


@router.get("")
def listing(db=Depends(db_session), user=Depends(current_user)):
    items = db.scalars(select(DecompositionRun).order_by(DecompositionRun.created_at.desc()))
    return [_with_version(db, item) for item in items]


@router.post("")
def create(payload: RunInput, db=Depends(db_session), user=Depends(writer)):
    return service.create(db, payload.comparison_id)


@router.post("/{id}/recompute")
def recompute(id: str, db=Depends(db_session), user=Depends(writer)):
    return service.recompute(db, id)


@router.get("/{id}")
def detail(id: str, db=Depends(db_session), user=Depends(current_user)):
    item = db.get(DecompositionRun, id)
    if not item:
        raise HTTPException(404, "运行不存在")
    return _with_version(db, item)
