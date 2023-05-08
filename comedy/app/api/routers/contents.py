from fastapi import APIRouter, Depends

from app.api.dependencies import get_db
from sqlalchemy.orm import Session
from app.api import dependencies as deps
from app import models
from app import crud
from app import schemas
from typing import List
router = APIRouter(responses={404: {"description": "Not found"}})


@router.get("/latest-contents/", tags=["latest-contents"], response_model=List[schemas.content.Content])
def get_latest_contents(db: Session = Depends(get_db), skip: int = 0, limit: int = 5):

    return crud.get_latest_contents(db, skip=skip, limit=limit)

@router.get("/me/recommend", tags=["recommendations"], response_model=List[schemas.content.Content])
def get_recommended_content(
        max_duration: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):
    max_duration_sec = max_duration * 60
    from recomentations.tmp import super_dumb_recommend
    recommended_content = super_dumb_recommend(time=max_duration_sec)
    return recommended_content



