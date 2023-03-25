from sqlalchemy.orm import Session
from app.models import ContentSource, Portal
from app.crud.base import CRUDBase
from app.schemas.source import SourceBase, SourceUpdate


class CRUDSource(CRUDBase[ContentSource, SourceBase, SourceUpdate]):

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

    def refresh_source(self,db: Session, source_id: int):
        s = self.get(db=db, id=source_id)
        from content_scrapers.content_controller import ContentController
        ContentController.refresh(db=db)
        db.query
        ...

source = CRUDSource(ContentSource)