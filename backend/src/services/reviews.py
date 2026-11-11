import uuid

from src.models import DriverReview
from src.services.runs import require_completed
from src.utils.time import now
from src.utils.serialization import serialize


def create(db, payload, user):
    run = require_completed(db, payload.run_id)
    item = DriverReview(
        id=str(uuid.uuid4()),
        created_at=now(),
        author=user["email"],
        run_id=payload.run_id,
        note=payload.note,
        decision=payload.decision,
        dataset_version=run.dataset_version,
    )
    db.add(item)
    db.commit()
    return serialize(item)
