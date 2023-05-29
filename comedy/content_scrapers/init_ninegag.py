from app.db.init_db import init_db
from app.db.session import SessionLocalApp, engine

if __name__ == '__main__':
    from content_scrapers.portals.ninegag.ninegag import NinegagSourceGroup
    xx = NinegagSourceGroup()
    xx.get_content()
    from source_managers.source_manager_ninegag import SourceManagerNinegag


    ng = SourceManagerNinegag(xx.source_name)
    ng.save(source_scraper=xx, db=SessionLocalApp())
    print()
