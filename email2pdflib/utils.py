from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


def can_url_fetch(src):
    try:
        req = Request(src)
        urlopen(req)
    except HTTPError:
        return False
    except URLError:
        return False
    except ValueError:
        return False

    return True
