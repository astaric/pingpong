from django.test import TestCase
from pingpong.helpers import berger_tables


class BergerTableTests(TestCase):
    def test_table_creation(self):
        self.assertEqual(precomputed_berger_tables[4], normalized(berger_tables(4)))
        self.assertEqual(precomputed_berger_tables[6], normalized(berger_tables(6)))
        self.assertEqual(precomputed_berger_tables[8], normalized(berger_tables(8)))


def normalized(xs):
    return [(a + 1, b + 1) for a, b in xs]


precomputed_berger_tables = {
    4: [(1, 4), (2, 3),
        (4, 3), (1, 2),
        (2, 4), (3, 1), ],
    6: [(1, 6), (2, 5), (3, 4),
        (6, 4), (5, 3), (1, 2),
        (2, 6), (3, 1), (4, 5),
        (6, 5), (1, 4), (2, 3),
        (3, 6), (4, 2), (5, 1), ],
    8: [(1, 8), (2, 7), (3, 6), (4, 5),
        (8, 5), (6, 4), (7, 3), (1, 2),
        (2, 8), (3, 1), (4, 7), (5, 6),
        (8, 6), (7, 5), (1, 4), (2, 3),
        (3, 8), (4, 2), (5, 1), (6, 7),
        (8, 7), (1, 6), (2, 5), (3, 4),
        (4, 8), (5, 3), (6, 2), (7, 1), ],
}
