#!/usr/bin/env python

"""High level json utilities"""


# Use simplejson or Python 2.6 json, prefer simplejson.
try:
    import simplejson as json
except ImportError:
    import json


def stringify_json(obj):
    """Make str() copies of all unicode() values from an object obtined
    from json.loads()

    Some libraries demand input as str() objects, but json.loads()
    returns unicode() values. One option is to convert on a need basis
    the unicode strings to str strings, but this is prone to errors:
    one might easily forget to convert one such value.
    """

    # for dicts: make a new dict stringifying keys and values
    if isinstance(obj, dict):
        newobj = {}
        for key, value in obj.iteritems():
            key = str(key)
            newobj[str(key)] = stringify_json(value)
        return newobj

    # return a list with all elems stringifyed
    if isinstance(obj, list):
        return [stringify_json(v) for v in obj]

    # try to convert unicode strings to int/float, or just stringify
    # with str()
    if isinstance(obj, unicode):
        if obj.isdigit():
            return int(obj)
        else:
            try:
                return float(obj)
            except ValueError:
                return str(obj)

    # if all else fails, just return the object as is
    return obj


def _test_stringify_json():
    """A basic test routine for stringify_json"""
    str_json = json.dumps({'a':'b', 'c': {'e':'d'}})
    print str_json
    py_unicode = json.loads(str_json)
    print py_unicode
    py_str = stringify_json(py_unicode)
    print py_str


if __name__ == "__main__":
    _test_stringify_json()


