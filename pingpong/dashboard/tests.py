from django.core.urlresolvers import reverse
from django.test import TestCase

from pingpong.dashboard.forms import UpcomingMatchesFromset
from pingpong.models import Match, Group, GroupMember, Category, Player
from pingpong.signup.forms import GroupScoresFormset


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
        match = Match.objects.filter(status=Match.PLAYING)[0]
        self.client.get(reverse('set_score', kwargs=dict(match_id=match.id)))


class DashboardViewsTests(TestCase):
    fixtures = ['ready_matches']

    def test_shows_ready_group_matches(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)

        self.assertIn('group_matches', resp.context)
        self.assertEqual(len(resp.context['group_matches']), 2)
        self.assertIn('bracket_matches', resp.context)
        self.assertEqual(len(resp.context['bracket_matches']), 5)
        self.assertIn('doubles_matches', resp.context)
        self.assertEqual(len(resp.context['doubles_matches']), 1)

    def test_set_group_score(self):
        category = self.create_category()
        self.create_players(category, 4)
        category.create_groups(number_of_groups=1)
        group = Group.objects.get(category=category)
        group_members = GroupMember.objects.order_by('id')
        edit_group_url = reverse('set_group_scores', kwargs=dict(group_id=group.id))

        # Get displays form
        resp = self.client.get(edit_group_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('formset', resp.context)
        self.assertIsInstance(resp.context['formset'], GroupScoresFormset)

        # Posting invalid data redisplays form
        resp = self.client.post(edit_group_url, {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 1,
            'form-MAX_NUM_FORMS': 1,
            'form-0-id': group_members[0].id,
            'form-0-place': 'invalid',
        })
        self.assertEqual(resp.status_code, 200)
        group_members = GroupMember.objects.order_by('id')
        self.assertIsNone(group_members[0].place)
        self.assertIn('formset', resp.context)
        self.assertEqual(len(resp.context['formset'].forms[0].errors['place']), 1)

        # Posting valid data modifies members
        resp = self.client.post(edit_group_url, {
            'form-TOTAL_FORMS': 4,
            'form-INITIAL_FORMS': 4,
            'form-MAX_NUM_FORMS': 4,
            'form-0-id': group_members[0].id,
            'form-0-place': 4,
            'form-1-id': group_members[1].id,
            'form-1-place': 3,
            'form-2-id': group_members[2].id,
            'form-2-place': 2,
            'form-3-id': group_members[3].id,
            'form-3-place': 1,
        })
        self.assertRedirects(resp, reverse('dashboard'))
        group_members = GroupMember.objects.order_by('id')
        self.assertEqual(group_members[0].place, 4)
        self.assertEqual(group_members[1].place, 3)
        self.assertEqual(group_members[2].place, 2)
        self.assertEqual(group_members[3].place, 1)

    @staticmethod
    def create_category():
        return Category.objects.create(type=Category.SINGLE, name="Sample category")

    @staticmethod
    def create_players(category, n):
        return [Player.objects.create(category=category, surname='player%d' % i)
                for i in range(n)]
