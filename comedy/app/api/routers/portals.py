from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select


from app import schemas
from sqlalchemy.orm import Session, aliased
from app.api import dependencies as deps
from app import crud, models
from app.models import Portal, User
from app.models.user_content import UserPortal

router = APIRouter(responses={404: {"description": "Not found"}})


@router.get("/", tags=["portals"], response_model=List[schemas.Portal])
def get_supported_portals(
        db: Session = Depends(deps.get_db)
):
    return crud.crud_portal.get_supported_portals(db)

@router.post("/",
             #"/portal_slug
             tags=["portals"], response_model=schemas.Msg
             )
def refresh_portal(current_user: models.User = Depends(deps.get_current_active_superuser)):
    crud.crud_portal.refresh_portal()
    return {"msg": "Portal queued for refresh"}

@router.get("/me/portals/", tags=["portals"], response_model=List[
    schemas.user_portal_and_source.UserPortalBase

])
def get_portals_users(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):
    return crud.user_portal.get_and_create_user_portals(db, current_user,)


@router.get("/me/portals/{portal_slug}", tags=["portals"], response_model=schemas.user_portal_and_source.UserPortalFull)
def get_my_portal(
        portal_slug: str,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):
    return crud.user_portal.get_or_create_user_portal(db, current_user, portal_slug=portal_slug)


@router.put("/me/portals/{user_portal_id}", tags=["portals"], response_model=schemas.user_portal_and_source.UserPortalFull)
def update_my_portal(
        user_portal_id: int|str,
        user_portal_in: schemas.user_portal_and_source.UserPortalUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),

):
    # TODO: iam thinking about rather searching by user
    user_portal = crud.user_portal.get(db, id=user_portal_id)
    o= crud.user_portal.update(db,
                                   db_obj=user_portal,

                                   obj_in=user_portal_in
                                   )
    return o
