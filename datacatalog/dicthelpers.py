import copy
import datetime
from collections import Mapping, MutableMapping
from attrdict import AttrDict
import jsondiff

LISTKEYS = ['child_of']
FILTERKEYS = ('_id', 'uuid', 'properties', 'measurements_ids',
              'measurements', 'files', 'samples')
class DictionaryMergeError(Exception):
    pass

def __data_merge(a, b):
    aa = AttrDict(a)
    bb = AttrDict(b)
    ab = dict(aa + bb)
    return ab

def right_merge(right_value, left_value):
    merged = None
    if isinstance(right_value, list) and isinstance(left_value, list):
        merged = list(set(left_value) | set(right_value))
        return merged
    else:
        return right_value

def data_merge(left, right, setkeys=LISTKEYS):
    """
    Merge two mappings objects together, combining overlapping Mappings,
    and favoring right-values
    left: The left Mapping object.
    right: The right (favored) Mapping object.
    NOTE: This is not commutative (merge(a,b) != merge(b,a)).
    """
    merged = {}
    left_keys = frozenset(left)
    right_keys = frozenset(right)
    # Items only in the left Mapping
    for key in left_keys - right_keys:
        merged[key] = left[key]
    # Items only in the right Mapping
    for key in right_keys - left_keys:
        merged[key] = right[key]
    # in both
    for key in left_keys & right_keys:
        left_value = left[key]
        right_value = right[key]
        if (isinstance(left_value, Mapping) and
                isinstance(right_value, Mapping)):  # recursive merge
            merged[key] = data_merge(left_value, right_value)
        else:  # overwrite with right value
            if key in setkeys:
                merged[key] = right_merge(left_value, right_value)
            else:
                merged[key] = right_value
    return merged


def data_merge_diff(a, b, filters=FILTERKEYS):
    ab = data_merge(a, b)
    df = json_diff(a, b, filters=FILTERKEYS)
    return ab, df

def json_diff(j1, j2, filters=FILTERKEYS):
    j1 = copy.deepcopy(j1)
    j2 = copy.deepcopy(j2)
    for f in filters:
        try:
            j1.pop(f)
        except KeyError:
            pass
        try:
            j2.pop(f)
        except KeyError:
            pass
    resp = jsondiff.diff(j1, j2, marshal=True)
    return resp

def filter_dict(target_dict, keys_to_filter):
    """Filters key(s) from top level of a dict
    Args:
        target_dict (dict): the dictionary to filter
        keys_to_filter (list, tuple, str): set of keys to filter
    Returns:
        A filtered copy of target_dict
    """
    assert isinstance(target_dict, dict)
    d = copy.deepcopy(target_dict)
    # Let keys_to_filter be a single string or a tuple of values
    if isinstance(keys_to_filter, str):
        keys_to_filter = [keys_to_filter]
    elif isinstance(keys_to_filter, tuple):
        keys_to_filter = list(keys_to_filter)
    elif keys_to_filter is None:
        keys_to_filter = []
    # Do the filtering
    for kf in keys_to_filter:
        try:
            d.pop(kf)
        except KeyError:
            pass
    return d

def dict_compare(a, b):
    '''Lexically compare values of all primitives in a pair of dicts'''
    # FIXME: This is not a great implementation
    aa = '.'.join(sorted([str(v)
                          for v in flatten(a).values() if is_primitive(v)]))
    bb = '.'.join(sorted([str(u)
                          for u in flatten(b).values() if is_primitive(u)]))
    if aa == bb:
        return False
    else:
        return True

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = '{0}{1}{2}'.format(parent_key, sep, k) if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # apply itself to each element of the list - that's it!
            items.append((new_key, map(flatten, v)))
        else:
            items.append((new_key, v))
    return dict(items)

def is_primitive(pyobj):
    """Determine if pyobj is one of (what other languages would deem) a primitive"""
    if type(pyobj) in (int, float, bool, str, bytes):
        return True
    else:
        return False

# Reference: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9#gistcomment-1986197
def dict_merge(dct, merge_dct, add_keys=True):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    This version will return a copy of the dictionary and leave the original
    arguments untouched.
    The optional argument ``add_keys``, determines whether keys which are
    present in ``merge_dict`` but not ``dct`` should be included in the
    new dict.
    Args:
        dct (dict) onto which the merge is executed
        merge_dct (dict): dct merged into dct
        add_keys (bool): whether to add new keys
    Returns:
        dict: updated dict
    """
    dct = copy.deepcopy(dct)
    if not add_keys:
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], Mapping)):
            dct[k] = dict_merge(dct[k], merge_dct[k], add_keys=add_keys)
        else:
            dct[k] = merge_dct[k]
    return dct

def list_merge(lst, merge_lst):
    # Does not preserve order
    return list(set(lst) | set(merge_lst))


def __data_merge(aa, bb):
    """Merges b into a and returns merged result
    NOTE: Tuples and arbitrary objects are not handled as it is ambiguous what should happen
    """
    key = None
    a = copy.deepcopy(aa)
    b = copy.deepcopy(bb)
    try:
        if a is None or isinstance(a, (str, int, float, bool, bytes, datetime.datetime)):
            # border case for first run or if a is a primitive
            if b is not None:
                a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a = list_merge(a, b)
            else:
                # append to list
                a = list_merge(a, b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise DictionaryMergeError(
                    'Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise DictionaryMergeError(
                'NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError as e:
        raise DictionaryMergeError(
            'TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a


def _dictcompare(a, b, section=None):
    # Used to compare database records as dicts
    # https://stackoverflow.com/a/48652830
    # This was not working for the comparisons I needed to make but am keeping
    # it around for reference
    return [(c, d, g, section) if all(not isinstance(i, dict) for i in [d, g]) and d != g else None if all(not isinstance(i, dict) for i in [d, g]) and d == g else _dictcompare(d, g, c) for [c, d], [h, g] in zip(a.items(), b.items())]
