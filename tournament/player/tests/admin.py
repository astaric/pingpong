from django.test import TestCase

from ..admin import player as player_admin
from ..models import Player, Group

def set_category(*args):
    for (player, category) in args:
        player.category_id = category
        player.save()

def get_category(x): return x.category_id

class ActionsTestCase(TestCase):
    fixtures = ('player_admin_testdata.json', )
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

        player_admin.refresh_categories(None, None, male_under_40)
        self.assertEqual(map(get_category, male_under_40.all()), map(get_category, correct_male_under_40))
        self.assertEqual(map(get_category, male_over_40.all()), map(get_category, changed_male_over_40))
        self.assertEqual(map(get_category, female.all()), map(get_category, changed_female))

        player_admin.refresh_categories(None, None, male_over_40)
        self.assertEqual(list(male_under_40.all()), correct_male_under_40)
        self.assertEqual(list(male_over_40.all()), correct_male_over_40)
        self.assertEqual(list(female.all()), changed_female)

        player_admin.refresh_categories(None, None, female)
        self.assertEqual(list(male_under_40.all()), correct_male_under_40)
        self.assertEqual(list(male_over_40.all()), correct_male_over_40)
        self.assertEqual(list(female.all()), correct_female)

    def test_create_groups(self):
        leaders = Player.objects.filter(id__in=(9, 10))

        player_admin.create_groups(None, None, leaders)
        groups = Group.objects.filter(category=1)
        self.assertEqual(len(groups), 2)
        id1, id2 = [x.id for x in groups]
        self.assertEqual(len(Player.objects.filter(group=id1)), 3)
        self.assertEqual(len(Player.objects.filter(group=id2)), 2)
        # Check that leaders are marked as such
        self.assertTrue(Player.objects.get(id=9).group_leader)
        self.assertTrue(Player.objects.get(id=10).group_leader)
        # Players from other groups should not be assigned to groups
        self.assertEqual(len(Player.objects.exclude(category=1).exclude(group=None)), 0)
        self.assertEqual(len(Player.objects.exclude(category=1).filter(group_leader=True)), 0)

    def test_create_groups_bad(self):
        player_admin.create_groups(None, None, Player.objects.none())
        self.assertEqual(len(Player.objects.exclude(group=None)), 0)
        self.assertEqual(len(Player.objects.filter(group_leader=True)), 0)
