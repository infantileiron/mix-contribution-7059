import uuid,redis
from fastapi import HTTPException
from src.models import DecompositionRun,PeriodComparison
from src.config.settings import REDIS_URL
from src.utils.time import now
from src.utils.serialization import serialize
def create(db,comparison_id):
 if not db.get(PeriodComparison,comparison_id):raise HTTPException(404,"两期对照不存在")
 item=DecompositionRun(id=str(uuid.uuid4()),comparison_id=comparison_id,status="queued",result={},error="",created_at=now());db.add(item);db.commit()
 try:redis.Redis.from_url(REDIS_URL).lpush("mix-contribution:jobs",item.id)
 except redis.RedisError:
  item.status="failed";item.error="队列暂时不可用，请重试";db.commit();raise HTTPException(503,item.error)
 return serialize(item)
def require_completed(db,id):
 item=db.get(DecompositionRun,id)
 if not item:raise HTTPException(404,"分解运行不存在")
 if item.status!="completed":raise HTTPException(409,"分解尚未完成")
 return item
