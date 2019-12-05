import time
import pickle
import operator

from utils import digest
from itertools import takewhile
from collections import OrderedDict
from abc import abstractmethod, ABC

class IStorage(ABC):
    """
    Local storage for this node.
    IStorage implementations of get must return the same type as put in by set
    """

    @abstractmethod
    def __setitem__(self, key, value):
        """
        Set a key to the given value.
        """

    @abstractmethod
    def __getitem__(self, key):
        """
        Get the given key.  If item doesn't exist, raises C{KeyError}
        """

    @abstractmethod
    def get(self, key, default=None):
        """
        Get given key.  If not found, return default.
        """

    @abstractmethod
    def iter_older_than(self, seconds_old):
        """
        Return the an iterator over (key, value) tuples for items older
        than the given secondsOld.
        """

    @abstractmethod
    def __iter__(self):
        """
        Get the iterator for this storage, should yield tuple of (key, value)
        """

class ForgetfulStorage(IStorage):
    def __init__(self, ttl=604800):
        """
        By default, max age is a week.
        """
        self.data = OrderedDict()
        self.ttl = ttl

    def __setitem__(self, key, value):
        if key in self.data:
            del self.data[key]
        self.data[key] = (time.monotonic(), value)
        self.cull()

    # added by mylsef
    def delete(self, key):
        self.cull()
        if key in self.data:
            del self.data[key]

    def cull(self):
        for _, _ in self.iter_older_than(self.ttl):
            self.data.popitem(last=False)

    def get(self, key, default=None):
        self.cull()
        if key in self.data:
            return self[key]
        return default

    def __getitem__(self, key):
        self.cull()
        return self.data[key][1]

    def __repr__(self):
        self.cull()
        return repr(self.data)

    def iter_older_than(self, seconds_old):
        min_birthday = time.monotonic() - seconds_old
        zipped = self._triple_iter()
        matches = takewhile(lambda r: min_birthday >= r[1], zipped)
        return list(map(operator.itemgetter(0, 2), matches))

    def _triple_iter(self):
        ikeys = self.data.keys()
        ibirthday = map(operator.itemgetter(0), self.data.values())
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ibirthday, ivalues)

    def __iter__(self):
        self.cull()
        ikeys = self.data.keys()
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ivalues)

class AwsomeStorage(IStorage):

    def __init__(self, ttl=604800):
        self.data_tag = OrderedDict()
        self.data_file = OrderedDict()
        self.max_age = ttl

    def __setitem__(self, key, value):
        return IStorage.__setitem__(key,value)

    # { tagid, (time, set(  fileid ) ) }
    def set(self, key, value):
        if key in self.data_tag:
            s = pickle.loads(self.data_tag[key][1])
            s.add(digest(value))
            self.data_tag[key] = (time.monotonic(), pickle.dumps(s))
        else:
            s = set()
            s.add(digest(value))
            self.data_tag[key] = (time.monotonic(), pickle.dumps(s))
        self.set_file(digest(value), value)
        self.cull()

    def set_file(self, key, value):
        self.data_file[key] = (time.monotonic(), pickle.dumps(value))
        self.cull()
        # cull para los files

    def cull(self):
        for _, _ in self.iter_older_than(self.max_age):
            self.data_tag.popitem(last = False)

    def get(self, key, default = None):
        self.cull()
        if key in self.data_tag:
            return self.data_tag[key][1]
        if key in self.data_file:
            return self.data_file[key][1]
        return default

    def get_file(self, key, default = None):
        self.cull()
        if key in self.data_file:
            return pickle.loads(self.data_file[key][1])
        return default

    def __getitem__(self, key):
        self.cull()
        return self.data_tag[key][1]

    def __iter__(self):
        self.cull()
        ikeys = self.data_tag.keys()
        ivalues = map(operator.itemgetter(1), self.data_tag.values())
        return zip(ikeys, ivalues)

    def delete(self, key):
        self.cull()
        del self.data_file[key]

    def delete_tag(self, key, value):
        self.cull()
        files = pickle.loads(self.data_tag[key][1])
        files.remove(digest(value))
        self.data_tag[key] = (time.monotonic(), pickle.dumps(files))

    def __repr__(self):
        self.cull()
        return repr(self.data_tag)

    def iter_older_than(self, seconds_old):
        t = time.monotonic() - seconds_old
        zipped = self._triple_iter()
        matches = takewhile(lambda r: t >= r[1], zipped)
        return list(map(operator.itemgetter(0,2),matches))

    def _triple_iter(self):
        ikeys = self.data_tag.keys()
        it = map(operator.itemgetter(0),self.data_tag.values())
        ivalues = map(operator.itemgetter(1), self.data_tag.values())
        return zip(ikeys, it, ivalues)