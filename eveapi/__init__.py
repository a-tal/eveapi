VERSION = '1.4.1'
DEFAULT_UA = "eveapi.py/{}".format(VERSION)
USER_AGENT = None

from eveapi.api import EVEAPIConnection  # noqa (unused imports)
from eveapi.exceptions import Error, ServerError, RequestError, AuthenticationError  # noqa
