from django.test import TestCase
from pingpong.models import Table, Match, Player, Category, Group, GroupMember


class CategoryCreateGroupsTests(TestCase):
    fixtures = ('create_groups_testdata', )

    def test_create_groups(self):
        category = Category.objects.get(name="Category without clubs")
        leaders = Player.objects.filter(category=category)[:4]

        category.create_groups_from_leaders(leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(len(groups), 4)
        # Check member counts
        self.assertEqual(groups[0].members.count(), 4)
        self.assertEqual(groups[1].members.count(), 3)
        self.assertEqual(groups[2].members.count(), 3)
        self.assertEqual(groups[3].members.count(), 3)

        # Check that leaders are marked as such
        self.assertTrue(GroupMember.objects.get(player=leaders[0]).leader)
        self.assertTrue(GroupMember.objects.get(player=leaders[1]).leader)
        self.assertTrue(GroupMember.objects.get(player=leaders[2]).leader)
        self.assertTrue(GroupMember.objects.get(player=leaders[3]).leader)

        # Players from other groups should not be assigned to groups
        self.assertFalse(GroupMember.objects.exclude(player__category=category).exists())

    def test_create_groups_with_clubs(self):
        category = Category.objects.get(name="Category with clubs")
        players = Player.objects.filter(category=category)
        leaders = players[:4]

        category.create_groups_from_leaders(leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(len(groups), 4)
        # Check member counts
        self.assertEqual(groups[0].members.count(), 4)
        self.assertEqual(groups[1].members.count(), 4)
        self.assertEqual(groups[2].members.count(), 4)
        self.assertEqual(groups[3].members.count(), 4)

        # Each group should have members from all 4 clubs
        member_clubs = lambda group: GroupMember.objects.filter(group=group).values_list("player__club", flat=True)
        self.assertEqual(len(set(member_clubs(groups[0]))), 4)
        self.assertEqual(len(set(member_clubs(groups[1]))), 4)
        self.assertEqual(len(set(member_clubs(groups[2]))), 4)
        self.assertEqual(len(set(member_clubs(groups[3]))), 4)

    def test_create_groups_with_no_leaders(self):
        category = Category.objects.get(name="Category with clubs")

        with self.assertRaises(ValueError):
            category.create_groups_from_leaders(Player.objects.none())

    def test_create_groups_with_too_many_players_from_same_club(self):
        # If there are more players in a club than there are group leaders,
        # requirement that players from the same club should not be in the
        # same group cannot be fulfilled.
        category = Category.objects.get(name="Category with too many from the same club")
        players = Player.objects.filter(category=category)
        leaders = players[:4]

        with self.assertRaises(ValueError):
            category.create_groups_from_leaders(leaders)

    def test_recreating_groups(self):
        category = Category.objects.get(name="Category without clubs")
        leaders = Player.objects.filter(category=category)[:4]

        category.create_groups_from_leaders(leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(len(groups), 4)
        # Check member counts
        self.assertEqual(groups[0].members.count(), 4)
        self.assertEqual(groups[1].members.count(), 3)
        self.assertEqual(groups[2].members.count(), 3)
        self.assertEqual(groups[3].members.count(), 3)

        category.create_groups_from_leaders(leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(len(groups), 4)
        # Check member counts
        self.assertEqual(groups[0].members.count(), 4)
        self.assertEqual(groups[1].members.count(), 3)
        self.assertEqual(groups[2].members.count(), 3)
        self.assertEqual(groups[3].members.count(), 3)

        self.assertEqual(len(leaders.all()), 4)


class MatchTests(TestCase):

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
