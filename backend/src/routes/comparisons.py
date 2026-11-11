from fastapi import APIRouter,Depends
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer,admin
from src.models import PeriodComparison
from src.schemas.comparison import ComparisonInput
from src.services import comparisons as service
from src.utils.serialization import rows
router=APIRouter(prefix="/comparisons")
@router.get("")
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(PeriodComparison).order_by(PeriodComparison.created_at.desc())))
@router.post("")
def create(payload:ComparisonInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload)
