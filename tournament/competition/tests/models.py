from django.test import TestCase

from ...registration import models as player_models
from ..models import BracketSlot, Group, GroupMember


class GroupMemberTest(TestCase):
    fixtures = ('groupmember_testdata.json',)

    def test_save_fills_brackets(self):
        place1, place2, place3 = 1, 2, 3
        group, = Group.objects.all()
        p1, p2, p3 = player_models.Player.objects.all()

        # Adding a groupmember with correct group and place should also fill a BracketSlot
        member = GroupMember.objects.create(group=group, place=place1, player=p1)

        slot = BracketSlot.objects.filter(player=p1)
        self.assertTrue(slot.exists())
        # As player should only be present in one slot, new one should not be created.
        member.save()
        self.assertEqual(slot.count(), 1)

        # Adding a player without a place should not create a match.
        member2 = GroupMember.objects.create(group=group, player=p2)
        slot = BracketSlot.objects.filter(player=p2)
        self.assertFalse(slot.exists())

        # Adding a place should cause match creation.
        member2.place = place2
        member2.save()
        self.assertTrue(slot.exists())

        # Correcting player's place should update slot
        member2.place = place1
        member2.save()
        slot.exists()
        self.assertEqual(slot.count(), 1)

    def test_saving_a_player_without_a_match_in_bracket_automatically_promotes_him(self):
        place = 3
        group, = Group.objects.all()
        p1, p2, p3 = player_models.Player.objects.all()
        member = GroupMember.objects.create(group=group, place=place, player=p1)

        slots = BracketSlot.objects.filter(player=p1)
        self.assertTrue(slots.exists())
        self.assertEqual(slots.count(), 2)
        self.assertTrue([slot for slot in slots if slot.level != 0])
