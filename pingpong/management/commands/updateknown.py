from django.core.management.base import BaseCommand
from pingpong.models import KnownClub, Player, KnownPlayer


class Command(BaseCommand):
    args = ''
    help = 'Update known players based on the currently registered players.'

    def handle(self, *args, **options):
        KnownClub.objects.all().delete()
        KnownPlayer.objects.all().delete()

        for c, in Player.objects.values_list('club').distinct('club'):
            if c:
                KnownClub.objects.create(name=c)

        for p in Player.objects.filter(category__type=0):
            KnownPlayer.objects.create(name=p.name, surname=p.surname, club=p.club)

