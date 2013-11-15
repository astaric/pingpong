from math import ceil, log
from itertools import chain, izip, izip_longest

from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from pingpong.bracket.models import BracketSlot, Bracket, GroupToBracketTransition
from pingpong.group.models import Group
from pingpong.models import Match


def create_single_elimination_bracket_slots(bracket, n):
    levels = max(int(ceil(log(n, 2))), 1)
    slots = [[] for i in range(levels)]

    def recursively_create_slots(parent, level):
        if level > levels:
            return
        s = []
        for i in range(2):
            slot = BracketSlot.objects.create(bracket=bracket, level=level, winner_goes_to=parent)
            slots[levels - level].append(slot)
            s.append(slot)
            recursively_create_slots(slot, level + 1)
        Match.objects.create(player1_bracket_slot=s[0], player2_bracket_slot=s[1])

    bracket_winner = BracketSlot.objects.create(bracket=bracket, level=0)
    recursively_create_slots(bracket_winner, 1)
    return slots


def create_tournament_seeds(n, groups=0):
    def create_seeds(levels):
        if levels == 0:
            return 0,
        s = create_seeds(levels - 1)
        n = 2 ** (levels) - 1
        return list(chain.from_iterable(izip(s, (n - x for x in s))))

    levels = max(int(ceil(log(n, 2))), 1)
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


def create_brackets(category):
    # First two players from each group go to the winners
    # bracket, the rest go to the losers bracket.
    Bracket.objects.filter(category=category).delete()
    groups = Group.objects.filter(category=category).annotate(member_count=Count('members'))

    all_members = list(alternate(*[[(g, i + 1) for i in range(g.member_count)] for g in groups]))

    n_winners = min(2 * len(groups), len(all_members))
    n_soothers = len(all_members) - n_winners
    if n_winners > 0:
        winner_bracket = Bracket.objects.create(category=category, name=_("WINNERS"), levels=levels(n_winners))
        w_slots = create_single_elimination_bracket_slots(winner_bracket, n_winners)
        create_transitions(all_members[:n_winners], groups, w_slots)

    if n_soothers > 0:
        soother_bracket = Bracket.objects.create(category=category, name=_("SOOTHERS"), levels=levels(n_soothers))
        s_slots = create_single_elimination_bracket_slots(soother_bracket, n_soothers)
        create_transitions(all_members[n_winners:], groups, s_slots)


def levels(n_players):
    return int(ceil(log(n_players, 2))) + 1


def create_transitions(candidates, groups, slots):
    n = len(candidates)
    placements = list(create_tournament_seeds(n, len(groups)))

    for placement, slot in zip(placements, slots[0]):
        if placement is not None:
            group, place = candidates[placement]
            GroupToBracketTransition.objects.create(group=group, place=place, slot=slot)
        else:
            slot.no_player = True
            slot.save()


def invert(xs, length=0):
    ys = [None] * (length or len(xs))
    for i, s in enumerate(xs):
        if s < len(ys):
            ys[s] = i
    return ys


def alternate(*iterables):
    MISSING = object()
    for tuple in izip_longest(*iterables, fillvalue=MISSING):
        for element in tuple:
            if element is not MISSING:
                yield element