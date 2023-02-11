if __name__ == '__main__':

    from typing import List
    from content.sources.youtube import YoutubeSource
    from content.content_models.videos import YoutubeVideo


    youtube_source = YoutubeSource()
    bittersteel_playlist_id = "UU4tWW-toq9KKo-HL3S8D23A"
    bitterstel_channel_id = 'UC4tWW-toq9KKo-HL3S8D23A'  # = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
    # uploads_playilis = youtube_source.get_channels_uploaded_playlist_id(channel_id=bitterstel_channel_id)
    vs: List[YoutubeVideo] = youtube_source.get_videos(bittersteel_playlist_id)

    from app.models import Source, YoutubeVideo, Portal
    from app.db.session import SessionLocalApp

    session = SessionLocalApp()
    if True:

        yt_portal = Portal(portal_name="youtube", portal_url="www.youtube.com")

        source = Source(
            source_id=bittersteel_playlist_id, source_name="bittersteel_TMP",
            #portal=yt_portal,
            portal_id=1
        )

        #session.add(yt_portal)
        session.add(source)
        session.commit()
    else:
        session = Session(engine)
        statement = select(Source).filter_by(source_name="bittersteel_TMP")
        result = session.execute(statement).first()
        source = result[0]

    vids = []
    for v in vs:
        vids.append(
            YoutubeVideo(
                id=v.id,
                thumbnails=v.thumbnails,
                title=v.title, description=v.description, published_at=v.published_at,
                source=source
            )
        )

    session.add_all(vids)
    session.commit()

