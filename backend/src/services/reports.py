import uuid,csv,io
from sqlalchemy import select
from fastapi import HTTPException
from src.models import PublishedReport,DriverReview
from src.services.runs import require_completed
from src.utils.time import now
from src.utils.serialization import serialize
from src.utils.csv import safe_cell
def create(db,payload,user):
 require_completed(db,payload.run_id)
 review=db.scalar(select(DriverReview).where(DriverReview.run_id==payload.run_id).order_by(DriverReview.created_at.desc()))
 if not review or review.decision!="accepted":raise HTTPException(409,"最新驱动复核须为接受才能归档")
 if db.scalar(select(PublishedReport).where(PublishedReport.run_id==payload.run_id)):raise HTTPException(409,"本次分解已归档")
 item=PublishedReport(id=str(uuid.uuid4()),published_by=user["email"],created_at=now(),**payload.model_dump());db.add(item);db.commit();return serialize(item)
def export(db,id):
 report=db.get(PublishedReport,id)
 if not report:raise HTTPException(404,"报告不存在")
 result=require_completed(db,report.run_id).result
 buf=io.StringIO();writer=csv.DictWriter(buf,["method","zone","scale","structure","intensity"]);writer.writeheader()
 for method in ("shapley","lmdi"):
  for row in result[method]["zones"]:writer.writerow({"method":method,**{k:safe_cell(v) for k,v in row.items()}})
 return "\ufeff"+buf.getvalue()
