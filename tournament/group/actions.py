from collections import deque, defaultdict
from math import ceil, log
import itertools
import string

from django.db.models import Count

from ..player import models as player_models
from .models import Group, GroupMember, Bracket, GroupToBracketTransition
from .utils import alternate, shuffled


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


def create_group_transitions(groups, **kwargs):
    # We currently assume that the groups contain up to 4
    # players, first two players go to the winners bracket
    # and the last two players go to the losers bracket.
    groups = list(groups.annotate(Count('groupmember')))
    for group in groups:
        assert group.groupmember__count <= 4

    bracket_levels = int((ceil(log(len(groups), 2)))) + 1
    winner_brackets = create_single_elimination_bracket(levels=bracket_levels, **kwargs)
    loser_brackets = create_single_elimination_bracket(levels=bracket_levels, **kwargs)

    transitions = []
    # Add dummy groups so the group count is equal to bracket size
    groups = groups + [Group(name="?")] * (len(winner_brackets[0]) - len(groups))
    for brackets, places in ((winner_brackets, (1, 2)), (loser_brackets, (3, 4))):
        for bracket, group, place in zip(alternate(brackets[0], brackets[0]),
                                         alternate(groups, groups[::-1]),
                                         itertools.cycle(places)):
            if group.id and place <= group.groupmember__count:
                transitions.append(
                    GroupToBracketTransition.objects.create(group=group, place=place, bracket=bracket))
    return transitions
