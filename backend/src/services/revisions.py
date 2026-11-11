import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from src.models import ConsumptionDataset, ObservationRevision
from src.utils.time import now
from src.utils.checksum import checksum
from src.utils.serialization import serialize


def listing(db, dataset_id: str | None = None):
    stmt = select(ObservationRevision).order_by(
        ObservationRevision.dataset_id, ObservationRevision.created_at.desc()
    )
    if dataset_id:
        stmt = stmt.where(ObservationRevision.dataset_id == dataset_id)
    return [serialize(r) for r in db.scalars(stmt)]


def create(db, dataset_id, payload, user):
    dataset = db.get(ConsumptionDataset, dataset_id)
    if not dataset:
        raise HTTPException(404, "观测集不存在")

    # 乐观并发控制：两人同时基于旧版本提交修订时，后提交者收到冲突
    if dataset.current_version != payload.base_version:
        raise HTTPException(
            409,
            f"修订冲突：观测已被他人修订（当前为第{dataset.current_version}版，"
            f"您依据的是第{payload.base_version}版），请刷新查看最新数据后再提交修订",
        )

    incoming = {(r.zone, r.period): r for r in payload.rows}
    if len(incoming) != len(payload.rows):
        raise HTTPException(422, "修订清单内分区与月份不能重复")

    existing = {(r["zone"], r["period"]): r for r in dataset.rows}
    unknown = sorted(set(incoming) - set(existing))
    if unknown:
        raise HTTPException(422, "修订只允许修正已有分区月份观测，不能新增：" + "、".join(
            f"{z}/{p}" for z, p in unknown[:5]
        ))

    changes = []
    for key, row in incoming.items():
        before = existing[key]
        if float(before["scale"]) != row.scale or float(before["water"]) != row.water:
            changes.append({
                "zone": row.zone,
                "period": row.period,
                "before": {"scale": before["scale"], "water": before["water"]},
                "after": {"scale": row.scale, "water": row.water},
            })
    if not changes:
        raise HTTPException(422, "没有检测到任何数值变化，无需修订")

    checksum_before = checksum(dataset.rows)
    new_rows = []
    updates = {
        (r.zone, r.period): {"scale": r.scale, "water": r.water} for r in payload.rows
    }
    for row in dataset.rows:
        patch = updates.get((row["zone"], row["period"]))
        if patch:
            new_rows.append({**row, **patch})
        else:
            new_rows.append(row)

    revision = ObservationRevision(
        id=str(uuid.uuid4()),
        dataset_id=dataset_id,
        reason=payload.reason,
        author=user["email"],
        base_version=dataset.current_version,
        new_version=dataset.current_version + 1,
        changes=changes,
        checksum_before=checksum_before,
        checksum_after=checksum(new_rows),
        created_at=now(),
    )
    dataset.rows = new_rows
    dataset.current_version += 1
    flag_modified(dataset, "rows")
    db.add(revision)
    db.commit()
    return {"revision": serialize(revision), "dataset": serialize(dataset)}
