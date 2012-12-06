from collections import deque, defaultdict
from math import ceil, log
from itertools import izip, chain, tee, cycle
from operator import add
import string

from django.db.models import Count

from ..player import models as player_models
from .models import Group, GroupMember, Bracket, GroupToBracketTransition
from .utils import alternate, group, shuffled, invert
from . import utils


def create_groups_from_leaders(category_id, leaders):
    Group.objects.filter(category=category_id).delete()
    groups = deque(())
    members = []
    clubs = defaultdict(set)

    for i, leader in enumerate(leaders):
        group = Group.objects.create(name=string.ascii_uppercase[i], category_id=category_id)
        groups.append(group)
        members.append(GroupMember(player=leader, group=group, leader=True))
        if leader.club:
            clubs[group].add(leader.club)

    leader_ids = [l.id for l in leaders]
    unallocated_players = deque(shuffled(
        player_models.Player.objects.filter(category=category_id).exclude(id__in=leader_ids)))

    tried = 0
    while unallocated_players:
        group = groups[0]
        player = unallocated_players.popleft()
        if player.club:
            if player.club in clubs[group]:
                unallocated_players.append(player)
                tried += 1
                if tried > len(unallocated_players):
                    raise ValueError("Weird data")
                continue
            else:
                clubs[group].add(player.club)
                tried = 0

        members.append(GroupMember(player=player, group=group))
        groups.rotate(-1)

    GroupMember.objects.bulk_create(members)


def create_single_elimination_bracket(levels, **kwargs):
    brackets = [[] for i in range(levels)]

    def recursively_create_brackets(parent, level):
        if level < 0:
            return
        for i in range(2):
            bracket = Bracket.objects.create(level=level, winner_goes_to=parent, **kwargs)
            brackets[level].append(bracket)
            recursively_create_brackets(bracket, level - 1)
    finale = Bracket.objects.create(level=levels - 1, **kwargs)
    brackets[-1].append(finale)
    recursively_create_brackets(finale, levels - 2)
    return brackets


def create_tournament_seeds(n, groups=0):
    def create_seeds(levels):
        if levels == 0:
            return 0,
        s = create_seeds(levels - 1)
        n = 2 ** (levels) - 1
        return list(chain.from_iterable(izip(s, (n - x for x in s))))

    levels = int(ceil(log(n, 2)))
    seeds = create_seeds(levels)
    if groups:
        N = len(seeds)
        inverted = invert(seeds)
        for i in range(groups, n):
            for j in range(i, N):
                if (inverted[i - groups] < N / 2) != (inverted[j] < N / 2):
                    inverted[i:j + 1] = inverted[j:j + 1] + inverted[i:j]
                    break
        seeds = invert(inverted)

    return [s if s < n else None for s in seeds]


def create_group_transitions(groups, **kwargs):
    # First two players from each group go to the winners
    # bracket, the rest go to the losers bracket.

    groups = list(groups.annotate(Count('members')))
    for group in groups:
        assert group.members__count >= 2

    n_players = sum(g.members__count for g in groups)
    all_members = reduce(add, zip(*[[(g, i) for i in range(g.members__count)] for g in groups]))

    n_winners = 2 * len(groups)
    create_group_bracket_transitions(all_members[:n_winners], **kwargs)
    create_group_bracket_transitions(all_members[n_winners:], **kwargs)


def create_group_bracket_transitions(candidates, **kwargs):
    n = len(candidates)
    levels = int(ceil(log(n)))

    brackets = create_single_elimination_bracket(levels=levels, **kwargs)
    placements = list(create_tournament_placement(levels=levels))

    for (m1, m2), b in zip(utils.group(placements, 2), brackets[0]):
        if m1 >= n or m2 >= n:
            b = b.winner_goes_to

        if m1 < n:
            group, place = candidates[m1]
            GroupToBracketTransition.objects.create(group=group, place=place, bracket=b.winner_goes_to)
        if m2 < n:
            group, place = candidates[m2]
            GroupToBracketTransition.objects.create(group=group, place=place, bracket=b.winner_goes_to)
