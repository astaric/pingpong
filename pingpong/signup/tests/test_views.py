from django.core.urlresolvers import reverse
from django.test import TestCase
from pingpong.bracket.helpers import create_brackets, create_pair_brackets
from pingpong.bracket.models import Bracket, BracketSlot

from pingpong.models import Category, Player, Group, GroupMember
from pingpong.signup.forms import CategoryAddForm, CategoryEditForm, PlayerFormSet


class SignupViewsTestCase(TestCase):
    def test_category_list_view(self):
        resp = self.client.get(reverse('category_list'))
        self.assertIn('categories', resp.context)

    def test_category_details_view(self):
        category = self.create_category()
        category_details_url = lambda cid: reverse('category', kwargs=dict(category_id=cid))

        # View should return category in context
        resp = self.client.get(category_details_url(category.id))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('category', resp.context)
        self.assertEqual(resp.context['category'].id, category.id)

        # Missing category should return 404
        resp = self.client.get(category_details_url(99))
        self.assertEqual(resp.status_code, 404)

    def test_add_category_view(self):
        add_category_url = reverse('category_add')

        # GET adds form to context
        resp = self.client.get(add_category_url)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)
        self.assertIsInstance(resp.context['form'], CategoryAddForm)

        # POST with invalid data redisplays category
        resp = self.client.post(add_category_url, dict(
            type='0', description='Description'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)
        self.assertEqual(len(resp.context['form'].errors['name']), 1)

        # POST creates the category
        resp = self.client.post(add_category_url, dict(
            type='0', name='Name', description='Description'))
        self.assertEqual(Category.objects.count(), 1)
        category = Category.objects.all()[0]
        self.assertRedirects(resp, reverse('category_edit', kwargs=dict(category_id=category.id)))

    def test_edit_category_view(self):
        category = self.create_category()
        category_edit_url = reverse('category_edit', kwargs=dict(category_id=category.id))

        # GET returns form in context
        resp = self.client.get(category_edit_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('category_fields_form', resp.context)
        self.assertIsInstance(resp.context['category_fields_form'], CategoryEditForm)

        # POST with invalid data redisplays form.
        resp = self.client.post(category_edit_url, {})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('category_fields_form', resp.context)
        self.assertEqual(len(resp.context['category_fields_form'].errors['name']), 1)

        # POST edits category and redirects
        resp = self.client.post(category_edit_url, {'category_fields-name': 'NewName'})
        self.assertRedirects(resp, reverse('category', kwargs={'category_id': category.id}))
        category = Category.objects.get(id=category.id)
        self.assertEqual(category.name, 'NewName')

        # Missing category returns 404
        resp = self.client.get(reverse('category_edit', kwargs={'category_id': 99}))
        self.assertEqual(resp.status_code, 404)

    def test_edit_category_players(self):
        category = self.create_category()
        category_url = reverse('category', kwargs=dict(category_id=category.id))
        edit_players_url = reverse('category_edit_players', kwargs=dict(category_id=category.id))

        # Get sets players formset
        resp = self.client.get(edit_players_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('players_formset', resp.context)
        self.assertIsInstance(resp.context['players_formset'], PlayerFormSet)

        # Post with invalid data redisplays formset
        resp = self.client.post(edit_players_url, {'players-TOTAL_FORMS': 1,
                                                   'players-INITIAL_FORMS': 0,
                                                   'players-MAX_NUM_FORMS': 1,
                                                   'players-0-name': 'name'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('players_formset', resp.context)
        self.assertEqual(len(resp.context['players_formset'].forms[0].errors['surname']), 1)
        self.assertEqual(Player.objects.count(), 0)

        # Post adds new players
        resp = self.client.post(edit_players_url, {'players-TOTAL_FORMS': 1,
                                                   'players-INITIAL_FORMS': 0,
                                                   'players-MAX_NUM_FORMS': 1,
                                                   'players-0-name': 'name',
                                                   'players-0-surname': 'surname',
                                                   'players-0-club': 'club',
                                                   })
        self.assertRedirects(resp, category_url)
        players = Player.objects.filter(category=category)
        self.assertEqual(players.count(), 1)
        player = players.get()
        self.assertEqual(player.name, 'name')
        self.assertEqual(player.surname, 'surname')
        self.assertEqual(player.club, 'club')

        # Post edits existing players
        resp = self.client.post(edit_players_url, {'players-TOTAL_FORMS': 1,
                                                   'players-INITIAL_FORMS': 1,
                                                   'players-MAX_NUM_FORMS': 1,
                                                   'players-0-id': player.id,
                                                   'players-0-name': 'new name',
                                                   'players-0-surname': 'surname',
                                                   'players-0-club': 'new club',
                                                   })
        self.assertRedirects(resp, category_url)
        players = Player.objects.filter(category=category)
        self.assertEqual(players.count(), 1)
        player = players.get()
        self.assertEqual(player.name, 'new name')
        self.assertEqual(player.surname, 'surname')
        self.assertEqual(player.club, 'new club')

        # Post deletes players
        resp = self.client.post(edit_players_url, {'players-TOTAL_FORMS': 1,
                                                   'players-INITIAL_FORMS': 1,
                                                   'players-MAX_NUM_FORMS': 1,
                                                   'players-0-id': player.id,
                                                   'players-0-DELETE': '1',
                                                   })
        self.assertRedirects(resp, category_url)
        players = Player.objects.filter(category=category)
        self.assertEqual(players.count(), 0)

        # 404 on missing category
        resp = self.client.get(reverse('category_edit_players', kwargs={'category_id': 99}))
        self.assertEqual(resp.status_code, 404)

    def test_delete_category(self):
        category = Category.objects.create(name="Sample category", gender=0)
        delete_category_url = reverse('category_delete', kwargs=dict(category_id=category.id))
        players = self.create_players(category, 3)

        # GET displays a confirmation page
        resp = self.client.get(delete_category_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('object_description', resp.context)
        self.assertIn(str(category.name), resp.context['object_description'])
        self.assertIn('related_objects', resp.context)
        related_objects = [o[1] for o in resp.context['related_objects']]
        for p in players:
            self.assertIn(p, related_objects)

        # Answering no redirects to edit page
        resp = self.client.post(delete_category_url, dict(no='No'))

        self.assertRedirects(resp, reverse('category_edit', kwargs=dict(category_id=category.id)))
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Player.objects.count(), 3)

        # Answering yes deletes category and redirects to index
        resp = self.client.post(delete_category_url, dict(yes='Yes'))

        self.assertRedirects(resp, reverse('category_list'))
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Player.objects.count(), 0)

    def test_delete_groups(self):
        category = Category.objects.create(name="Sample category", gender=0)
        self.create_players(category, 16)
        category.create_groups(number_of_groups=4)
        delete_groups_url = reverse('delete_groups', kwargs=dict(category_id=category.id))
        edit_category_url = reverse('category_edit', kwargs=dict(category_id=category.id))
        groups = Group.objects.all()
        group_members = GroupMember.objects.all()

        # GET displays a confirmation page
        resp = self.client.get(delete_groups_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('object_description', resp.context)
        self.assertSetEqual(set(groups), set(resp.context['object_description']))
        self.assertIn('related_objects', resp.context)
        related_objects = [o[1] for o in resp.context['related_objects']]
        for m in group_members:
            self.assertIn(m, related_objects)

        # Answering no redirects to edit page
        resp = self.client.post(delete_groups_url, dict(no='No'))

        self.assertRedirects(resp, edit_category_url)
        self.assertEqual(Group.objects.count(), 4)
        self.assertEqual(GroupMember.objects.count(), 16)

        # Answering yes deletes groups and redirects to index
        resp = self.client.post(delete_groups_url, dict(yes='Yes'))

        self.assertRedirects(resp, edit_category_url)
        self.assertEqual(Group.objects.count(), 0)
        self.assertEqual(GroupMember.objects.count(), 0)

    def test_delete_brackets(self):
        category = Category.objects.create(name="Sample category", gender=0)
        self.create_players(category, 16)
        create_pair_brackets(category)
        delete_brackets_url = reverse('delete_brackets', kwargs=dict(category_id=category.id))
        edit_category_url = reverse('category_edit', kwargs=dict(category_id=category.id))
        bracket = Bracket.objects.get()
        bracket_slots = BracketSlot.objects.all()

        # GET displays a confirmation page
        resp = self.client.get(delete_brackets_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('object_description', resp.context)
        self.assertIn(bracket, resp.context['object_description'])
        self.assertIn('related_objects', resp.context)
        related_objects = [o[1] for o in resp.context['related_objects']]
        for bs in bracket_slots:
            self.assertIn(bs, related_objects)

        # Answering no redirects to edit page
        resp = self.client.post(delete_brackets_url, dict(no='No'))

        self.assertRedirects(resp, edit_category_url)
        self.assertEqual(Bracket.objects.count(), 1)
        self.assertEqual(BracketSlot.objects.count(), 31)

        # Answering yes deletes brackets and redirects to index
        resp = self.client.post(delete_brackets_url, dict(yes='Yes'))

        self.assertRedirects(resp, edit_category_url)
        self.assertEqual(Bracket.objects.count(), 0)
        self.assertEqual(BracketSlot.objects.count(), 0)


    @staticmethod
    def create_category():
        return Category.objects.create(type=Category.SINGLE, name="Sample category")

    @staticmethod
    def create_players(category, n):
        return [Player.objects.create(category=category, surname='player%d' % i)
                for i in range(n)]
