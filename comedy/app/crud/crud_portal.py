from sqlalchemy.orm import Session
from app.models import Portal
from content_scrapers.refresh import refresh_portal as refresh_portal_real

def get_supported_portals(db: Session):
    return db.query(Portal).all()

def refresh_portal():
    return refresh_portal_real()
