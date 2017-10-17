#TODO
class Record(object):
    """A record from a fm find query"""
    def __init__(self, keys, values):
        self._keys = keys
        self._values = values

    def keys(self):
        return self._keys

    def values(self):
       return self._values

    def __repr__(self):
       return '<Record>'
