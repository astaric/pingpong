from contextlib import contextmanager
from collections import deque
import random
from django.conf import settings
from django.db import connection
from django.template import Template, Context
import sys


@contextmanager
def debug_sql():
    settings.DEBUG = True
    connection.queries = []
    try:
        yield
    finally:
        time = sum([float(q['time']) for q in connection.queries])
        t = Template("{{count}} quer{{count|pluralize:\"y,ies\"}} in {{time}} seconds:\n\n{% for sql in sqllog %}[{{forloop.counter}}] {{sql.time}}s: {{sql.sql|safe}}{% if not forloop.last %}\n\n{% endif %}{% endfor %}")
        print >> sys.stderr, t.render(Context({'sqllog': connection.queries, 'count': len(connection.queries), 'time': time}))

        # Empty the query list between TestCases.


def debug_sql_wrapper(fun):
    def wrapped(*args, **kwargs):
        with debug_sql():
            fun(*args, **kwargs)
    return wrapped


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


def shuffled(xs):
    xs = list(xs)
    return random.sample(xs, len(xs))
