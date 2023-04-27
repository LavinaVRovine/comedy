if __name__ == '__main__':
    from app.db.session import SessionLocalApp
    print("b")
    from app.models.content_source import ContentSource as SourceModel
    print("c")
    from content_scrapers.sources.ninegag import NinegagGroupSource
    from sqlalchemy import select
    session = SessionLocalApp()
    res = session.scalar(
        select(SourceModel).where(SourceModel.source_name == "top")
    )
    n = NinegagGroupSource(res)
    n._get_new_posts()
    print("d")