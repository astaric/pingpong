import random
import string

from django.test import TestCase

from ..admin import PlayerAdmin
from ..models import Category, Player


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
