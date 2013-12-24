import string
from django.test import TestCase
from pingpong.bracket.helpers import create_tournament_seeds, create_brackets, levels, create_single_elimination_bracket_slots
from pingpong.bracket.models import Bracket
from pingpong.group.models import Group, GroupMember
from pingpong.models import Player, Category


class TestCreateBrackets(TestCase):
    def test_create_single_elimination_bracket(self):
        bracket = Bracket.objects.create(category_id=1)
        slots = create_single_elimination_bracket_slots(bracket, 3)
        self.assertEqual(len(slots), 2)
        self.assertEqual(len(slots[0]), 4)
        self.assertEqual(len(slots[1]), 2)

        bracket = Bracket.objects.create(category_id=1)
        slots = create_single_elimination_bracket_slots(bracket, 5)
        self.assertEqual(len(slots), 3)
        self.assertEqual(len(slots[0]), 8)
        self.assertEqual(len(slots[1]), 4)
        self.assertEqual(len(slots[2]), 2)

        for level, slots in enumerate(slots[:-1]):
            for slot in slots:
                self.assertEqual(slot.level, 3-level)
                self.assertEqual(slot.winner_goes_to.level, (3 - level) - 1)

    def test_create_tournament_seeds(self):
        seeds = create_tournament_seeds
        self.assertEqual(seeds(1, 1), [0, None])
        self.assertEqual(seeds(4, 2), [0, 3, 1, 2])
        self.assertEqual(seeds(6, 2), [0, None, 3, 4, 1, None, 2, 5])
        self.assertEqual(seeds(6, 3), [0, None, 4, 5, 1, None, 2, 3])
        self.assertEqual(seeds(8, 4), [0, 6, 3, 5, 1, 7, 2, 4])
        self.assertEqual(seeds(10, 5), [0, None, 6, 7, 3, None, 4, None, 1, None, 8, 9, 2, None, 5, None])
        self.assertEqual(seeds(12, 6), [0, None, 7, 8, 3, None, 4, 11, 1, None, 6, 9, 2, None, 5, 10])
        self.assertEqual(seeds(16, 8), [0, 14, 7, 9, 3, 13, 4, 10, 1, 15, 6, 8, 2, 12, 5, 11])

    def test_create_group_transitions(self):
        category = Category.objects.create(name='', gender=0)
        groups = [x.id for x in [Group.objects.create(category=category, name=string.ascii_uppercase[i])
                                 for i in range(5)]]
        for i in range(20):
            p = Player.objects.create(name='', surname='', category=category)
            GroupMember.objects.create(group_id=groups[i % 5], player=p)

        transitions = create_brackets(category)
        # print "\n".join(map(unicode, transitions))

    def test_levels(self):
        self.assertEqual(levels(1), 1)
        self.assertEqual(levels(2), 2)
        self.assertEqual(levels(3), 3)
        self.assertEqual(levels(4), 3)
        self.assertEqual(levels(5), 4)
        self.assertEqual(levels(7), 4)
        self.assertEqual(levels(8), 4)
        self.assertEqual(levels(9), 5)
        self.assertEqual(levels(15), 5)
        self.assertEqual(levels(16), 5)
        self.assertEqual(levels(17), 6)