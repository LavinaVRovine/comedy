from app.db.init_db import init_db
from app.db.session import SessionLocalApp, engine

if __name__ == '__main__':
    from content_scrapers.sources.ninegag_new.ninegag import NinegagSourceGroup
    xx = NinegagSourceGroup()
    xx.get_content()
    from content_scrapers.some_controller.dunno_yet import SourceManagerNinegag


    ng = SourceManagerNinegag()
    ng.save(source_scraper=xx, db=SessionLocalApp())
    print()
