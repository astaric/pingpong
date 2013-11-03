# coding=utf-8
import random

from django.core.management.base import BaseCommand, make_option
from pingpong.models import Category, Player

category_fields = ('name', 'description', 'gender', 'min_age', 'max_age')
category_data = (
    ("M <40",   u"Moški do 39",      0, None, 40),
    ("M 40-50", u"Moški 40 do 49",   0, 40,   50),
    ("M 50-60", u"Moški 50 do 59",   0, 50,   60),
    ("M 60-70", u"Moški 60 do 69",   0, 60,   70),
    ("M >70",   u"Moški nad 70",     0, 70,   None),
    ("Z <40",   u"Ženske do 39",     1, None, 40),
    ("Z >40",   u"Ženske nad 40",    1, 40,   None),
    ("DM <50",  u"Dvojice Moški do 49",  0, None, 50),
    ("DM <50",  u"Dvojice Moški nad 50", 0, 50,   None),
    ("DZ",      u"Dvojice Ženske",       1, 50,   None),
)

MALE, FEMALE = 0, 1
male_names = ('Franc', 'Janez', 'Anton', 'Ivan', 'Andrej', 'Marko', 'Peter', 'Matej', 'Branko', 'Luka', 'Bojan')
female_names = ('Marija', 'Ana', 'Maja', 'Irena', 'Mojca', 'Mateja', 'Nina', 'Barbara', 'Andreja', 'Petra', 'Katja')
surnames = ('Novak', 'Horvat', 'Kranjc', 'Mlakar', 'Vidmar', 'Kos', 'Golob', 'Turk', 'Kralj', 'Zupan', 'Bizjak',
            'Bizjak', 'Hribar', 'Kotnik', 'Rozman', 'Petek', 'Kastelic', 'Kolar', 'Koren', 'Zajc', 'Medved')
male_proportion = .7

player_fields = ('name', 'surname', 'gender', 'age')

existing_players = {''}


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-a', '--all',
                    action='store_true',
                    default=False,
                    help="Create players, categories and groups."),
        make_option('-p', '--players',
                    type='int',
                    help='Create N players. Implies -c.'),
        make_option('-c', '--categories',
                    type='int',
                    help='Create categories.'),
    )
    args = ''
    help = 'Adds dummy data to the database'

    def handle(self, *args, **options):
        print options
        if options['all']:
            options['players'] = 40
            options['categories'] = 7
            options['groups'] = 1

        categories = ()
        if options['categories']:
            Category.objects.all().delete()
            categories = [Category.objects.create(**dict(zip(category_fields, category_data[c])))
                          for c in xrange(options['categories'])]

        if options['players']:
            Player.objects.all().delete()
            n_players = options['players']
            players = []
            if categories:
                for category in categories:
                    n = random.randint(0, n_players) if category != categories[-1] else n_players
                    players.extend(self.create_players(n=n, category=category))
                    n_players -= n

    @staticmethod
    def create_players(n=40, category=None):
        for _ in xrange(n):
            gender = random.random() > male_proportion if category is None else category.gender
            names = male_names if gender == MALE else female_names

            new_name = False
            while not new_name:
                name = names[random.randint(0, len(names) - 1)]
                surname = surnames[random.randint(0, len(surnames) - 1)]
                new_name = (name + surname) not in existing_players
            else:
                existing_players.add(name + surname)
            age = random.randint(16, 90) if category is None else random.randint(category.min_age or 16,
                                                                                 category.max_age or 90)
            yield Player.objects.create(**dict(zip(player_fields, (name, surname, gender, age))))
