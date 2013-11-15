from collections import deque, defaultdict
import random
import string
from pingpong.group.models import Group, GroupMember
from pingpong.models import Player, Match


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
    group_members = defaultdict(list)
    for member in GroupMember.objects.filter(group__category=category).select_related('group'):
        group_members[member.group].append(member)

    matches = []
    for group in groups:
        for p1, p2 in berger_tables(len(group_members[group])):
            matches.append(Match(player1=group_members[group][p1].player,
                                 player2=group_members[group][p2].player,
                                 group=group,
                                 status=Match.READY))
    Match.objects.bulk_create(matches)


def shuffled(xs):
    xs = list(xs)
    return random.sample(xs, len(xs))


def berger_tables(n):
    m = n if n % 2 == 0 else n + 1
    m2 = m // 2
    players = deque(range(m))

    matches = []
    for i in range(m - 1):
        for a, b in zip(list(players)[:m2], list(players)[m2:][::-1]):
            if a < n and b < n:
                matches.append((a, b))
        if i % 2 == 0:
            x = players.pop()
            players.rotate(m2 - 2)
            players.appendleft(x)
        else:
            x = players.popleft()
            players.rotate(-m2 + 1)
            players.append(x)

    return matches
