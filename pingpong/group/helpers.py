from collections import deque
import random


def shuffled(xs):
    xs = list(xs)
    return random.sample(xs, len(xs))


def berger_tables(n):
    m = n if n % 2 == 0 else n + 1
    m2 = m // 2
    players = deque(range(m))

    matches = []
    for i in range(m - 1):
        for a, b in zip(list(players)[:m2], list(players)[m2:][::-1]):
            if a < n and b < n:
                matches.append((a, b))
        if i % 2 == 0:
            x = players.pop()
            players.rotate(m2 - 2)
            players.appendleft(x)
        else:
            x = players.popleft()
            players.rotate(-m2 + 1)
            players.append(x)

    return matches
