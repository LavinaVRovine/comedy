from app.db.init_db import init_db
from app.db.session import SessionLocalApp, engine

if __name__ == '__main__':
    # from content_scrapers.portals import YoutubeUploadedPlaylist
    # xx = YoutubeUploadedPlaylist()
    # xx.get_content()
    from content_scrapers import YoutubeVideoPortal

    p = YoutubeVideoPortal("PLRv5q2ew_zJt4Wbynk2fGBBldb1qzB1HH")
    p.get_content()
    print()
    exit()
    from source_managers.source_manager_ninegag import SourceManagerNinegag


    ng = SourceManagerNinegag(xx.source_name)
    ng.save(source_scraper=xx, db=SessionLocalApp())
    print()
