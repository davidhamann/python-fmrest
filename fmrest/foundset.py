"""Foundset class for collections of Records"""

class Foundset(object):
    """A set of Record instances

    Foundsets are used for both find results and portal data (related records)
    """

    def __init__(self, records):
        """Initialize the Foundset class.

        Parameters
        ----------
        records : generator
            Generator of Record instances representing the records in a foundset or
            related records from a portal.
        """
        self._records = records
        self._records_fetched = [] # we will store each record in here once iterated over
        self._all_fetched = False

    def __iter__(self):
        """Make foundset iterable

        Return iter for list of records already fetched from generator, or self
        to start/continue fetching from generator via __next__.
        """

        if self._all_fetched:
            return iter(self._records_fetched)

        return self

    def __next__(self):
        """Fetch records from generator and cache them in list for potential later iterations"""
        try:
            record = next(self._records)
            self._records_fetched.append(record)
            return record
        except StopIteration:
            self._all_fetched = True
            raise StopIteration("Reached end of foundset.")

    def __repr__(self):
        return '<Foundset fetched_records={}>'.format(len(self._records_fetched))
