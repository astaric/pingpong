from django.core.urlresolvers import reverse
from django.test import TestCase


class PlayerViewsTestCase(TestCase):
    fixtures = ('competitionviews_testdata.json',)

    def test_index(self):
        resp = self.client.get(reverse('group_index'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('categories', resp.context)
        self.assertEqual(len(resp.context['categories']), 1)

    def test_details(self):
        resp = self.client.get(reverse('group_details', kwargs={'category_id': '1'}))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('category', resp.context)
        self.assertIn('members', resp.context)
        self.assertIn('brackets', resp.context)

        category = resp.context['category']
        self.assertEqual(category.id, 1)
        members = resp.context['members']
        self.assertEqual(len(members), 8)
        self.assertEqual([m.group.id for m in members], [1, 1, 1, 1, 2, 2, 2, 2])

        # Ensure that non-existing category throws a 404.
        resp = self.client.get(reverse('group_details', kwargs={'category_id': '99'}))
        self.assertEqual(resp.status_code, 404)

    def test_upcoming_matches(self):
        resp = self.client.get(reverse('upcoming_matches'))
        self.assertIn('matches', resp.context)

        matches = resp.context['matches']
        self.assertEqual(len(matches), 4)
        brackets = [m.winner_goes_to_id for m in matches]
        self.assertEqual(brackets, [2, 2, 5, 5])


