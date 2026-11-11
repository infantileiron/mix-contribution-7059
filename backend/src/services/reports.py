import csv
import io
import uuid

from sqlalchemy import select
from fastapi import HTTPException

from src.models import (
    PublishedReport,
    DriverReview,
    PeriodComparison,
    ConsumptionDataset,
)
from src.services.runs import require_completed
from src.utils.time import now
from src.utils.serialization import serialize
from src.utils.csv import safe_cell


def create(db, payload, user):
    run = require_completed(db, payload.run_id)
    review = db.scalar(
        select(DriverReview)
        .where(DriverReview.run_id == payload.run_id)
        .order_by(DriverReview.created_at.desc())
    )
    if not review or review.decision != "accepted":
        raise HTTPException(409, "最新驱动复核须为接受才能归档")

    comparison = db.get(PeriodComparison, run.comparison_id)
    dataset = db.get(ConsumptionDataset, comparison.dataset_id)
    if run.dataset_version != dataset.current_version:
        raise HTTPException(
            409,
            f"该复核基于第{run.dataset_version}版观测，当前已是第{dataset.current_version}版；"
            "旧版复核不能批准新版报告，请基于最新观测重新运行分解并复核",
        )

    if db.scalar(select(PublishedReport).where(PublishedReport.run_id == payload.run_id)):
        raise HTTPException(409, "本次分解已归档")
    item = PublishedReport(
        id=str(uuid.uuid4()),
        published_by=user["email"],
        created_at=now(),
        **payload.model_dump(),
    )
    db.add(item)
    db.commit()
    return serialize(item)


def export(db, id):
    report = db.get(PublishedReport, id)
    if not report:
        raise HTTPException(404, "报告不存在")
    # 已归档结果始终读取运行自身的结果与快照，修订后仍能追溯旧数据
    result = require_completed(db, report.run_id).result
    buf = io.StringIO()
    writer = csv.DictWriter(buf, ["method", "zone", "scale", "structure", "intensity"])
    writer.writeheader()
    for method in ("shapley", "lmdi"):
        for row in result[method]["zones"]:
            writer.writerow({"method": method, **{k: safe_cell(v) for k, v in row.items()}})
    return "﻿" + buf.getvalue()
