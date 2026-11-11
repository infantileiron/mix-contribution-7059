from fastapi import APIRouter, Depends

from src.config.database import db_session
from src.controllers.auth import current_user, writer
from src.schemas.revision import RevisionInput
from src.services import revisions as service

router = APIRouter(prefix="/datasets/{dataset_id}/revisions")


@router.get("")
def listing(dataset_id: str, db=Depends(db_session), user=Depends(current_user)):
    return service.listing(db, dataset_id)


@router.post("")
def create(dataset_id: str, payload: RevisionInput,
           db=Depends(db_session), user=Depends(writer)):
    return service.create(db, dataset_id, payload, user)
