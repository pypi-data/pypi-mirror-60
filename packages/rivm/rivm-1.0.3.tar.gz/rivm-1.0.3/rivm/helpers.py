from collections import ChainMap

from rivm.conversion.constants import INVALID


class DictionaryHelper(object):
    """
    Dictionary utilities.
    """

    @classmethod
    def inverse(cls, dict_):
        """
        Convert the input dictionary and inverse the key/value pairs.
        :param dict_: the input `dict` to convert.
        """
        return {value: key for key, value in dict_.items()}

    @classmethod
    def merge(cls, *dicts):
        """
        Merge mappings together into a single dictionary.
        :param *dicts: any number of `dict` objects to merge.
        """
        return dict(ChainMap(*dicts))


class Mapping(dict):
    """
    Dict subclass to add a fallback value for unmapped values.
    """

    def __missing__(self, key):
        return INVALID
