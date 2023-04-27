from sqlalchemy.orm import Session
from app.models import Content, YoutubeVideo, NinegagPhoto, NinegagAnimated
from app.models.user_content import UserPortal, UserSource, UserContent
from sqlalchemy import select
from app.db.session import SessionLocalApp, engine
from sqlalchemy.orm import selectin_polymorphic
def super_dumb_recommend(db: Session = None, time: float = None):
    # FIXME: fix dbs and all that
    # TODO: see https://docs.sqlalchemy.org/en/20/orm/queryguide/inheritance.html#configuring-selectin-polymorphic-on-mappers
    #  to maybe apply the selectin polymo by default
    """
    Performance and all the inheritance considerations:
    https://docs.sqlalchemy.org/en/20/orm/queryguide/inheritance.html#using-selectin-polymorphic

    :param time: total max time in seconds
    :return:
    """
    with SessionLocalApp() as session:
        loader_opt = selectin_polymorphic(Content, [YoutubeVideo, NinegagPhoto, NinegagAnimated])
        # noinspection PyComparisonWithNone
        statement = select(Content).outerjoin(UserContent).where(UserContent.seen == None).order_by(Content.published_at).limit(20).options(loader_opt)
        lala = session.scalars(statement).all()
        return lala#[:10]


if __name__ == '__main__':
    yt = super_dumb_recommend()[0]
    print()








