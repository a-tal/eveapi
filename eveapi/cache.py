"""This used to be used in testing, might as well make it available."""


import os
import zlib
import pickle
from datetime import datetime


class _CacheBase(object):
    """Subclass this to implement storage. Do not use this directly.

    Implement `save`, `fetch` and `delete` methods in your subclass.
    """

    def __init__(self):
        self.cache = {}

    def retrieve(self, host, path, params):
        # eveapi asks if we have this request cached
        key = hash((host, path, frozenset(list(params.items()))))

        # see if we have the key in memory or fallback to implementation
        cached = self.cache.get(key, self.fetch(key))

        if cached is not None:
            content, until = cached
            # check if the cached doc is fresh enough
            if datetime.utcnow() < until:
                return content  # return the cached XML doc

            # it's stale. purge it from memory
            del self.cache[key]

            # and in our active implementation
            self.delete(key)

    def store(self, host, path, params, doc, obj):
        # eveapi is asking us to cache an item
        key = hash((host, path, frozenset(list(params.items()))))

        cached_for = obj.cachedUntil - obj.currentTime
        if cached_for:
            # store in memory
            self.cache[key] = (doc, obj.cachedUntil)

            # store in implementation
            self.save(key, doc, obj.cachedUntil)


class MemoryCache(_CacheBase):
    """Stores returns in memory for the intended timeframe."""

    def save(self, key, content, until):
        """This is passed the key name, the content and a datetime until."""
        pass

    def fetch(self, key):
        """This should return a tuple of the content, and datetime until.
        None if not found."""
        pass

    def delete(self, key):
        """This should delete the content based on its key."""
        pass


class FileCache(_CacheBase):
    """
    Note: this is an example handler to demonstrate how to use them.
    a -real- handler should probably be thread-safe and handle errors
    properly (and perhaps use a better hashing scheme).

    Initalize with a directory filepath to use for storing .cache files.
    """

    def __init__(self, cache_dir):
        if not os.path.isdir(cache_dir):
            raise OSError("{} is not a directory".format(cache_dir))
        self.cache_dir = cache_dir
        super(FileCache, self).__init__()

    def _get_cache_file(self, key):
        return os.path.join(self.cache_dir, "{}.cache".format(key))

    def fetch(self, key):
        """Fetches (content, until) from our cache folder."""

        cache_file = self._get_cache_file(key)
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as opencache:
                return pickle.loads(zlib.decompress(opencache.read()))

    def delete(self, key):
        """Removes the .cache file from disk."""

        try:
            os.remove(self._get_cache_file(key))
        except:
            pass

    def save(self, key, content, until):
        """Saves (content, until) to our cache folder."""

        cache_file = os.path.join(self.cache_dir, "{}.cache".format(key))
        with open(cache_file, "wb") as opencache:
            opencache.write(zlib.compress(pickle.dumps((content, until), -1)))
