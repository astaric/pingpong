from django.test import TestCase

from ..models import Category, Player


class PlayerTestCase(TestCase):
    def test_save_fills_category(self):
        category1 = Category.objects.create(name="M <40", gender=0, max_age=40)
        category2 = Category.objects.create(name="M 41-60", gender=0, min_age=41, max_age=60)
        category3 = Category.objects.create(name="M >61", gender=0, min_age=61)
        category4 = Category.objects.create(name="F", gender=1)

        rest = {'name': '', 'surname': ''}
        new_player = Player.objects.create
        self.assertEqual(new_player(gender=0, age=10, **rest).category, category1)
        self.assertEqual(new_player(gender=0, age=40, **rest).category, category1)
        self.assertEqual(new_player(gender=0, age=41, **rest).category, category2)
        self.assertEqual(new_player(gender=0, age=60, **rest).category, category2)
        self.assertEqual(new_player(gender=0, age=61, **rest).category, category3)
        self.assertEqual(new_player(gender=0, age=99, **rest).category, category3)
        self.assertEqual(new_player(gender=1, age=50, **rest).category, category4)

        # If category is set manually, it should be respected
        self.assertEqual(new_player(gender=0, age=50, category=category1, **rest).category, category1)
        self.assertEqual(new_player(gender=0, age=50, category=category2, **rest).category, category2)
        self.assertEqual(new_player(gender=0, age=50, category=category3, **rest).category, category3)
        self.assertEqual(new_player(gender=0, age=50, category=category4, **rest).category, category4)
