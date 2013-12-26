from contextlib import contextmanager
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
        with debug_sql:
            fun(*args, **kwargs)
    return wrapped()
