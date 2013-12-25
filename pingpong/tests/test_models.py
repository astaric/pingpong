from django.test import TestCase

from pingpong.models import Table, Match, Player, Category, Group, GroupMember


class CategoryCreateGroupsTests(TestCase):
    fixtures = ('create_groups_testdata', )

    def test_create_groups(self):
        category = Category.objects.get(name="Category without clubs")
        leaders = Player.objects.filter(category=category)[:4]

        category.create_groups_from_leaders(leaders)

        groups = Group.objects.filter(category=category).order_by('name')
        self.assertEqual(groups.count(), 4)
        self.assertMemberCountsEqual(groups, [4, 3, 3, 3])

        for leader, group in zip(leaders, groups):
            self.assertIsLeader(leader, group)

        # Players from other groups should not be assigned to groups
        self.assertFalse(GroupMember.objects.exclude(player__category=category).exists())

    def test_create_groups_with_clubs(self):
        category = Category.objects.get(name="Category with clubs")
        players = Player.objects.filter(category=category)
        leaders = players[:4]

        category.create_groups_from_leaders(leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(groups.count(), 4)
        self.assertMemberCountsEqual(groups, [4, 4, 4, 4])

        for group in groups:
            clubs = set(GroupMember.objects.filter(group=group).values_list("player__club", flat=True))
            self.assertEqual(len(clubs), 4)

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
        self.assertEqual(groups.count(), 4)
        self.assertMemberCountsEqual(groups, [4, 3, 3, 3])

        category.create_groups_from_leaders(leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(groups.count(), 4)
        self.assertMemberCountsEqual(groups, [4, 3, 3, 3])

        self.assertEqual(len(leaders.all()), 4)



    def assertMemberCountsEqual(self, groups, member_counts):
        for group, member_count in zip(groups, member_counts):
            self.assertEqual(group.members.count(), member_count)

    def assertIsLeader(self, player, group):
        self.assertTrue(GroupMember.objects.filter(player=player, group=group, leader=True).exists())

    def assertIsMember(self, player, group):
        self.assertTrue(GroupMember.objects.filter(player=player, group=group, leader=False).exists())


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
