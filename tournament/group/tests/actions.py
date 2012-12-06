import random
import string

from django.test import TestCase

from ...player import models as player_models
from ..models import Group, GroupMember
from .. import actions


class TestCreateGroups(TestCase):
    fixtures = ('create_groups_testdata.json', )

    def test_create_groups(self):
        category = player_models.Category.objects.get(name="Category without clubs")
        leaders = player_models.Player.objects.filter(category=category)[:4]

        actions.create_groups_from_leaders(category.id, leaders)

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
        category = player_models.Category.objects.get(name="Category with clubs")
        players = player_models.Player.objects.filter(category=category)
        leaders = players[:4]

        actions.create_groups_from_leaders(category.id, leaders)

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
        actions.create_groups_from_leaders(None, player_models.Player.objects.none())
        self.assertFalse(Group.objects.exists())
        self.assertFalse(GroupMember.objects.exists())

    def test_create_groups_with_too_many_players_from_same_club(self):
        # If there are more players in a club than there are group leaders,
        # requirement that players from the same club should not be in the
        # same group cannot be fulfilled.
        category = player_models.Category.objects.get(name="Category with too many from the same club")
        players = player_models.Player.objects.filter(category=category)
        leaders = players[:4]

        with self.assertRaises(ValueError):
            actions.create_groups_from_leaders(category.id, leaders)

    def test_recreating_groups(self):
        category = player_models.Category.objects.get(name="Category without clubs")
        leaders = player_models.Player.objects.filter(category=category)[:4]

        actions.create_groups_from_leaders(category.id, leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(len(groups), 4)
        # Check member counts
        self.assertEqual(groups[0].members.count(), 4)
        self.assertEqual(groups[1].members.count(), 3)
        self.assertEqual(groups[2].members.count(), 3)
        self.assertEqual(groups[3].members.count(), 3)

        actions.create_groups_from_leaders(category.id, leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(len(groups), 4)
        # Check member counts
        self.assertEqual(groups[0].members.count(), 4)
        self.assertEqual(groups[1].members.count(), 3)
        self.assertEqual(groups[2].members.count(), 3)
        self.assertEqual(groups[3].members.count(), 3)

        self.assertEqual(len(leaders.all()), 4)


class TestCreateSingleEliminationBracket(TestCase):
    def test_create_single_elimination_bracket(self):
        brackets = actions.create_single_elimination_bracket(1, category_id=1)
        self.assertEqual(len(brackets), 1)
        self.assertEqual(len(brackets[0]), 1)

        brackets = actions.create_single_elimination_bracket(5, category_id=1)
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


class TestCreateTournamentPlacement(TestCase):
    def test_create_tournament_seeds(self):
        self.assertEqual(actions.create_tournament_seeds(4, 2), [0, 3, 1, 2])
        self.assertEqual(actions.create_tournament_seeds(6, 2), [0, None, 3, 4, 1, None, 2, 5])
        self.assertEqual(actions.create_tournament_seeds(6, 3), [0, None, 4, 5, 1, None, 2, 3])
        self.assertEqual(actions.create_tournament_seeds(8, 4), [0, 6, 3, 5, 1, 7, 2, 4])
        self.assertEqual(actions.create_tournament_seeds(10, 5), [0, None, 6, 7, 3, None, 4, None, 1, None, 8, 9, 2, None, 5, None])
        self.assertEqual(actions.create_tournament_seeds(12, 6), [0, None, 7, 8, 3, None, 4, 11, 1, None, 6, 9, 2, None, 5, 10])
        self.assertEqual(actions.create_tournament_seeds(16, 8), [0, 14, 7, 9, 3, 13, 4, 10, 1, 15, 6, 8, 2, 12, 5, 11])


class CreateGroupTransitions(TestCase):

    def test_create_group_transitions(self):
        groups = [x.id for x in [Group.objects.create(category_id=1, name=string.ascii_uppercase[i])
                                 for i in range(5)]]
        for i in range(20):
            p = player_models.Player.objects.create(name='', surname='', age=0, gender=0)
            GroupMember.objects.create(group_id=groups[i % 5], player=p)

        transitions = actions.create_group_transitions(Group.objects.filter(id__in=groups), category_id=1)
        # print "\n".join(map(unicode, transitions))
