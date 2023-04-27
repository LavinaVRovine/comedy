from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from app import crud, models, schemas
from app.api import dependencies as deps
from app.core.celery_app import celery_app
from worker import refresh_source as celery_refresh_source
router = APIRouter()


@router.get("/"
            )
def read_sources(db: Session = Depends(deps.get_db),
                 skip: int = 0,
                 limit: int = 100,
                 ):
    return crud.source.get_multi(db, skip=skip, limit=limit)


@router.get("/{source_id}/refresh", response_model=schemas.Msg
            )
def refresh_source(source_id: int, current_user: models.User = Depends(deps.get_current_active_superuser),):
    celery_refresh_source.delay(source_id)
    return {"msg": f"Queued source refresh {source_id}"}

    #return dict(id=source_id, content=crud.source.refresh_source_and_get_new_content(db, source_id=source_id))

