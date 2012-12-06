import random
import string

from django.test import TestCase

from ..admin.player import PlayerAdmin
from ..models import Category, Player, Group, GroupMember


def set_category(*args):
    for (player, category) in args:
        player.category_id = category
        player.save()


def get_category(x):
    return x.category_id


class ActionsTestCase(TestCase):
    fixtures = ('player_admin_testdata.json', )

    def setUp(self):
        self.admin = PlayerAdmin(Player, None)

    def test_refresh_categories(self):
        male_under_40 = Player.objects.filter(gender=0, age__lt=40)
        male_over_40 = Player.objects.filter(gender=0, age__gte=40)
        female = Player.objects.filter(gender=1)
        male1 = Player.objects.get(id=1)
        male2 = Player.objects.get(id=2)
        female1 = Player.objects.get(id=3)

        correct_male_under_40 = list(male_under_40.all())
        correct_male_over_40 = list(male_over_40.all())
        correct_female = list(female.all())

        # Change some categories to incorrect ones
        set_category((male1, 2), (male2, 3), (female1, 1))
        # Ensure that the players are really changed
        self.assertNotEqual(map(get_category, male_under_40.all()), map(get_category, correct_male_under_40))
        self.assertNotEqual(map(get_category, male_over_40.all()), map(get_category, correct_male_over_40))
        self.assertNotEqual(map(get_category, female.all()), map(get_category, correct_female))
        changed_male_over_40 = list(male_over_40)
        changed_female = list(female)

        self.admin.refresh_categories(None, male_under_40)
        self.assertEqual(map(get_category, male_under_40.all()), map(get_category, correct_male_under_40))
        self.assertEqual(map(get_category, male_over_40.all()), map(get_category, changed_male_over_40))
        self.assertEqual(map(get_category, female.all()), map(get_category, changed_female))

        self.admin.refresh_categories(None, male_over_40)
        self.assertEqual(list(male_under_40.all()), correct_male_under_40)
        self.assertEqual(list(male_over_40.all()), correct_male_over_40)
        self.assertEqual(list(female.all()), changed_female)

        self.admin.refresh_categories(None, female)
        self.assertEqual(list(male_under_40.all()), correct_male_under_40)
        self.assertEqual(list(male_over_40.all()), correct_male_over_40)
        self.assertEqual(list(female.all()), correct_female)

    def test_refresh_category_works_for_queries_filtered_by_category(self):
        players = Player.objects.filter(category=1)
        player_ids = list(players.values_list('id', flat=True))

        self.admin.refresh_categories(None, players)

        for player in Player.objects.filter(id__in=player_ids):
            self.assertEqual(player.category_id, 1)

    def test_create_groups(self):
        leaders = Player.objects.filter(id__in=(5, 6))

        self.admin.create_groups_from_leaders(None, leaders)
        groups = Group.objects.filter(category=2)
        self.assertEqual(len(groups), 2)
        id1, id2 = [x.id for x in groups]
        self.assertEqual(len(GroupMember.objects.filter(group=id1)), 2)
        self.assertEqual(len(GroupMember.objects.filter(group=id2)), 2)
        # Check that leaders are marked as such
        self.assertTrue(GroupMember.objects.get(player_id=5).leader)
        self.assertTrue(GroupMember.objects.get(player_id=6).leader)
        # Players from other groups should not be assigned to groups
        self.assertFalse(GroupMember.objects.exclude(player__category=2).exists())

    def test_create_groups_with_clubs(self):
        random.seed(0)
        category = Category.objects.create(name="Category", gender=0)
        players = [Player.objects.create(name="New", surname="Player",
                                         age=0, gender=0,
                                         club=str(club),
                                         category=category)
                   for _ in range(4) for club in range(4)]
        leaders = Player.objects.filter(id__in=[x.id for x in players][:4])

        self.admin.create_groups_from_leaders(None, leaders)
        for group in Group.objects.filter(category=category):
            clubs_in_group = GroupMember.objects.filter(group=group).values_list("player__club", flat=True)
            self.assertEqual(len(clubs_in_group), 4)
            self.assertEqual(len(clubs_in_group), len(set(clubs_in_group)))

    def test_create_groups_bad(self):
        self.admin.create_groups_from_leaders(None, Player.objects.none())
        self.assertFalse(Group.objects.exists())
        self.assertFalse(GroupMember.objects.exists())

        # If there are more players in a club than there are group leaders,
        # requirement that players from the same club should not be in the
        # same group cannot be fulfilled.
        category = Category.objects.create(name="Category", gender=0)
        players = [Player.objects.create(name="New", surname="Player",
                                         age=0, gender=0,
                                         club=str("1"),
                                         category=category) for i in range(2)]
        leaders = Player.objects.filter(id=players[0].id)
        with self.assertRaises(ValueError):
            self.admin.create_groups_from_leaders(None, leaders)

    def test_recreating_groups_does_not_delete_players(self):
        leaders = Player.objects.filter(id__in=(5, 6))

        self.admin.create_groups_from_leaders(None, leaders)
        self.admin.create_groups_from_leaders(None, leaders)

        self.assertEqual(len(leaders.all()), 2)

    def test_create_single_elimination_bracket(self):
        brackets = self.admin.create_single_elimination_bracket(1, category_id=1)
        self.assertEqual(len(brackets), 1)
        self.assertEqual(len(brackets[0]), 1)

        brackets = self.admin.create_single_elimination_bracket(5, category_id=1)
        self.assertEqual(len(brackets), 5)
        self.assertEqual(len(brackets[0]), 16)
        self.assertEqual(len(brackets[1]), 8)
        self.assertEqual(len(brackets[2]), 4)
        self.assertEqual(len(brackets[3]), 2)
        self.assertEqual(len(brackets[4]), 1)

        for level, brackets in enumerate(brackets[:-1]):
            for bracket in brackets:
                self.assertEqual(bracket.level, level)
                self.assertEqual(bracket.winner_goes_to.level, level + 1)

    def test_create_group_transitions(self):
        groups = [x.id for x in [Group.objects.create(category_id=1, name=string.ascii_uppercase[i])
                                 for i in range(5)]]
        for i in range(20):
            Player.objects.create(name="New", surname="Player",
                                  age=0, gender=0)

        transitions = self.admin.create_group_transitions(Group.objects.filter(id__in=groups), category_id=1)
        # print "\n".join(map(unicode, transitions))
