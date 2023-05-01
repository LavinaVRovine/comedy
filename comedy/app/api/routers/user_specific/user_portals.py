
from typing import List, Dict, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.exceptions import ValidationError

from app import schemas
from sqlalchemy.orm import Session
from app.api import dependencies as deps
from app import crud, models


router = APIRouter(responses={404: {"description": "Not found"}})


@router.get("/me/", tags=["portals"], response_model=List[
    schemas.user_portal.UserPortalGet

])
def get_and_create_my_user_portals(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):
    return crud.user_portal.get_and_create_user_portals(db, current_user,)


@router.get("/me/{portal_slug}", tags=["portals"], response_model=schemas.user_portal.UserPortalGet)
def get_my_user_portal(
        portal_slug: str,
        user_portal_id: Annotated[int | None, Query()] = None,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):
    if user_portal_id:
        return crud.user_portal.get(db, id=user_portal_id)
    return crud.user_portal.get_user_portal(db, current_user, portal_slug=portal_slug)


@router.post("/me/", tags=["portals"], response_model=schemas.user_portal.UserPortalGet)
def create_my_portal(
        user_portal_create: schemas.user_portal.UserPortalCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):
    # TODO: non working
    raise NotImplementedError
    crud.user_portal.create(db, obj_in=user_portal_create)
    return crud.user_portal.get_user_portal(db, current_user, portal_slug=portal_slug)


@router.put("/me/{user_portal_id}", tags=["portals"], response_model=schemas.user_portal.UserPortalGet)
def update_my_user_portal(
        user_portal_id: int,
        user_portal_in: schemas.user_portal.UserPortalUpdateWatching,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):
    user_portal = crud.user_portal.get(db, id=user_portal_id)
    o = crud.user_portal.update(db,
                                db_obj=user_portal,

                                obj_in=user_portal_in
                                )
    return o

@router.get("/me/sync/{user_portal_id}", tags=["portals"], )
def sync_my_user_portal(
        user_portal_id: int,

        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):
    user_portal = crud.user_portal.get(db, id=user_portal_id)
    crud.user_portal._refresh_user_portal_sources(db, user=current_user,user_portal=user_portal)

    return True