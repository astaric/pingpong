import re

from django.core import urlresolvers
from django.db.models import Count, Max
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import datastructures
from django.contrib.auth.decorators import login_required

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
    brackets = models.Bracket.objects.filter(category=category)\
                                     .annotate(rounds=Max('bracketslot__level'))

    return render(request, 'competition/group_details.html', {'category': category,
                                                              'members': members,
                                                              'brackets': brackets, })


def match_index(request, filter=''):
    matches = models.BracketSlot.objects.exclude(player=None)
    if filter == 'upcoming':
        matches = matches.filter(status=0)
    elif filter == 'current':
        matches = matches.filter(status=1)
    matches = matches.values('winner_goes_to_id').annotate(icount=Count('id')).filter(icount=2)\
                     .values('winner_goes_to_id')
    matches_query = models.BracketSlot.objects.filter(winner_goes_to_id__in=matches)\
                                              .select_related('player', 'bracket__category')
    matches = datastructures.MultiValueDict()
    for match in matches_query:
        matches.appendlist(match.winner_goes_to_id, match)

    available_tables = models.Table.objects.annotate(count=Count('bracketslot'))\
                                           .filter(count=0)\
                                           .order_by('sort_order')
    return render(request, 'competition/match_index.html',
                  {
                      'matches': matches,
                      'tables': tables,
                      'available_tables': available_tables,
                  })


def tables(request):
    tables = models.Table.objects.prefetch_related('bracketslot_set')
    return render(request, 'competition/tables.html', {'tables': tables})


@login_required(login_url='/admin')
def set_table(request):
    match_id = request.POST.get('match_id', None)
    table_id = request.POST.get('table_id', None)

    if match_id and table_id:
        for slot in models.BracketSlot.objects.filter(winner_goes_to=match_id):
            slot.table_id = table_id
            slot.save()

    return redirect(urlresolvers.reverse("upcoming_matches"))

score_re = re.compile(r'(\d+)[^\d]+(\d+)')


@login_required(login_url='/admin')
def set_score(request):
    match_id = request.POST.get('match_id', None)
    score = request.POST.get('score', None)

    if match_id and score:
        scores = score_re.match(score)
        if scores:
            slots = models.BracketSlot.objects.filter(winner_goes_to=match_id)
            for slot, score in zip(slots, scores.groups()):
                slot.score = int(score)
                slot.save()

    return redirect(urlresolvers.reverse('current_matches'))


def match_details(request, match_id):
    return render(request, 'competition/match_details.html', {'players': range(16)})

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
