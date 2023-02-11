import asyncio
from app.models.source import Source
from app.db.session import SessionLocalApp, SessionLocalAppAsync
from sqlalchemy import select
from datetime import datetime

from content.sources.youtube import YoutubeSource, YoutubePlaylist
from dateutil import parser
from app.models.content import YoutubeVideo


async def get_sources_to_refresh(since: datetime = datetime.utcnow().replace(tzinfo=None)):
    # FIXME
    since = since.replace(tzinfo=None)
    statement = select(Source).where(
        (Source.last_checked_at == None) | (Source.last_checked_at >= since)
    )

    async with SessionLocalAppAsync() as session:
        result = await session.scalars(statement)
        return result.all()

def get_new_videos(source: Source):
    to_add = []
    y = YoutubePlaylist(source)
    lala = y._get_videos()
    for i, v in enumerate(lala):
        published_at = parser.parse(v["snippet"]["publishedAt"])
        if published_at >= source.last_checked_at:
            break
        # if i>10:
        #     print("stopiter")
        #     break
        to_add.append(
            YoutubeVideo(id=v["snippet"]["resourceId"]["videoId"],
                         description=v["snippet"]["description"],
                         title=v["snippet"]["title"],
                         thumbnails=v["snippet"]["thumbnails"],
                         published_at=published_at)
        )
        return to_add
if __name__ == '__main__':

    since = datetime.utcnow()#.replace(tzinfo=pytz.UTC)
    refresh_sources = asyncio.run(get_sources_to_refresh(since))


    for source_to_refresh in refresh_sources:
        to_add = get_new_videos(source_to_refresh)
        # TODO: isnt there a new syntax for 2.0?
        with SessionLocalApp() as session:
            session.bulk_save_objects(to_add)
            source_to_refresh.last_checked_at = since
            session.add(source_to_refresh)
            session.commit()

    print()
