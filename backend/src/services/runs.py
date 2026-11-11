import uuid

import redis
from fastapi import HTTPException

from src.models import DecompositionRun, PeriodComparison, ConsumptionDataset
from src.config.settings import REDIS_URL
from src.utils.time import now
from src.utils.serialization import serialize


def _enqueue(db, comparison):
    dataset = db.get(ConsumptionDataset, comparison.dataset_id)
    # 锁定排队时刻的观测版本并冻结快照；修订只影响之后排队的新运行
    item = DecompositionRun(
        id=str(uuid.uuid4()),
        comparison_id=comparison.id,
        status="queued",
        result={},
        error="",
        dataset_version=dataset.current_version,
        dataset_snapshot=[dict(r) for r in dataset.rows],
        created_at=now(),
    )
    db.add(item)
    db.commit()
    try:
        redis.Redis.from_url(REDIS_URL).lpush("mix-contribution:jobs", item.id)
    except redis.RedisError:
        item.status = "failed"
        item.error = "队列暂时不可用，请重试"
        db.commit()
        raise HTTPException(503, item.error)
    return serialize(item)


def create(db, comparison_id):
    comparison = db.get(PeriodComparison, comparison_id)
    if not comparison:
        raise HTTPException(404, "两期对照不存在")
    return _enqueue(db, comparison)


def recompute(db, run_id):
    """修订后基于当前最新观测重新排队同一对照的分解。"""
    previous = db.get(DecompositionRun, run_id)
    if not previous:
        raise HTTPException(404, "分解运行不存在")
    comparison = db.get(PeriodComparison, previous.comparison_id)
    dataset = db.get(ConsumptionDataset, comparison.dataset_id)
    if previous.dataset_version == dataset.current_version:
        raise HTTPException(409, "观测尚未修订，没有可重算的新版本数据")
    return _enqueue(db, comparison)


def require_completed(db, id):
    item = db.get(DecompositionRun, id)
    if not item:
        raise HTTPException(404, "分解运行不存在")
    if item.status != "completed":
        raise HTTPException(409, "分解尚未完成")
    return item
