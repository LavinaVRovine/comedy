

from app.core.celery_app import celery_app
from app.core.config import settings
from content_scrapers.content_controller import ContentController
# TODO: ehm how can i specify that the name is app.worker?
@celery_app.task(acks_late=True, )
def test_celery(word: str) -> str:
    print(f"LALA - { word }")
    return f"test task return {word}"


@celery_app.task(acks_late=True, )
def refresh_source(id: int):
    from app.db.session import SessionLocalApp, engine
    db = SessionLocalApp()
    from app.crud.crud_source import source

    s = source.get(db=db, id=id)

    c = ContentController(content_source_to_refresh=s)
    new_thingis = c.refresh(db=db)
    return True



if __name__ == '__main__':

    x = refresh_source.delay(1)
    #print()