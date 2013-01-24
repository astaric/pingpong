import re

from django.core import urlresolvers
from django.db.models import Count, Max
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import datastructures
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from . import models
from . import actions
from ..registration import models as player_models


def group_index(request):
    category_members = {
        category: []
        for category in player_models.Category.objects.annotate(player_count=Count('player'))
    }
    for member in models.GroupMember.objects\
                                    .order_by('group__category', 'group', 'place', '-leader', 'player__surname')\
                                    .prefetch_related('group', 'group__category', 'player'):
        category_members[member.group.category].append(member)

    return render(request, "competition/group_index.html", {"category_members": category_members.items()})


def group_details(request, category_id):
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
        if not models.BracketSlot.objects.filter(table_id=table_id).exists():
            for slot in models.BracketSlot.objects.filter(winner_goes_to=match_id):
                slot.table_id = table_id
                slot.save()
        else:
            messages.add_message(request, messages.ERROR, "Table (%s) is already occupied." % table_id)
    else:
        messages.add_message(request, messages.ERROR, "Invalid request")

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
        else:
            messages.add_message(request, messages.ERROR, "Invalid score. (%s)" % score)
    else:
        messages.add_message(request, messages.ERROR, "Invalid request")

    return redirect(urlresolvers.reverse('current_matches'))

@login_required(login_url='/admin')
def set_places(request):
    try:
        members = [(name.split('_')[1], placement)
                   for name, placement in request.POST.items()
                   if name.startswith('member_')]
    except ValueError:
        members = ()
        messages.add_message(request, messages.ERROR, "Invalid request")

    member_id = members[0][0] if len(members) else None
    max_placement = models.GroupMember.with_same_group_as(member_id).count()
    for member_id, placement in members:
        valid = True
        if placement.isdigit():
            placement = int(placement)
            if not 1 <= placement <= max_placement:
                valid = False
        elif placement == '':
            placement = None
        else:
            valid = False

        if valid:
            members = models.GroupMember.objects.filter(id=member_id)
            for member in members:
                member.place = placement
                member.save()
        else:
            messages.add_message(request, messages.ERROR, "Invalid placement (%s)" % placement)

    return redirect(urlresolvers.reverse('group_index'))

player_re = re.compile(r'player_([\d]+)_group')
def set_leaders(request):
    category_id = request.POST['category_id']

    leaders = []
    for name, value in request.POST.items():
        match = player_re.match(name)
        if match and value:
            id, = match.groups()
            leaders.append((value, id))

    leaders.sort()
    if leaders:
        leaders = [player_models.Player.objects.get(id=id)
                   for group, id in leaders]
        actions.create_groups_from_leaders(category_id, leaders)
        actions.create_brackets(player_models.Category.objects.get(id=category_id))

    return redirect(urlresolvers.reverse('group_index'))

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


def print_group(request, category_id):
    members = models.GroupMember.objects.filter(group__category=category_id)
    return render(request, 'competition/print_group.html', {'members': members})

def print_match(request, id=0):
    template = map(list, match_template)
    template[20][2:66] = "Anze Staric".ljust(64)
    template[22][2:66] = "Filip Evgen Trdan Staric".ljust(64)
    template[20][-4:-2] = "15".rjust(2)
    template = map(lambda x: u"".join(x), template)

    return HttpResponse(u"\n".join(template), content_type="text/plain; charset=utf-8")
