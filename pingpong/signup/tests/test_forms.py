from django.test import TestCase
from pingpong.models import Group, Match, Table
from pingpong.signup.forms import GroupScoresFormset


class GroupScoresFormsetTests(TestCase):
    fixtures = ['ready_matches']

    def test_setting_all_places_changes_match_to_complete(self):
        group = Group.objects.get(id=1)
        self.assertEqual(group.match.get().status, Match.READY)

        match = group.match.get()
        match.table = Table.objects.all()[0]
        match.save()
        self.assertEqual(group.match.get().status, Match.PLAYING)

        data = create_empty_match_post_data(group.members.all())
        for i in range(3):
            data['form-%d-place' % i] = str(i+1)
            formset = GroupScoresFormset(data)
            self.assertTrue(formset.is_valid())
            formset.save()
            if i < 2:
                self.assertEqual(group.match.get().status, Match.PLAYING)

        self.assertEqual(group.match.get().status, Match.COMPLETE)

    def test_validation(self):
        group = Group.objects.get(id=1)
        data = create_empty_match_post_data(group.members.all())

        data['form-0-place'] = '1'
        data['form-1-place'] = '1'
        self.assertFalse(GroupScoresFormset(data).is_valid())

        data['form-1-place'] = '5'
        self.assertFalse(GroupScoresFormset(data).is_valid())


def create_empty_match_post_data(matches):
        data = {
            'form-TOTAL_FORMS': len(matches),
            'form-INITIAL_FORMS': len(matches),
            'form-MAX_NUM_FORMS': len(matches),
        }
        for i, match in enumerate(matches):
            data['form-%d-id' % i] = unicode(match.id)
        return data
