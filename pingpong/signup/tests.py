from django.core.urlresolvers import reverse

from django.test import TestCase
from pingpong.models import Category, Player, Group, Match, Table
from pingpong.signup.forms import GroupScoresFormset


class SignupViewsTestCase(TestCase):
    def test_index_view(self):
        resp = self.client.get(reverse('signup'))

        self.assertRedirects(resp, reverse('category_add'))

        category = Category.objects.create(name="Sample category", gender=0)
        resp = self.client.get(reverse('signup'))

        self.assertRedirects(resp, reverse('category_edit', kwargs=dict(category_id=category.id)))

    def test_edit_category_view(self):
        expected_category = Category.objects.create(name="Sample category", gender=0)
        unexpected_category = Category.objects.create(name="Different category", gender=0)
        expected_players = self.create_players(expected_category, 3)
        unexpected_players = self.create_players(unexpected_category, 3)
        category_edit_url = reverse('category_edit_players', kwargs=dict(category_id=expected_category.id))

        resp = self.client.get(category_edit_url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('players_formset', resp.context)
        formset_instances = [f.instance for f in resp.context['players_formset'].forms]
        for p in expected_players:
            self.assertIn(p, formset_instances)
        for p in unexpected_players:
            self.assertNotIn(p, formset_instances)

        post_data = {
            'category-name': 'New name',
            'category-descritpion': 'New description',
            'players-0-name': 'X',
            'players-0-surname': 'Y',
            'players-0-club': 'C',
            'players-TOTAL_FORMS': 1,
            'players-INITIAL_FORMS': 0,
            'players-MAX_NUM_FORMS': 10
        }
        resp = self.client.post(category_edit_url, post_data)

        self.assertRedirects(resp, reverse('category', kwargs=dict(category_id=expected_category.id)))
        self.assertEqual(Player.objects.filter(name='X', surname='Y', club='C', category=expected_category).count(), 1)

    def test_add_category_view(self):
        # GET renders add_category form
        add_category_url = reverse('category_add')
        resp = self.client.get(add_category_url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)

        # POST creates the category
        resp = self.client.post(add_category_url, dict(type='0',
                                                       name='Name',
                                                       description='Description',
                                                       gender=0))
        self.assertEqual(Category.objects.count(), 1)
        category = Category.objects.all()[0]
        self.assertRedirects(resp, reverse('category_edit', kwargs=dict(category_id=category.id)))

    def test_delete_category(self):
        category = Category.objects.create(name="Sample category", gender=0)
        delete_category_url = reverse('category_delete', kwargs=dict(category_id=category.id))
        self.create_players(category, 3)

        # GET displays a confirmation page
        resp = self.client.get(delete_category_url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('object_description', resp.context)
        self.assertIn(str(category.name), resp.context['object_description'])

        # Answering no redirects to edit page
        resp = self.client.post(delete_category_url, dict(no='No'))

        self.assertRedirects(resp, reverse('category_edit', kwargs=dict(category_id=category.id)))

        # Answering yes deletes category and redirects to index
        resp = self.client.post(reverse('category_delete', kwargs=dict(category_id=category.id)), dict(yes='Yes'))

        self.assertRedirects(resp, reverse('signup'), target_status_code=302)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Player.objects.count(), 0)

    @staticmethod
    def create_players(category, n):
        return [Player.objects.create(category=category)
                for i in range(n)]


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
