
from app import models
from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import SessionLocalApp, engine
from app.crud.crud_source import source
from source_managers.source_manager import SourceManager
from source_managers import init_manager_from_class
# TODO: ehm how can i specify that the name is app.worker?
# @celery_app.task(acks_late=True, )
# def test_celery(word: str) -> str:
#     print(f"LALA - { word }")
#     return f"test task return {word}"


#@celery_app.task(acks_late=True, )
def refresh_source(id: int):

    db = SessionLocalApp()


    s = source.get(db=db, id=id)
    print(type(s))
    klass = init_manager_from_class(s)
    c = klass(source=s)
    new_thingis = c.refresh(db=db)
    return True



if __name__ == '__main__':
    refresh_source(1)
    #x = refresh_source.delay(1)
    print("a")