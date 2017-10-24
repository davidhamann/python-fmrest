"""Record class for FileMaker record responses"""

class Record(object):
    """A FileMaker record"""

    def __init__(self, keys, values):
        """Initialize the Record class.

        Parameters
        ----------
        keys : list
            List of keys (fields) for this Record as returned by FileMaker Server
        values : list
            Values corresponding to keys
        """

        self._keys = keys
        self._values = values

        if len(self._keys) != len(self._values):
            raise ValueError("Length of keys does not match length of values.")

    def keys(self):
        """Access keys of Record."""
        return self._keys

    def values(self):
        """Access values of Record."""
        return self._values

    def __repr__(self):
        return '<Record id={}>'.format(self.recordId)

    def __getitem__(self, key):
        """Returns value for given key. For dict lookups, like my_id = record['id']."""
        keys = self.keys()

        try:
            index = keys.index(key)
            return self.values()[index]
        except ValueError:
            raise KeyError(("No field named {}. Note that the Data API only returns fields "
                            "placed on your FileMaker layout.").format(key))

    def __getattr__(self, key):
        """Returns value for given key. For attribute lookups, like my_id = record.id.

        Calls __getitem__ for key access.
        """
        try:
            return self[key]
        except KeyError as ex:
            raise AttributeError(ex) from None
