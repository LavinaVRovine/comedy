from typing import List
from fastapi import APIRouter, Depends
from app import schemas
from sqlalchemy.orm import Session
from app.api import dependencies as deps
from app import crud, models


router = APIRouter(responses={404: {"description": "Not found"}})


@router.get("/", tags=["portals"], response_model=List[schemas.Portal])
def get_supported_portals(
        db: Session = Depends(deps.get_db)
):
    return crud.crud_portal.get_supported_portals(db)


@router.post("/",
             # "/portal_slug
             tags=["portals"], response_model=schemas.Msg
             )
def refresh_portal_content(current_user: models.User = Depends(deps.get_current_active_superuser)):
    """
    Refresh all sources for a portal
    :param current_user:
    :return:
    """
    crud.crud_portal.refresh_portal()
    return {"msg": "Portal queued for refresh"}
