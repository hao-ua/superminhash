from __future__ import division, unicode_literals

__all__ = ['utlilits']

import hashlib
import numpy as np
import logging
import sys

if sys.version_info[0] >= 3:
    basestring = str
    unicode = str
    long = int

try:
    from utlilits import get_value, superminhash_build_by_features, MAX_UINT32
except:
    from superminhash.utlilits import get_value, superminhash_build_by_features, MAX_UINT32

def _hash_function(x):
    if isinstance(x, str):
        return int(hashlib.md5(x.encode()).hexdigest(), 16)
    else:
        return int(hashlib.md5(x).hexdigest(), 16)

class Superminhash(object):

    def __init__(self, value, length=64, hash_function=None, log=None):

        self.length = length
        self.values = [MAX_UINT32] * length  # float64
        self.q = [-1] * length  # int64
        self.p = list(range(length))  # uint16
        self.b = [0] * (length - 1) + [np.int64(length)]  # int64
        self.i = 0  # int64
        self.a = length - 1  # uint16

        if hash_function is None:
            self.hash_function = _hash_function
        else:
            self.hash_function = hash_function

        if log is None:
            self.log = logging.getLogger(type(self).__name__.lower())
        elif isinstance(log, logging.Logger):
            self.log = log

        self.values, self.q, self.p, self.b, self.i, self.a = get_value(value, self, superminhash_build_by_features,
                                                   kwargs={'hash_function': self.hash_function,
                                                           'push_function': self._push, 'length': self.length})

    def _push(self, feature, values, q, p, b, i, a, hash_function=None):
        np.random.seed(seed=(hash(feature) if hash_function is None else hash_function(feature)) % MAX_UINT32)
        for j in range(a):
            r = np.float64(np.random.randint(MAX_UINT32)) / MAX_UINT32
            offset = np.random.randint(MAX_UINT32) % np.uint32(np.uint16(len(values)) - j)
            k = np.uint32(j) + offset

            if q[j] != i:
                q[j] = i
                p[j] = np.uint16(j)

            if q[k] != i:
                q[k] = i
                p[k] = np.uint16(k)

            p[j], p[k] = p[k], p[j]
            rj = r + np.float64(j)
            if rj < values[p[j]]:

                jc = np.uint16(min(values[p[j]], np.float64(len(values) - 1)))
                values[p[j]] = rj
                if j < jc:
                    b[jc] -= 1
                    b[j] += 1
                    while b[a] == 0:
                        a -= 1

        i += 1
        return values, q, p, b, i, a

    # // Push ...
    def push(self, feature):
        self.values, self.q, self.p, self.b, self.i, self.a = \
            self._push(feature, self.values, self.q, self.p, self.b, self.i, self.a, self.hash_function)

    # // Similarity ...
    def similarity(self, other):

        if self.length != other.length:
            raise ValueError("signatures not of same length, sign has length %d, while other has length %d" \
                             , len(self.values), len(other.values))

        sim = 0.0
        for i, element in enumerate(self.values):
            if element == other.values[i]:
                sim += 1

        return sim / np.float64(self.length)

    # // Distance ...
    def distance(self, other):

        return 1 - self.similarity(other)