# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 15:09:52 2018

@author: nnnet
"""

import numpy as np
import sys
import collections
import copy

if sys.version_info[0] >= 3:
    basestring = str
    unicode = str
    long = int
    dict_items = type({}.items())

MAX_UINT32 = np.iinfo(np.uint32).max

def get_value(value_in, hash_type, build_by_features, kwargs=None):
    if isinstance(value_in, type(hash_type)):
        if type(hash_type).__name__ == 'Superminhash':
            value_out = (copy.deepcopy(value_in.values), copy.deepcopy(value_in.q), copy.deepcopy(value_in.p)\
                             , copy.deepcopy(value_in.b), value_in.i, value_in.a)
        else:
            raise Exception('Bad parameter with type.__name__ {0}'.format(type(value_in).__name__))
    elif isinstance(value_in, collections.abc.Iterable):
        value_out = build_by_features(value_in, **kwargs)
    else:
        raise Exception('Bad parameter with type {0}'.format(type(value_in)))

    return value_out

def superminhash_build_by_features(features, length, hash_function, push_function):
    values = [MAX_UINT32] * length  # float64
    q = [-1] * length  # int64
    p = list(range(length))  # uint16
    b = [0] * (length - 1) + [np.int64(length)]  # int64
    i = 0  # int64
    a = length - 1  # uint16
    if isinstance(features, dict):
        features = features.items()

    if sys.version_info[0] >= 3 and isinstance(features, dict_items):
        features = (x[0] for x in features.__iter__())
    elif isinstance(features, zip):
        features = (x[0] for x in features)
    elif isinstance(features[0], tuple):
        features = (x[0] for x in features)

    for feature in features:
        values, q, p, b, i, a = push_function(feature, values, q, p, b, i, a, hash_function)

    return values, q, p, b, i, a
