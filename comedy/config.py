from pathlib import Path
from typing import Final
import os

ROOT_DIR: Final[Path] = Path(os.path.dirname(os.path.abspath(__file__)))


def read_ccloud_config(config_file):
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                conf[parameter] = value.strip()
    return conf


CONFLUENT_CONFIG = read_ccloud_config(ROOT_DIR.joinpath("client.properties"))
CONFLUENT_SCHEMA_REGISTRY_CONFIG = {
    "url": "https://psrc-mvkrw.europe-west3.gcp.confluent.cloud",
    # "basic.auth.credentials.source": "USER_INFO",
    "basic.auth.user.info": "YGF2AJDBSWVM6DY6:kVcj7sQRyF9VsrXmV5qn/cnUQX2EETq6cqHqDXGhtAO2rR1hvOCLSDTm669skA59"

}
