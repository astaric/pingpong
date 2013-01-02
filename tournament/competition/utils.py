from itertools import izip_longest
import random


def shuffled(xs):
    xs = list(xs)
    return random.sample(xs, len(xs))


def group(iterable, n):
    return izip_longest(*(iterable[i::n] for i in range(n)))


def alternate(*iterables):
    MISSING = object()
    for tuple in izip_longest(*iterables, fillvalue=MISSING):
        for element in tuple:
            if element is not MISSING:
                yield element


def invert(xs, length=0):
    ys = [None] * (length or len(xs))
    for i, s in enumerate(xs):
        if s < len(ys):
            ys[s] = i
    return ys
