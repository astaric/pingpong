from django.test import TestCase


def get_pk(x):
    return x.pk


class PlayerViewsTestCase(TestCase):
    fixtures = ('player_views_testdata.json',)

    def test_index(self):
        resp = self.client.get('/player/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('categories' in resp.context)
        self.assertEqual(len(resp.context['categories']), 1)
        self.assertEqual(len(resp.context['categories'][0]), 2)
        category, players = resp.context['categories'][0]
        self.assertEqual(category.pk, 1)
        self.assertEqual(map(get_pk, players), [1, 2])
        self.assertEqual(category.name, 'under 45')
        self.assertEqual(players[0].name, 'Janez')
        self.assertEqual(players[0].surname, 'Medved')
        self.assertEqual(players[1].name, 'Andrej')
        self.assertEqual(players[1].surname, 'Novak')

    def test_details(self):
        resp = self.client.get('/player/1/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('player' in resp.context)
        player = resp.context['player']
        self.assertEqual(player.name, 'Janez')
        self.assertEqual(player.surname, 'Medved')

        # Ensure that non-existing player throws a 404.
        resp = self.client.get('/player/99/')
        self.assertEqual(resp.status_code, 404)
