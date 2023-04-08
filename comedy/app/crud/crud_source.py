from sqlalchemy.orm import Session
from app.models import ContentSource, Portal
from app.crud.base import CRUDBase
from app.schemas.source import SourceSimplified, SourceUpdate


class CRUDSource(CRUDBase[ContentSource, SourceSimplified, SourceUpdate]):

    ...

    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100, portal: Portal | None = None
    ):

        if not portal:
            return super(CRUDSource, self).get_multi(db=db, skip=skip, limit=limit,)
        return db.query(self.model).where(ContentSource.portal == portal).offset(skip).limit(limit).all()


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
        from content_scrapers.content_controller import ContentController
        c = ContentController(content_source_to_refresh=s)
        new_thingis = c.refresh(db=db)
        return new_thingis


source = CRUDSource(ContentSource)
