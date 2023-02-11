from fastapi import APIRouter, Depends
# noinspection PyUnresolvedReferences
# from confluent_kafka.error import KafkaError, KafkaException
#
# from kafka_my.get_x import get_n_thingis
from app.api.dependencies import get_db
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from typing import List
router = APIRouter(responses={404: {"description": "Not found"}})


@router.get("/latest-contents/", tags=["latest-contents"], response_model=List[schemas.YoutubeVideo])
def get_latest_contents(db: Session = Depends(get_db)):

    return crud.get_latest_contents(db)
