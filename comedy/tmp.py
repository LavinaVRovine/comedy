if __name__ == '__main__':
    from app.db.session import SessionLocalApp

    from app.models import Content, YoutubeVideo
    from sqlalchemy import select
    session = SessionLocalApp()
    res = session.scalar(
        select(YoutubeVideo)
    )

    print("d")