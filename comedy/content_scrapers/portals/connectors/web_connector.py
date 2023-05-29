from requests import Session
from .common import Connector


class WebConnector(Connector, Session):

    def __init__(self):
        super(WebConnector, self).__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        }




