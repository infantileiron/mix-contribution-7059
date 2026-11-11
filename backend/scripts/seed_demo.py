import json
import math
import random

from sqlalchemy import select, func

from src.config.database import Base, engine, Session
from src.models import (
    User,
    ConsumptionDataset,
    ObservationRevision,
    PeriodComparison,
    DecompositionRun,
    DriverReview,
    PublishedReport,
)
from src.services.analysis import analyze
from src.utils.security import hash_password
from src.utils.time import now
from src.utils.checksum import checksum


def seed():
    Base.metadata.create_all(engine)
    with Session() as db:
        for role in ("admin", "analyst", "viewer"):
            if not db.get(User, role):
                db.add(User(id=role, email=role + "@muhe.demo",
                            password=hash_password("Water2026!"), role=role))
        rng = random.Random(2209)
        zones = ["研发东区", "研发西区", "试制中心", "装配区", "后勤区",
                 "培训楼", "配套区", "检验区"]
        rows = []
        for m in range(24):
            index = 2024 * 12 + 10 + m
            year, month = divmod(index, 12)
            period = f"{year}-{month + 1:02}"
            for i, z in enumerate(zones):
                scale = round((1800 + i * 170) * (1 + .012 * m)
                              * (1 + .06 * math.sin(m / 2 + i)) + rng.uniform(-50, 50), 2)
                intensity = (.085 + i * .016) * (1 - .004 * m) * (1 + .08 * math.cos(m / 3 + i))
                rows.append({"zone": z, "period": period,
                             "scale": scale, "water": round(scale * intensity, 3)})

        if not db.get(ConsumptionDataset, "demo-data"):
            # 保留首版（原始）行，用于演示旧版本可追溯；rows 保存修订后的当前版本
            original_rows = [dict(r) for r in rows]
            target = next(r for r in rows if r["zone"] == "装配区" and r["period"] == "2026-10")
            old_water = target["water"]
            target["water"] = round(old_water * 1.032, 3)
            db.add(ConsumptionDataset(
                id="demo-data", name="沐禾园区·24月分区水量与作业规模",
                source="muhe_water_202411_202610.json", rows=rows,
                current_version=2, created_at=now()))
            db.add(ObservationRevision(
                id="demo-revision", dataset_id="demo-data",
                reason="水表复核发现装配区10月总表与分区表差3.2%，按复核单修正分区水量。",
                author="analyst@muhe.demo", base_version=1, new_version=2,
                changes=[{
                    "zone": "装配区", "period": "2026-10",
                    "before": {"scale": target["scale"], "water": old_water},
                    "after": {"scale": target["scale"], "water": target["water"]},
                }],
                checksum_before=checksum(original_rows),
                checksum_after=checksum(rows), created_at=now()))
            db.flush()

        if not db.get(PeriodComparison, "demo-comparison"):
            db.add(PeriodComparison(
                id="demo-comparison", name="2026年9月至10月·口径一致对照",
                dataset_id="demo-data", period_before="2026-09",
                period_after="2026-10", created_at=now()))
            db.flush()

        if not db.get(DecompositionRun, "demo-run"):
            dataset = db.get(ConsumptionDataset, "demo-data")
            db.add(DecompositionRun(
                id="demo-run", comparison_id="demo-comparison", status="completed",
                result=analyze(dataset.rows, "2026-09", "2026-10"), error="",
                dataset_version=2, dataset_snapshot=[dict(r) for r in dataset.rows],
                created_at=now()))
            db.flush()

        if not db.get(DriverReview, "demo-review"):
            db.add(DriverReview(
                id="demo-review", run_id="demo-run",
                note="两期均含8个分区，规模采用有效作业人日。归因是恒等式分解，不能直接当作节水措施的因果证据。",
                decision="accepted", author="analyst@muhe.demo",
                dataset_version=2, created_at=now()))
            db.flush()

        if not db.get(PublishedReport, "demo-report"):
            db.add(PublishedReport(
                id="demo-report", run_id="demo-run",
                title="10月用水结构·驱动复核年鉴",
                published_by="admin@muhe.demo", created_at=now()))

        db.commit()
        return {m.__tablename__: db.scalar(select(func.count()).select_from(m)) for m in (
            User, ConsumptionDataset, ObservationRevision, PeriodComparison,
            DecompositionRun, DriverReview, PublishedReport)}


if __name__ == "__main__":
    print(json.dumps(seed(), ensure_ascii=False))
