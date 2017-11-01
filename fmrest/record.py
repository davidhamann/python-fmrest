"""Record class for FileMaker record responses"""

class Record(object):
    """A FileMaker record"""

    def __init__(self, keys, values, in_portal=None):
        """Initialize the Record class.

        Parameters
        ----------
        keys : list
            List of keys (fields) for this Record as returned by FileMaker Server
        values : list
            Values corresponding to keys
        in_portal : bool
            If true, this record instance describes a related record from a portal. This is a
            special case as portal records are treated differently by the Data API and don't get
            all standard keys (modId is missing).
        """

        self._keys = keys
        self._values = values
        self._in_portal = in_portal

        if len(self._keys) != len(self._values):
            raise ValueError("Length of keys does not match length of values.")

    def __repr__(self):
        return '<Record id={} modification_id={}>'.format(
            self.record_id(),
            self.modification_id()
        )

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

    def record_id(self):
        """Returns the internal record id.

        This is exposed as a method to reliably return the record id, even if the API might change
        in the future.
        """
        return self.recordId

    def modification_id(self):
        """Returns the internal modification id.

        This is exposed as a method to reliably return the modification id, even if the API might
        change in the future.
        """
        return None if self._in_portal else self.modId

    def keys(self):
        """Returns all keys of this record."""
        return self._keys

    def values(self):
        """Returns all values of this record."""
        return self._values
