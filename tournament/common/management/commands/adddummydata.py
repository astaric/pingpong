# coding=utf-8
import random

from django.core.management.base import BaseCommand
from ....registration.models import Category, Player
from ....competition.models import Table, Group, GroupMember
from ....competition.actions import create_groups_from_leaders, create_brackets

category_fields = ('name', 'description', 'gender', 'min_age', 'max_age')
categories = (
    ("M <40",   u"Moški do 39",      0, None, 40),
    ("M 40-50", u"Moški 40 do 50",   0, 40,   50),
    ("M 50-60", u"Moški 50 do 60",   0, 50,   60),
    ("M 60-70", u"Moški 60 do 70",   0, 60,   70),
    ("M >70",   u"Moški nad 70",     0, 70,   None),
    ("Z <40",   u"Ženske do 40",     1, None, 40),
    ("Z >40",   u"Ženske nad 40",    1, 40,   None),
    ("D <50",   u"Dvojice do 50",    2, None, 50),
    ("D <50",   u"Dvojice nad 50",   2, 50,   None),
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

        # create groups
        category = Category.objects.all()[0]
        n_players = Player.objects.filter(category=category).count()
        n_groups = (n_players - 1) // 4 + 1
        leader_ids = Player.objects.filter(category=category).values_list('id', flat=True)[:n_groups]
        create_groups_from_leaders(category.id, Player.objects.filter(id__in=leader_ids))
        create_brackets(category)

        # create group results
        for group in Group.objects.all():
            for i, member in enumerate(GroupMember.objects.filter(group=group)):
                member.place = i + 1
                member.save()

        for id in [10, 11, 12, 7, 8, 9, 4, 5, 6, 1, 2, 3]:
            Table(name='Table %d' % (id), sort_order=id).save()
