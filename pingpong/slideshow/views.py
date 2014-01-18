from django.db.models import Max, Count
from django.shortcuts import render
import itertools
from pingpong.models import Category, Group, GroupMember, Bracket, BracketSlot


def brackets_slideshow(request):
    bracket_groups = []
    for category in Category.objects.filter(type=Category.DOUBLE):
        new_brackets = list(Bracket.objects.filter(category=category).annotate(rounds=Max('bracketslot__level')))
        if category.type == Category.SINGLE and bracket_groups and len(bracket_groups[-1]) == 2:
            bracket_groups[-1].extend(new_brackets)
        else:
            bracket_groups.append(new_brackets)

    return render(request, 'brackets_slideshow.html', dict(bracket_groups=bracket_groups))


def groups_slideshow(request):
    males = Category.objects.filter(gender=0).annotate(player_count=Count('players'))

    male_members = {
        category: []
        for category in males
    }
    for member in GroupMember.objects \
                             .filter(group__category__in=males) \
                             .order_by('group__category', 'group', 'place', '-leader', 'player__surname') \
                             .prefetch_related('group', 'group__category', 'player'):
        male_members[member.group.category].append(member)

    females = Category.objects.filter(gender=1).annotate(player_count=Count('players'))
    female_members = {
        category: []
        for category in females
    }
    for member in GroupMember.objects \
        .filter(group__category__in=females) \
        .order_by('group__category', 'group', 'place', '-leader', 'player__surname') \
        .prefetch_related('group', 'group__category', 'player'):
        female_members[member.group.category].append(member)

    groups = Group.objects.select_related('category')

    single_matches = BracketSlot.objects.filter(status=1, bracket__category__gender__lt=2) \
        .select_related('player', 'bracket__category')
    single_matches = [(a, list(b)) for a, b in itertools.groupby(single_matches, lambda x: x.winner_goes_to_id)]
    single_matches = [(match, slots) for match, slots in single_matches if len(slots) == 2]

    pair_matches = BracketSlot.objects.filter(status=1, bracket__category__gender__gte=2) \
        .select_related('player', 'bracket__category')
    pair_matches = [(a, list(b)) for a, b in itertools.groupby(pair_matches, lambda x: x.winner_goes_to_id)]
    pair_matches = [(match, slots) for match, slots in pair_matches if len(slots) == 2]

    return render(request, 'groups_slideshow.html', {
        'males': male_members.items(),
        'females': female_members.items(),
        'groups': groups,
        'single_matches': single_matches,
        'pair_matches': pair_matches,
    })
