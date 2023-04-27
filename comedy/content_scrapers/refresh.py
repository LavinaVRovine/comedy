from sqlalchemy import select
from app.db.session import SessionLocalApp, engine
from app.models.content_source import Portal, ContentSource
from worker import refresh_source
from comedy.config import DEBUGGING
from app.models.content_source import ContentSource, YoutubeContentSource, NinegagContentSource
from sqlalchemy.orm import selectin_polymorphic
def refresh_portal(portal_id: int = None, portal=None):
    # TODO: ok i think the loader opts needs to be default - see dumb recommned
    loader_opt = selectin_polymorphic(ContentSource, [YoutubeContentSource, NinegagContentSource, ])
    assert portal or portal_id
    if portal_id:
        statement = select(ContentSource.id).where(ContentSource.portal_id == portal_id)
    else:
        statement = select(ContentSource.id).where(ContentSource.portal == portal)
    statement = statement.options(loader_opt)
    with SessionLocalApp() as session:
        source_ids = session.scalars(statement).all()
        for i, source_id in enumerate(source_ids):

            if DEBUGGING:
                if i > 3:
                    print("CARE, NOT REFRESHING MORE SOURCES")
                    break
                refresh_source(source_id)
            else:
                refresh_source.delay(source_id)


    ...
if __name__ == '__main__':
    refresh_portal(2)