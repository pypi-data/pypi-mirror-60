import shelve
from hashlib import sha256


class Cache:
    def __init__(self, path="/tmp/ccc-cache"):
        self.path = path

    def get(self, key):
        with shelve.open(self.path) as db:
            try:
                return db[key]
            except KeyError:
                return None

    def set(self, key, value):
        with shelve.open(self.path) as db:
            db[key] = value


def create_identifier(*args):
    """
    Generate a hash from a string.

    :param args: arguments to use for identifier
    :return: hash for a given string
    :rtype: str
    """

    string = ' '.join([str(elem) for elem in args])
    return sha256(str(string).encode()).hexdigest()
