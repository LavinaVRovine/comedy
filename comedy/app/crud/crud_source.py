from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.crud.base import CRUDBase
from app import crud
from app.schemas.source import SourceSimplified, SourceUpdate, SourceCreate
from source_managers import init_manager_from_class
from app import models
from fastapi.encoders import jsonable_encoder
class CRUDSource(CRUDBase[models.ContentSource, SourceCreate, SourceUpdate]):

    ...



    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100, portal: models.Portal | None = None
    ):

        if not portal:
            return super(CRUDSource, self).get_multi(db=db, skip=skip, limit=limit,)
        return db.query(self.model).where(models.ContentSource.portal == portal).offset(skip).limit(limit).all()

    def get_recommended_sources(self, db: Session, *, portal: models.Portal | None = None) -> list[models.ContentSource]:
        # TODO: limit etc -> rewrite get or rather get multi to accept some filter args .join(models.Portal, models.ContentSource.portal_id == models.Portal.id)
        if portal:
            statement = select(models.ContentSource).where(and_(
                models.ContentSource.portal_id == portal.id,
                models.ContentSource.recommended == True
            ))
        else:
            statement = select(models.ContentSource).where(
                models.ContentSource.recommended == True
            )
        return db.scalars(statement).all()
        # TODO: write
        return []
    # def update(
    #     self,
    #     db: Session,
    #     *,
    #     db_obj: ModelType,
    #     obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    # ) -> ModelType:

    def refresh_source_and_get_new_content(self, db: Session, source_id: int):
        # iam leaving this here for now but probably not needed
        s = self.get(db=db, id=source_id)
        c = init_manager_from_class(s)
        new_thingis = c.refresh(db=db)
        return new_thingis

    def get_or_create_multiple_sources(self, db:Session,):
        ...


source = CRUDSource(models.ContentSource)
