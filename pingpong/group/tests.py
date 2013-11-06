from django.core.urlresolvers import reverse
from django.test import TestCase
from pingpong.group.helpers import create_groups_from_leaders
from pingpong.group.models import Group, GroupMember
from pingpong.models import Category, Player


class TestGroupViewsTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test category", gender=0)

    def test_index(self):
        pass

    def test_groups_create(self):
        resp = self.client.get(reverse('groups_create', kwargs=dict(category_id=self.category.id)))

        self.assertEqual(resp.status_code, 200)

    def test_group_edit(self):
        group = Group.objects.create(category=self.category)
        resp = self.client.get(reverse('group_edit', kwargs=dict(group_id=group.id)))

        self.assertEqual(resp.status_code, 200)

    def test_groups_delete(self):

        resp = self.client.get(reverse('delete_groups', kwargs=dict(category_id=self.category.id)))
        self.assertEqual(resp.status_code, 200)


class TestCreateGroups(TestCase):
    fixtures = ('create_groups_testdata.json', )

    def test_create_groups(self):
        category = Category.objects.get(name="Category without clubs")
        leaders = Player.objects.filter(category=category)[:4]

        create_groups_from_leaders(category, leaders)

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
        category = Category.objects.get(name="Category with clubs")
        players = Player.objects.filter(category=category)
        leaders = players[:4]

        create_groups_from_leaders(category, leaders)

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
        create_groups_from_leaders(None, Player.objects.none())
        self.assertFalse(Group.objects.exists())
        self.assertFalse(GroupMember.objects.exists())

    def test_create_groups_with_too_many_players_from_same_club(self):
        # If there are more players in a club than there are group leaders,
        # requirement that players from the same club should not be in the
        # same group cannot be fulfilled.
        category = Category.objects.get(name="Category with too many from the same club")
        players = Player.objects.filter(category=category)
        leaders = players[:4]

        with self.assertRaises(ValueError):
            create_groups_from_leaders(category.id, leaders)

    def test_recreating_groups(self):
        category = Category.objects.get(name="Category without clubs")
        leaders = Player.objects.filter(category=category)[:4]

        create_groups_from_leaders(category, leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(len(groups), 4)
        # Check member counts
        self.assertEqual(groups[0].members.count(), 4)
        self.assertEqual(groups[1].members.count(), 3)
        self.assertEqual(groups[2].members.count(), 3)
        self.assertEqual(groups[3].members.count(), 3)

        create_groups_from_leaders(category, leaders)

        groups = Group.objects.filter(category=category)
        self.assertEqual(len(groups), 4)
        # Check member counts
        self.assertEqual(groups[0].members.count(), 4)
        self.assertEqual(groups[1].members.count(), 3)
        self.assertEqual(groups[2].members.count(), 3)
        self.assertEqual(groups[3].members.count(), 3)

        self.assertEqual(len(leaders.all()), 4)
