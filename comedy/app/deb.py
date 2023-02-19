from sqlalchemy import select
from app.models import Portal, User
from app.models.user_portal import UserPortal
from sqlalchemy.orm import aliased
from app.db.session import SessionLocalApp


with SessionLocalApp() as session:
    # FIXME: use slugs and lowercase and all
    portal_name = "Youtube"
    x=session.query(UserPortal).filter(UserPortal.portal.has(name=portal_name) ).first()

session.query(UserPortal).filter(
        UserPortal.user_id == User.id,
        UserPortal.portal.has(name=portal_name)
).first()
