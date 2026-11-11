import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import ConsumptionDataset
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,payload):
 if db.scalar(select(ConsumptionDataset).where(ConsumptionDataset.name==payload.name)):raise HTTPException(409,"观测集名称已存在")
 item=ConsumptionDataset(id=str(uuid.uuid4()),name=payload.name,source=payload.source,rows=[r.model_dump() for r in payload.rows],created_at=now());db.add(item);db.commit();return serialize(item)
def require(db,id):
 item=db.get(ConsumptionDataset,id)
 if not item:raise HTTPException(404,"观测集不存在")
 return item
