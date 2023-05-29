import pytest
from app import models
from faker import Faker
from source_managers.source_manager_ninegag import SourceManagerNinegag
# TODO: add the tag source

from content_scrapers import portals
from content_scrapers.schemas.ninegag import NinegagPhoto
from datetime import datetime
from content_scrapers.schemas.common import Image
from app.supported_portals import SupportedPortals
fake = Faker()


class TestNiceTest:
    @pytest.fixture
    def source(self):
        yield models.YoutubeContentSource(
            target_system_id=fake.name(),
            source_name="lala",
            portal_id=SupportedPortals.ninegag.id

        )

    @pytest.fixture
    def manager(self, source):
        yield SourceManagerNinegag(source)

    @pytest.fixture
    def source_scraper(self):
        scraper = portals.YoutubeVideoPortal()
        ids = [fake.uuid4(str) for _ in range(0, 5)]
        scraper.content = {
            i: NinegagPhoto(
                target_system_id=i,
                title=fake.name(),
                type="Photo",
                description=fake.text(),
                published_at=datetime.now(),
                likes=fake.random_int(),
                dislikes=fake.random_int(),
                comments=fake.random_int(),
                images={"image700": Image(url=fake.url(), width=fake.random_int(), height=fake.random_int())}
            ) for i in ids
        }
        yield scraper
    # def test__save_tags_as_sources_test(self, manager, source_scraper):
    #     assert False
    def test_topics_saving(self, manager, source_scraper):
        ...
    # TODO: write
    def test_model_preparation_actually_works(self, manager, source_scraper):

        models = manager.prepare_models(source_scraper)
        assert models
