import urllib.request
import urllib.error

from carte import exceptions


def download_resource(url: str) -> str:
    response = None

    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as error:
        raise exceptions.GeocodeException("%s: %s", error.code, error.reason)
    except urllib.error.URLError as error:
        raise exceptions.GeocodeException(error.reason)

    return response.read()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )

        return cls._instances[cls]
