#TODO
class Foundset(object):
    """A set of record instances from a find query"""

    def __init__(self, records):
        self._records = records

    def next(self):
        return self.__next__()

    def __next__(self):
        try:
            next_record = next(self._records)
            return next_record
        except StopIteration:
            raise StopIteration('no more records in foundset')

    def first(self):
        pass
