from django.core.urlresolvers import reverse

from django.test import TestCase
from pingpong.models import Category, Player


class SignupViewsTestCase(TestCase):
    def test_index_view(self):
        resp = self.client.get(reverse('signup'))

        self.assertRedirects(resp, reverse('category_add'))

        category = Category.objects.create(name="Sample category", gender=0)
        resp = self.client.get(reverse('signup'))

        self.assertRedirects(resp, reverse('category_edit', kwargs=dict(id=category.id)))

    def test_edit_category_view(self):
        expected_category = Category.objects.create(name="Sample category", gender=0)
        unexpected_category = Category.objects.create(name="Different category", gender=0)
        expected_players = self.create_players(expected_category, 3)
        unexpected_players = self.create_players(unexpected_category, 3)
        category_edit_url = reverse('category_edit', kwargs=dict(id=expected_category.id))

        resp = self.client.get(category_edit_url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('formset', resp.context)
        formset_instances = [f.instance for f in resp.context['formset'].forms]
        for p in expected_players:
            self.assertIn(p, formset_instances)
        for p in unexpected_players:
            self.assertNotIn(p, formset_instances)

        post_data = {
            'category-name': 'New name',
            'category-descritpion': 'New description',
            'player-0-name': 'X',
            'player-0-surname': 'Y',
            'player-0-club': 'C',
            'player-TOTAL_FORMS': 1,
            'player-INITIAL_FORMS': 0,
            'player-MAX_NUM_FORMS': 10
        }
        resp = self.client.post(category_edit_url, post_data)

        self.assertRedirects(resp, category_edit_url)
        self.assertEqual(Player.objects.filter(name='X', surname='Y', club='C', category=expected_category).count(), 1)

    def test_add_category_view(self):
        # GET renders add_category form
        add_category_url = reverse('category_add')
        resp = self.client.get(add_category_url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)

        # POST creates the category
        resp = self.client.post(add_category_url, dict(name='Name',
                                                       description='Description',
                                                       gender=0))
        self.assertEqual(Category.objects.count(), 1)
        category = Category.objects.all()[0]
        self.assertRedirects(resp, reverse('category_edit', kwargs=dict(id=category.id)))

    def test_delete_category(self):
        category = Category.objects.create(name="Sample category", gender=0)
        delete_category_url = reverse('category_delete', kwargs=dict(id=category.id))
        self.create_players(category, 3)

        # GET displays a confirmation page
        resp = self.client.get(delete_category_url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('category', resp.context)
        self.assertEqual(resp.context['category'], category)

        # Answering no redirects to edit page
        resp = self.client.post(delete_category_url, dict(no='No'))

        self.assertRedirects(resp, reverse('category_edit', kwargs=dict(id=category.id)))

        # Answering yes deletes category and redirects to index
        resp = self.client.post(reverse('category_delete', kwargs=dict(id=category.id)), dict(yes='Yes'))

        self.assertRedirects(resp, reverse('signup'), target_status_code=302)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Player.objects.count(), 0)

    @staticmethod
    def create_players(category, n):
        return [Player.objects.create(category=category)
                for i in range(n)]
