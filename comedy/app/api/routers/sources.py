from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from app import crud, models, schemas
from app.api import dependencies as deps

router = APIRouter()


@router.get("/"
            )
def read_sources(db: Session = Depends(deps.get_db),
                 skip: int = 0,
                 limit: int = 100,
                 ):
    return crud.source.get_multi(db, skip=skip, limit=limit)

@router.get("/{source_id}"
            )
def refresh_source(source_id):
    return crud.source.refresh_source(source_id)