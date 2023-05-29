
def test_ninegag_scrapes_top_category(ninegag_source):
    ninegag_source.get_content()
    assert len(ninegag_source.content) == 10, "Ninegag scraper failed to scrape top content"
