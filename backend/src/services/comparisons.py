import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import PeriodComparison
from src.services.datasets import require
from src.services.periods import prepare
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload):
 dataset=require(db,payload.dataset_id)
 try:prepare(dataset.rows,payload.period_before,payload.period_after)
 except ValueError as e:raise HTTPException(422,str(e))
 if db.scalar(select(PeriodComparison).where(PeriodComparison.name==payload.name)):raise HTTPException(409,"对照名称已存在")
 item=PeriodComparison(id=str(uuid.uuid4()),created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
