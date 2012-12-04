import random


def shuffled(xs):
    xs = list(xs)
    for i in range(len(xs)):
        j = random.randint(i, len(xs) - 1)
        xs[i], xs[j] = xs[j], xs[i]

    return xs
