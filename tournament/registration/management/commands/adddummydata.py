import random

from django.core.management.base import BaseCommand
from ...models import Category, Player

category_fields = ('name', 'gender', 'min_age', 'max_age')
categories = (
    ("moski do 45", 0, None, 45),
    ("moski nad 46", 0, 46, None),
    ("zenske do 45", 1, None, 45),
    ("zenske nad 46", 1, 46, None),
)

MALE, FEMALE = 0, 1
male_names = ('Franc', 'Janez', 'Anton', 'Ivan', 'Andrej', 'Marko', 'Peter', 'Matej', 'Branko', 'Luka', 'Bojan')
female_names = ('Marija', 'Ana', 'Maja', 'Irena', 'Mojca', 'Mateja', 'Nina', 'Barbara', 'Andreja', 'Petra', 'Katja')
surnames = ('Novak', 'Horvat', 'Kranjc', 'Mlakar', 'Vidmar', 'Kos', 'Golob', 'Turk', 'Kralj', 'Zupan', 'Bizjak',
            'Bizjak', 'Hribar', 'Kotnik', 'Rozman', 'Petek', 'Kastelic', 'Kolar', 'Koren', 'Zajc', 'Medved')
male_proportion = .7

player_fields = ('name', 'surname', 'gender', 'age')

existing_players = {''}


def players(n=40):
    for _ in xrange(n):
        gender = random.random() > male_proportion
        names = male_names if gender == MALE else female_names

        new_name = False
        while not new_name:
            name = names[random.randint(0, len(names) - 1)]
            surname = surnames[random.randint(0, len(surnames) - 1)]
            new_name = (name + surname) not in existing_players
        else:
            existing_players.add(name + surname)
        age = random.randint(16, 70)
        yield (name, surname, gender, age)


class Command(BaseCommand):
    args = ''
    help = 'Adds dummy data to the database'

    def handle(self, *args, **options):
        for c in categories:
            category = dict(zip(category_fields, c))
            Category(**category).save()

        for p in players():
            player = dict(zip(player_fields, p))
            Player(**player).save()
