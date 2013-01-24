import re

from django.core import urlresolvers
from django.db import transaction
from django.db.models import Count, Max
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import datastructures
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from . import models
from . import actions
from ..registration import models as player_models

def index(request):
    return redirect(urlresolvers.reverse("category_index"))


def category_index(request):
    category_members = {
        category: []
        for category in player_models.Category.objects.annotate(player_count=Count('player'))
    }
    for member in models.GroupMember.objects\
                                    .order_by('group__category', 'group', 'place', '-leader', 'player__surname')\
                                    .prefetch_related('group', 'group__category', 'player'):
        category_members[member.group.category].append(member)

    return render(request, "competition/category_index.html", {"category_members": category_members.items()})


def category_details(request, category_id):
    category = get_object_or_404(player_models.Category, id=category_id)
    members = models.GroupMember.objects.filter(group__category=category)\
                                        .select_related('player', 'group')\
                                        .order_by('group', '-leader', 'player__surname')
    brackets = models.Bracket.objects.filter(category=category)\
                                     .annotate(rounds=Max('bracketslot__level'))

    return render(request, 'competition/category_details.html', {'category': category,
                                                              'members': members,
                                                              'brackets': brackets, })


def match_index(request, filter=''):
    status = 0 if filter == 'upcoming' else 1

    groups = models.Group.objects.filter(status=status).select_related('category')

    singles_query = models.BracketSlot.objects.filter(status=status, bracket__category__gender__lt=2)\
                                              .with_two_players()\
                                              .select_related('player', 'bracket__category')
    single_matches = datastructures.MultiValueDict()
    for match in singles_query:
        single_matches.appendlist(match.winner_goes_to_id, match)

    pairs_query = models.BracketSlot.objects.raw(
        '''SELECT s.*
             FROM competition_bracketslot s
       INNER JOIN competition_bracket b ON b.id = s.bracket_id
       INNER JOIN registration_category c ON c.id = b.category_id
       INNER JOIN competition_bracketslot s2 ON s2.winner_goes_to_id = s.winner_goes_to_id
       INNER JOIN registration_player p ON p.id = s2.player_id
       INNER JOIN registration_player p2 ON p2.part_of_double_id = p.id
        LEFT JOIN competition_bracketslot s3 ON s3.player_id = p2.id AND s3.status < 2
            WHERE c.gender >= 2
         GROUP BY s.id
           HAVING COUNT(s2.id) = 4
              AND COUNT(s3.id) = 0''')
    pair_matches = datastructures.MultiValueDict()
    for match in pairs_query:
        pair_matches.appendlist(match.winner_goes_to_id, match)

    available_tables = models.Table.objects.annotate(count1=Count('bracketslot'), count2=Count('group'))\
                                           .filter(count1=0, count2=0)\
                                           .order_by('sort_order')
    return render(request, 'competition/match_index.html',
                  {
                      'mode': filter,
                      'matches': single_matches,
                      'groups': groups,
                      'pairs': pair_matches,
                      'available_tables': available_tables,
                  })


@login_required(login_url='/admin')
def set_table(request):
    try:
        table_id = request.POST['table_id']
        match_id = request.POST.get('match_id', None)
        group_id = request.POST.get('group_id', None)
        if bool(match_id) == bool(group_id):  # exactly one should be set
            raise KeyError

        if models.Table.objects.get(id=table_id).occupied():
            raise ValueError("Table (%s) is already occupied." % table_id)

        if match_id:
            for slot in models.BracketSlot.objects.filter(winner_goes_to=match_id):
                slot.table_id = table_id
                slot.save()
        if group_id:
            group = models.Group.objects.get(id=group_id)
            group.table_id = table_id
            group.save()
    except ValueError as err:
        messages.add_message(request, messages.ERROR, err.message)
    except Exception:
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

member_place_re = re.compile(r'member_([\d]+)_place')
@login_required(login_url='/admin')
@transaction.commit_on_success
def set_places(request):
    try:
        max_placement = None
        for name, placement in request.POST.items():
            match = member_place_re.match(name)
            if not match:
                continue

            member_id, = match.groups()
            if max_placement is None:
                max_placement = models.GroupMember.with_same_group_as(member_id).count()
            placement = int(placement)
            if placement is not None and not (1 <= placement <= max_placement):
                raise ValueError("Invalid placement (%s)" % placement)

            member = models.GroupMember.objects.get(id=member_id)
            member.place = placement
            member.save()
    except ValueError as err:
        transaction.rollback()
        messages.add_message(request, messages.ERROR, err.message)
    except Exception as err:
        transaction.rollback()
        messages.add_message(request, messages.ERROR, "Invalid request")
    return redirect(request.POST.get('redirect', '/'))

player_re = re.compile(r'player_([\d]+)_group')
@login_required(login_url='/admin')
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

    return redirect(urlresolvers.reverse('print_group', kwargs={"category_id": category_id}))

@login_required(login_url='/admin')
def create_pair_bracket(request):
    category_id = request.POST['category_id']
    actions.create_pair_brackets(category_id)
    return redirect(urlresolvers.reverse('category_index'))

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
    members = models.GroupMember.objects.filter(group__category=category_id).select_related('group', 'player')
    return render(request, 'competition/print_group.html', {'members': members})

def print_match(request, id=0):
    template = map(list, match_template)
    template[20][2:66] = "Anze Staric".ljust(64)
    template[22][2:66] = "Filip Evgen Trdan Staric".ljust(64)
    template[20][-4:-2] = "15".rjust(2)
    template = map(lambda x: u"".join(x), template)

    return HttpResponse(u"\n".join(template), content_type="text/plain; charset=utf-8")
