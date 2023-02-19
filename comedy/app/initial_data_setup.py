from app.db.init_db import init_db


if __name__ == '__main__':
    from app.db.session import SessionLocalApp, engine
    init_db(
        SessionLocalApp(), engine=engine
    )
