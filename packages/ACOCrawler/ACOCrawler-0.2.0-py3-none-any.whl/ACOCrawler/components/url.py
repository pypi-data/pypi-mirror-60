import urllib
import re

URL_SPECIAL_CHARACTERS = re.compile('["\\\\\']')


class Url:

    @classmethod
    def erase_url_parameters(cls, url):
        parsed = urllib.parse.urlparse(url)
        return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, None, None, None))

    @classmethod
    def erase_url_special_characters(cls, url):
        url = URL_SPECIAL_CHARACTERS.sub('', url)
        return url

    @classmethod
    def get_url_domain(cls, url):
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc

    @classmethod
    def get_absolute_url(cls, original, relative):
        return urllib.parse.urljoin(original, relative)
