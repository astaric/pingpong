from django.core.urlresolvers import reverse

from django.test import TestCase
from pingpong.models import Category


class SignupViewsTestCase(TestCase):
    def test_index_view(self):
        category = Category.objects.create(name="Sample category", gender=0)
        resp = self.client.get(reverse('signup'))

        self.assertEqual(resp.status_code, 200)
        self.assertIn('categories', resp.context)
        self.assertEqual(len(resp.context['categories']), 1)
        for c in resp.context['categories']:
            self.assertEqual(c.name, category.name)


