from sqlalchemy.orm import Session
from app.models import Portal


def get_supported_portals(db: Session):
    return db.query(Portal).all()
