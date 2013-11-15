from django import template

register = template.Library()

@register.inclusion_tag('snippets/group_play_card.html')
def group_play_card(members):
    berger_tables = {
        3: [(2, 3), (1, 2), (3, 1)],
        4: [(1, 4), (2, 3), (4, 3), (1, 2), (2, 4), (3, 1)],
        5: [(2, 5), (3, 4), (5, 3), (1, 2), (3, 1), (4, 5), (1, 4), (2, 3), (4, 2), (5, 1)],
        6: [(1, 6), (2, 5), (3, 4), (6, 4), (5, 3), (1, 2), (2, 6), (3, 1), (4, 5), (6, 5), (1, 4), (2, 3), (3, 6), (4, 2), (5, 1)],
        7: [(2, 7), (3, 6), (4, 5), (6, 4), (7, 3), (1, 2), (3, 1), (4, 7), (5, 6), (7, 5), (1, 4), (2, 3), (4, 2), (5, 1), (6, 7), (1, 6), (2, 5), (3, 4), (5, 3), (6, 2), (7, 1)],
        8: [],
    }

    matches = []
    if 3 <= len(members) <= 6:
        for p1, p2 in berger_tables[len(members)]:
            matches.append((members[p1 - 1], members[p2 - 1]))

    return {
        'members': members,
        'matches': matches,
    }


@register.inclusion_tag('snippets/match_card.html')
def match_card(match):
    return {
        'match': match,
    }