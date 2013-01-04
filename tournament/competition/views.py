from django.db.models import Count, Max
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import datastructures
import sys

from . import models
from ..registration import models as player_models


def index(request):
    categories = player_models.Category.objects.all()

    return render(request, "competition/group_index.html", {"categories": list(categories)})


def details(request, category_id):
    category = get_object_or_404(player_models.Category, id=category_id)
    members = models.GroupMember.objects.filter(group__category=category)\
                                        .select_related('player', 'group')\
                                        .order_by('group', '-leader', 'player__surname')

    brackets = []
    for bracket, name, rounds in models.Bracket.objects.filter(category=category)\
                                                       .values_list('id', 'name')\
                                                       .annotate(rounds=Max('bracketslot__level')):
        slots = models.BracketSlot.objects.filter(bracket=bracket)\
                                          .select_related('transition', 'player')\
                                          .prefetch_related('transition__group')\
                                          .order_by('id')
        brackets.append((name, (rounds, slots)))

    return render(request, 'competition/group_details.html', {'category': category,
                                                              'members': members,
                                                              'brackets': brackets})


def upcoming_matches(request):
    matches_with_players = models.BracketSlot.objects.exclude(player=None).exclude(status__gt=1)\
                                                     .values('winner_goes_to_id').annotate(icount=Count('id'))\
                                                     .filter(icount=2).values('winner_goes_to_id')
    matches_query = models.BracketSlot.objects.filter(winner_goes_to_id__in=matches_with_players).select_related('player')
    matches = datastructures.MultiValueDict()
    for match in matches_query:
        matches.appendlist(match.winner_goes_to, match)

    return render(request, 'competition/upcoming_matches.html', {'matches': matches})


match_template = ('',) * 19 + (
    '+-----------------------------------------------------------------+----------+',
    '|                                                                 | Miza     |',
    '+-----------------------------------------------------------------+----------+',
    '|                                                                            |',
    '+----------+----------+----------+----------+----------+----------+----------+',
    '|          |          |          |          |          | Skupaj:  |          |',
    '+----------+----------+----------+----------+----------+----------+----------+',
)


def print_match(request, id=0):
    template = map(list, match_template)
    template[20][2:66] = "Anze Staric".ljust(64)
    template[22][2:66] = "Filip Evgen Trdan Staric".ljust(64)
    template[20][-4:-2] = "15".rjust(2)
    template = map(lambda x: u"".join(x), template)

    return HttpResponse(u"\n".join(template), content_type="text/plain; charset=utf-8")
