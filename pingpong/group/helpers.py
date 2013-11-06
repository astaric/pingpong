from collections import deque, defaultdict
import random
import string
from pingpong.group.models import Group, GroupMember
from pingpong.models import Player


def create_groups_from_leaders(category, leaders):
    Group.objects.filter(category=category).delete()
    groups = deque(())
    members = []
    clubs = defaultdict(set)

    for i, leader in enumerate(leaders):
        group = Group.objects.create(name=string.ascii_uppercase[i], category=category)
        groups.append(group)
        members.append(GroupMember(player=leader, group=group, leader=True))
        if leader.club:
            clubs[group].add(leader.club)

    leader_ids = [l.id for l in leaders]
    unallocated_players = deque(shuffled(
        Player.objects.filter(category=category).exclude(id__in=leader_ids)))

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


def shuffled(xs):
    xs = list(xs)
    return random.sample(xs, len(xs))
