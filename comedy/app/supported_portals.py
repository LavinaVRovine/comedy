from app.models import Portal


class SupportedPortals:
    youtube = Portal(
            id=1, name="Youtube", url="whatever", img_path="youtube.png", syncable=True
        )
    ninegag = Portal(
            id=2, name="Ninegag", url="whatever2", img_path="9gag.png"
        )
