from enum import Enum

from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query

import app.schemas.user_source
from app import schemas
from app import models, crud
from app.api import dependencies as deps


router = APIRouter(responses={404: {"description": "Not found"}})


# @router.get("/me/{user_source_id}", tags=["sources"], response_model=schemas.user_source.UserSourceFull)
# def get_my_user_source(
#         user_source_id: int,
#         user_source_in: schemas.user_source.UserSourceUpdate,
#         db: Session = Depends(deps.get_db),
#         current_user: models.User = Depends(deps.get_current_active_user),
#
# ):
#     raise NotImplementedError


@router.put("/me/{user_source_id}", tags=["sources"], response_model=schemas.user_source.UserSourceFull)
def update_my_source(
        user_source_id: int,
        user_source_in: schemas.user_source.UserSourceUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):
    user_source = crud.user_source.get(db, id=user_source_id)
    return crud.user_portal.update(db,
                                   db_obj=user_source,

                                   obj_in=user_source_in
                                   )


@router.post("/me/{portal_slug}", tags=["sources"], response_model=schemas.user_source.UserSourceFull)
def create_my_user_sources(
        portal_slug: str,
        user_source_in: app.schemas.user_source.UserSourceFake,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):

    user_source_in.watching = True
    user_source_in.portal_slug = portal_slug
    user_portal = crud.user_portal.get_user_portal(db, current_user, portal_slug=portal_slug)
    user_source_in.user_portal = user_portal
    #user_source_in.source = crud.source.get(db, id=user_source_in.source.id)
    user_source = crud.user_source.create(db, obj_in=user_source_in, user=current_user)
    return user_source


class SourcesType(str, Enum):
    mine = "mine"
    recommended = "recommended"
    other = "other"

@router.get("/me/{portal_slug}", tags=["sources"], response_model=list[
    schemas.user_source.UserSourceFull | schemas.user_source.UserSourceFake ])
def get_my_portal_sources(
        portal_slug: str,
        source_type: Annotated[SourcesType|None, Query()] = None,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):

    user_portal = crud.crud_user_portal.user_portal.get_user_portal(db, user=current_user, portal_slug=portal_slug)
    # TODO: iam sort of assuming only < 100 sources
    if source_type is None or source_type.value == "mine":

        lala = crud.user_source.get_multi(db, user_portal=user_portal)
        return lala
    if source_type.value == "recommended":
        return crud.crud_user_source.user_source.fake_recommended_user_sources(db=db, user_portal=user_portal)

    rec = crud.crud_user_source.user_source.fake_all_user_sources(db=db,user_portal=user_portal)
    return rec
