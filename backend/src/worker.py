from pathlib import Path
import redis,traceback
from sqlalchemy import select
from src.config.settings import REDIS_URL
from src.config.database import Session
from src.models import DecompositionRun,PeriodComparison,ConsumptionDataset
from src.services.analysis import analyze
client=redis.Redis.from_url(REDIS_URL);heartbeat=Path("/artifacts/worker-heartbeat")
def execute(id):
 with Session() as db:
  run=db.get(DecompositionRun,id)
  if not run or run.status not in ("queued","running"):return
  run.status="running";db.commit()
  try:
   comparison=db.get(PeriodComparison,run.comparison_id);dataset=db.get(ConsumptionDataset,comparison.dataset_id)
   run.result=analyze(dataset.rows,comparison.period_before,comparison.period_after);run.status="completed"
  except Exception as e:run.error=str(e);run.status="failed";traceback.print_exc()
  db.commit()
with Session() as db:
 for id in db.scalars(select(DecompositionRun.id).where(DecompositionRun.status.in_(["queued","running"]))):client.lpush("mix-contribution:jobs",id)
while True:
 heartbeat.touch();job=client.brpop("mix-contribution:jobs",timeout=1)
 if job:execute(job[1].decode())
