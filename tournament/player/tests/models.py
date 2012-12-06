from django.test import TestCase

from ..models import Bracket, Category, Group, GroupMember, GroupToBracketTransition, Match, Player


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


class GroupMemberTest(TestCase):
    def test_save_fills_brackets(self):
        group, group2 = Group.objects.create(category_id=1), Group.objects.create(category_id=2)
        place, place2 = 1, 2
        bracket = Bracket.objects.create(category_id=1, level=0)
        GroupToBracketTransition.objects.create(group=group, place=place, bracket=bracket)
        GroupToBracketTransition.objects.create(group=group, place=place2, bracket=bracket)
        player1, player2, player3 = [Player.objects.create(name='', surname='', age=40, gender=0)
                                     for i in range(3)]

        # Adding a groupmember with correct group and place should also create a Match.
        member = GroupMember.objects.create(group=group, place=place, player=player1)

        match = Match.objects.filter(bracket=bracket, player=player1)
        self.assertTrue(match.exists())
        # As match already exists, new one should not be created.
        member.save()
        self.assertEqual(match.count(), 1)

        # Adding a player without a place should not create a match.
        member2 = GroupMember.objects.create(group=group, player=player2)
        match = Match.objects.filter(bracket=bracket, player=player2)
        self.assertFalse(match.exists())

        # Adding a place should cause match creation.
        member2.place = place2
        member2.save()
        self.assertTrue(match.exists())
