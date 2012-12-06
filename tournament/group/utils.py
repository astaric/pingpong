from itertools import izip_longest
import random


def shuffled(xs):
    xs = list(xs)
    for i in range(len(xs)):
        j = random.randint(i, len(xs) - 1)
        xs[i], xs[j] = xs[j], xs[i]

    return xs


def group(iterable, n):
    return izip_longest(*(iterable[i::n] for i in range(n)))


def alternate(iterable1, iterable2):
    MISSING = object()

    for a, b in izip_longest(iterable1, iterable2, fillvalue=MISSING):
        if a is not MISSING:
            yield a
        if b is not MISSING:
            yield b
