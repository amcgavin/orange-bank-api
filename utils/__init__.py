import os

from urllib.parse import urljoin


def get_url(path: str) -> str:
    return urljoin(os.environ.get("BASE_URL", ""), path)
