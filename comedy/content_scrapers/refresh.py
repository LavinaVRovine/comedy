from sqlalchemy import select
from app.db.session import SessionLocalApp, engine
from app.models.content_source import Portal, ContentSource
from worker import refresh_source
from comedy.config import DEBUGGING
def refresh_portal(portal_name: str = None):
    # TODO: since iam atm having only YT, its fine, but needs to be redone
    statement = select(ContentSource.id).where(ContentSource.portal_id==1)
    with SessionLocalApp() as session:
        source_ids = session.scalars(statement)
        for source_id in source_ids:
            if DEBUGGING:
                refresh_source(source_id)
            else:
                refresh_source.delay(source_id)

        print()

    ...
if __name__ == '__main__':
    refresh_portal()