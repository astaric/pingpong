from django.core.urlresolvers import reverse
from django.test import TestCase

from pingpong.models import Category, Group


class TestGroupViewsTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test category", gender=0)

    def test_index(self):
        pass

    def test_groups_create(self):
        resp = self.client.get(reverse('groups', kwargs=dict(category_id=self.category.id)))

        self.assertEqual(resp.status_code, 200)

    def test_group_edit(self):
        group = Group.objects.create(category=self.category)
        resp = self.client.get(reverse('edit_group', kwargs=dict(category_id=group.category_id,
                                                                 group_id=group.id)))

        self.assertEqual(resp.status_code, 200)

    def test_groups_delete(self):

        resp = self.client.get(reverse('delete_groups', kwargs=dict(category_id=self.category.id)))
        self.assertEqual(resp.status_code, 200)
