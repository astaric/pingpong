from django.test import TestCase

from ...player import models as player_models
from ..models import Bracket, Group, GroupMember, GroupToBracketTransition, Match


class GroupMemberTest(TestCase):
    def test_save_fills_brackets(self):
        group, group2 = Group.objects.create(category_id=1), Group.objects.create(category_id=2)
        place, place2 = 1, 2
        bracket = Bracket.objects.create(category_id=1, level=0)
        GroupToBracketTransition.objects.create(group=group, place=place, bracket=bracket)
        GroupToBracketTransition.objects.create(group=group, place=place2, bracket=bracket)
        player1, player2, player3 = [player_models.Player.objects.create(name='', surname='', age=40, gender=0)
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
