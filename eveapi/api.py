try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from eveapi.cache import MemoryCache
from eveapi.context import _RootContext

proxy = None
proxySSL = False


def set_user_agent(user_agent_string):
    """
    Sets a User-Agent for any requests sent by the library.
    """
    global USER_AGENT
    USER_AGENT = user_agent_string


def EVEAPIConnection(url="api.eveonline.com", cacheHandler=MemoryCache,
                     proxy=None, proxySSL=False):
    """
    Creates an API object through which you can call remote functions.

    The following optional arguments may be provided:

    url - root location of the EVEAPI server

    proxy - (host,port) specifying a proxy server through which to request
            the API pages. Specifying a proxy overrides default proxy.

    proxySSL - True if the proxy requires SSL, False otherwise.

    cacheHandler - an object which must support the following interface:

         retrieve(host, path, params)

             Called when eveapi wants to fetch a document.
             host is the address of the server, path is the full path to
             the requested document, and params is a dict containing the
             parameters passed to this api call (keyID, vCode, etc).
             The method MUST return one of the following types:

              None - if your cache did not contain this entry
              str/unicode - eveapi will parse this as XML
              Element - previously stored object as provided to store()
              file-like object - eveapi will read() XML from the stream.

         store(host, path, params, doc, obj)

             Called when eveapi wants you to cache this item.
             You can use obj to get the info about the object (cachedUntil
             and currentTime, etc) doc is the XML document the object
             was generated from. It's generally best to cache the XML, not
             the object, unless you pickle the object. Note that this method
             will only be called if you returned None in the retrieve() for
             this object.
    """

    if not url.startswith("http"):
        url = "https://" + url
    p = urlparse(url, "https")
    if p.path and p.path[-1] == "/":
        p.path = p.path[:-1]
    ctx = _RootContext(None, p.path, {}, {})
    ctx.setcachehandler(cacheHandler)
    ctx._scheme = p.scheme
    ctx._host = p.netloc
    ctx._proxy = proxy or globals()["proxy"]
    ctx._proxySSL = proxySSL or globals()["proxySSL"]
    return ctx
