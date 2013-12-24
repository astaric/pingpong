from django.utils import unittest
from pingpong.models import Table, Match, Player


class MatchTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_assigning_table_sets_start_time(self):
        table = self.create_table()
        match = self.create_match_with_players()

        self.assertIsNone(match.start_time)

        match.table = table
        match.save()

        self.assertIsNotNone(match.start_time)

    def test_assigning_result_sets_end_time(self):
        match = self.create_match_with_players()
        match.table = self.create_table()
        match.save()
        self.assertIsNone(match.end_time)

        match.player1_score = 1
        match.player2_score = 3
        match.save()

        self.assertIsNotNone(match.end_time)

    def create_table(self):
        return Table.objects.create(display_order=1)

    def create_match(self):
        return Match.objects.create()

    def create_match_with_players(self):
        match = self.create_match()
        match.player1 = Player.objects.create()
        match.player2 = Player.objects.create()
        match.save()
        return match

if __name__ == '__main__':
    unittest.main()
