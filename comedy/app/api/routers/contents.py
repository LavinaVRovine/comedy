from fastapi import APIRouter, Depends
# noinspection PyUnresolvedReferences
# from confluent_kafka.error import KafkaError, KafkaException
#
# from kafka_my.get_x import get_n_thingis
from app.api.dependencies import get_db
from sqlalchemy.orm import Session
from app.api import dependencies as deps
from app import models
from app import crud
from app import schemas
from typing import List
router = APIRouter(responses={404: {"description": "Not found"}})

# TODO: i think ill reorganize api to have /me
# TODO: figure out how to have multiple response models?
@router.get("/latest-contents/", tags=["latest-contents"], response_model=List[schemas.content.Content])
def get_latest_contents(db: Session = Depends(get_db)):

    return crud.get_latest_contents(db)

@router.get("/me/recommend", tags=["recommendations"], response_model=List[schemas.content.Content])
def get_recommended_content(db: Session = Depends(get_db), current_user: models.User = Depends(deps.get_current_active_user),):
    from recomentations.tmp import super_dumb_recommend
    recommended_content = super_dumb_recommend()
    return recommended_content



