# -*- coding: utf-8 -*-

from benedict.dicts.io import IODict
from benedict.dicts.keylist import KeylistDict
from benedict.dicts.keypath import KeypathDict
from benedict.dicts.parse import ParseDict
from benedict.utils import dict_util


class benedict(IODict, KeypathDict, ParseDict):

    def __init__(self, *args, **kwargs):
        """
        Constructs a new instance.
        """
        super(benedict, self).__init__(*args, **kwargs)

    def clean(self, strings=True, collections=True):
        """
        Clean the current dict instance removing all empty values: None, '', {}, [], ().
        If strings or collections (dict, list, set, tuple) flags are False,
        related empty values will not be deleted.
        """
        dict_util.clean(self, strings=strings, collections=collections)

    def clone(self):
        """
        Creates and return a clone of the current dict instance (deep copy).
        """
        return benedict(dict_util.clone(self),
            keypath_separator=self._keypath_separator)

    def copy(self):
        """
        Creates and return a copy of the current instance (shallow copy).
        """
        return benedict(super(benedict, self).copy(),
            keypath_separator=self._keypath_separator)

    def deepcopy(self):
        """
        Alias of 'clone' method.
        """
        return self.clone()

    def deepupdate(self, other, *args):
        """
        Alias of 'merge' method.
        """
        self.merge(other, *args)

    def dump(self, data=None):
        """
        Return a readable string representation of any dict/list.
        This method can be used both as static method or instance method.
        """
        return dict_util.dump(data or self)

    def filter(self, predicate):
        """
        Return a new filtered dict using the given predicate function.
        Predicate function receives key, value arguments and should return a bool value.
        """
        return dict_util.filter(self, predicate)

    def flatten(self, separator='_'):
        """
        Return a new flattened dict using the given separator
        to join nested dict keys to flatten keypaths.
        """
        return dict_util.flatten(self, separator)

    def invert(self, flat=False):
        """
        Return a new inverted dict, where values become keys and keys become values.
        Since multiple keys could have the same value, each value will be a list of keys.
        If flat is True each value will be a single value (use this only if values are unique).
        """
        return dict_util.invert(self, flat)

    def items_sorted_by_keys(self, reverse=False):
        """
        Return items (key/value list) sorted by keys.
        If reverse is True, the list will be reversed.
        """
        return dict_util.items_sorted_by_keys(self, reverse=reverse)

    def items_sorted_by_values(self, reverse=False):
        """
        Return items (key/value list) sorted by values.
        If reverse is True, the list will be reversed.
        """
        return dict_util.items_sorted_by_values(self, reverse=reverse)

    def keypaths(self):
        """
        Return a list of all keypaths in the dict.
        """
        sep = self._keypath_separator or '.'
        return dict_util.keypaths(self, separator=sep)

    def merge(self, other, *args):
        """
        Merge one or more dict objects into current instance (deepupdate).
        Sub-dictionaries will be merged toghether.
        """
        dict_util.merge(self, other, *args)

    def move(self, key_src, key_dest):
        """
        Move a dict instance value item from 'key_src' to 'key_dst'.
        If key_dst exists, its value will be overwritten.
        """
        dict_util.move(self, key_src, key_dest)

    def remove(self, keys, *args):
        """
        Remove multiple keys from the current dict instance.
        It is possible to pass a single key or more keys (as list or *args).
        """
        dict_util.remove(self, keys, *args)

    def rename(self, key, key_new):
        """
        Rename a dict item key from 'key' to 'key_new'.
        If key_new exists, a KeyError will be raised.
        """
        dict_util.rename(self, key, key_new)

    def search(self, query, in_keys=True, in_values=True, exact=False, case_sensitive=False):
        """
        Search and return a list of items (dict, key, value, ) matching the given query.
        """
        return dict_util.search(self, query, in_keys, in_values, exact, case_sensitive)

    def standardize(self):
        """
        Standardize all dict keys (e.g. 'Location Latitude' -> 'location_latitude').
        """
        dict_util.standardize(self)

    def subset(self, keys, *args):
        """
        Return a new dict subset for the given keys.
        It is possible to pass a single key or multiple keys (as list or *args).
        """
        return dict_util.subset(self, keys, *args)

    def swap(self, key1, key2):
        """
        Swap items values at the given keys.
        """
        dict_util.swap(self, key1, key2)

    def traverse(self, callback):
        """
        Traverse the current dict instance (including nested dicts),
        and pass each item (dict, key, value) to the callback function.
        """
        dict_util.traverse(self, callback)

    def unflatten(self, separator='_'):
        """
        Return a new unflattened dict using the given separator
        to split dict keys to nested keypaths.
        """
        return dict_util.unflatten(self, separator)

    def unique(self):
        """
        Remove duplicated values from the current dict instance.
        """
        dict_util.unique(self)
