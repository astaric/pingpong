from django.core.urlresolvers import reverse
from django.test import TestCase
from pingpong.live.forms import UpcomingMatchesFromset
from pingpong.models import Match


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


class UpcomingMatchesFromsetTests(TestCase):
    fixtures = ['ready_matches']

    def test_no_change(self):
        group_matches = Match.ready_group_matches()
        data = self.create_empty_post_data()

        formset = UpcomingMatchesFromset(data)
        self.assertTrue(formset.is_valid())

        formset.save()
        self.assertEqual(len(group_matches), len(Match.ready_group_matches()))

    def test_assigning_table(self):
        group_matches = list(Match.ready_group_matches())
        data = self.create_empty_post_data()
        data['form-0-table'] = u'5'

        formset = UpcomingMatchesFromset(data)
        self.assertTrue(formset.is_valid())

        formset.save()
        self.assertEqual(len(group_matches) - 1, len(Match.ready_group_matches()))

    def test_assigning_multiple_tables(self):
        data = self.create_empty_post_data()
        data['form-0-table'] = u'5'
        data['form-1-table'] = u'6'

        formset = UpcomingMatchesFromset(data)
        self.assertTrue(formset.is_valid())

        formset.save()
        self.assertEqual(0, len(Match.ready_group_matches()))
        pass

    def test_assigning_same_table_to_different_matches(self):
        data = self.create_empty_post_data()
        data['form-0-table'] = u'4'
        data['form-1-table'] = u'4'

        formset = UpcomingMatchesFromset(data)

        self.assertEqual(formset.is_valid(), False)

    def create_empty_post_data(self):
        matches = Match.ready_group_matches()
        data = {
            'form-TOTAL_FORMS': len(matches),
            'form-INITIAL_FORMS': len(matches),
            'form-MAX_NUM_FORMS': len(matches),
        }
        for i, match in enumerate(Match.ready_group_matches()):
            data['form-%d-id' % i] = unicode(match.id)
        return data