from django.core.urlresolvers import reverse
from django.test import TestCase
from pingpong.dashboard.forms import UpcomingMatchesFromset, CurrentMatchForm
from pingpong.models import Match, Table


class UpcomingMatchesViewTests(TestCase):
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

        self.assertEqual(len(bracket_matches), 5)

    def test_shows_ready_double_matches(self):
        resp = self.client.get(reverse('upcoming_matches'))

        self.assertEqual(resp.status_code, 200)
        self.assertIn('doubles_matches', resp.context)

        doubles_matches = resp.context['doubles_matches']

        self.assertEqual(len(doubles_matches), 1)


class UpcomingMatchesFromsetTests(TestCase):
    fixtures = ['ready_matches']

    def test_no_change(self):
        group_matches = Match.ready_group_matches()
        data = create_empty_match_post_data(group_matches)

        formset = UpcomingMatchesFromset(data)
        self.assertTrue(formset.is_valid())

        formset.save()
        self.assertEqual(len(group_matches), len(Match.ready_group_matches()))

    def test_assigning_table(self):
        group_matches = list(Match.ready_group_matches())
        data = create_empty_match_post_data(group_matches)
        data['form-0-table'] = u'5'

        formset = UpcomingMatchesFromset(data)
        self.assertTrue(formset.is_valid())

        formset.save()
        self.assertEqual(len(group_matches) - 1, len(Match.ready_group_matches()))

    def test_assigning_multiple_tables(self):
        data = create_empty_match_post_data(Match.ready_group_matches())
        data['form-0-table'] = u'5'
        data['form-1-table'] = u'6'

        formset = UpcomingMatchesFromset(data)
        self.assertTrue(formset.is_valid())

        formset.save()
        self.assertEqual(0, len(Match.ready_group_matches()))
        pass

    def test_assigning_same_table_to_different_matches(self):
        data = create_empty_match_post_data(Match.ready_group_matches())
        data['form-0-table'] = u'4'
        data['form-1-table'] = u'4'

        formset = UpcomingMatchesFromset(data)

        self.assertEqual(formset.is_valid(), False)


class CurrentMatchFormTests(TestCase):
    fixtures = ['current_matches']

    def test_can_validate_empty_score(self):
        form = CurrentMatchForm({'id': 4})
        self.assertTrue(form.is_valid())

    def test_can_parse_different_score_formats(self):
        data = {'id': 4, 'score': '5:2'}

        form = CurrentMatchForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.player1_score, 5)
        self.assertEqual(form.instance.player2_score, 2)

        data['score'] = '5 2'
        form = CurrentMatchForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.player1_score, 5)
        self.assertEqual(form.instance.player2_score, 2)

        data['score'] = '5.2'
        form = CurrentMatchForm(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.player1_score, 5)
        self.assertEqual(form.instance.player2_score, 2)

        # Negative tests
        data['score'] = '5'
        form = CurrentMatchForm(data)
        self.assertFalse(form.is_valid())

        data['score'] = 'x y'
        form = CurrentMatchForm(data)
        self.assertFalse(form.is_valid())

        data['score'] = '1:b'
        form = CurrentMatchForm(data)
        self.assertFalse(form.is_valid())


class CurrentMatchesViewTests(TestCase):
    fixtures = ['current_matches']

    def test_current_matches(self):
        self.client.get(reverse('current_matches'))

    def test_setting_scores(self):
        data = create_empty_match_post_data(Match.current_matches())

        self.client.post(reverse('current_matches'), data)


def create_empty_match_post_data(matches):
        data = {
            'form-TOTAL_FORMS': len(matches),
            'form-INITIAL_FORMS': len(matches),
            'form-MAX_NUM_FORMS': len(matches),
        }
        for i, match in enumerate(matches):
            data['form-%d-id' % i] = unicode(match.id)
        return data


class SetScoreViewTests(TestCase):
    fixtures = ['current_matches']

    def test_shows_table_info(self):
        table = Table.objects.filter(all_matches__isnull=True)[0:1].get()
        self.client.get(reverse('set_score', kwargs=dict(table_id=table.id)))
