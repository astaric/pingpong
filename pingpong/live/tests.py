from django.core.urlresolvers import reverse
from django.test import TestCase


class UpcomingMatchesTests(TestCase):
    fixtures = ['ready_matches']

    def test_shows_ready_group_matches(self):
        resp = self.client.get(reverse('upcoming_matches'))

        self.assertEqual(resp.status_code, 200)
        self.assertIn('group_matches', resp.context)

        group_matches = resp.context['group_matches']

        self.assertEqual(len(group_matches), 2)

    def test_shows_ready_bracket_matches(self):
        resp = self.client.get(reverse('upcoming_matches'))

        self.assertEqual(resp.status_code, 200)
        self.assertIn('bracket_matches', resp.context)

        bracket_matches = resp.context['bracket_matches']

        self.assertEqual(len(bracket_matches), 4)

    def test_shows_ready_double_matches(self):
        resp = self.client.get(reverse('upcoming_matches'))

        self.assertEqual(resp.status_code, 200)
        self.assertIn('doubles_matches', resp.context)

        doubles_matches = resp.context['doubles_matches']

        self.assertEqual(len(doubles_matches), 3)
