from sqlalchemy.orm import Session
from app.models import Content


def get_latest_contents(db: Session):
    return db.query(Content).order_by(Content.published_at.desc()).limit(5).all()



if __name__ == '__main__':
    from app.db.database import SessionApp
    from sqlalchemy import select
    with SessionApp() as session:
        statement = select(Content).order_by(Content.published_at.desc()).limit(5)
        results = session.execute(statement).all()
        x= [r[0] for r in results]
