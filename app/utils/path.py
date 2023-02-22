from urllib.parse import urljoin, urlparse
from os import path
from app.core.config import settings


def host_validation(host: str) -> bool:
    return host.startswith(settings.s3.endpoint_url)

def get_full_url(path: str) -> str:
    """ Add s3 domain to path."""
    return urljoin(settings.s3.endpoint_url, path)

def trim_domain(url: str) -> str:
    """ Removes the domain part from a url. """
    return urlparse(url).path

def get_default_profile_picture_url():
    """ returns default picture when user haven't upload any thing yet. """
    return path.join(settings.s3.bucket_name, 'default.png')
