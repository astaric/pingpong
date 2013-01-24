from collections import defaultdict

from django import template

from .. import models
from ...registration import models as player_models

register = template.Library()


@register.simple_tag()
def show_bracket(bracket, admin_view=False):
    slots = defaultdict(list)
    for slot in models.BracketSlot.objects.filter(bracket=bracket)\
                                          .select_related('transition', 'player')\
                                          .prefetch_related('transition__group')\
                                          .order_by('level', 'id'):
        slots[slot.level].append(slot)

    def render_slot(slot):
        if slot is None:
            return u"&nbsp;"

        name = slot.player.full_name() if slot.player is not None else ''
        score = slot.score if slot.score is not None else ''

        if admin_view:
            name = name or u'(empty)'
            name = u'<a href="%(admin_url)s">%(name)s</a>' % {
                'admin_url': slot.get_admin_url(),
                'name': name,
            }

        if name:
            name = u'<div class="player">%s</div>' % name
        if score:
            score = u'<div class="score">%s</div>' % slot.score

        return u'%s%s' % (score, name)

    return render_bracket(bracket, slots, render_slot)


def render_bracket(bracket, slots, render_slot):
    def get_slot(slots, i, j):
        if not i % 2 ** (j + 1) == int(2 ** j - 1):
            return None
        return slots[j + 1][i // 2 ** (j + 1)]

    def visible_borders(i, j):
        borders = []
        if i % 2 ** (j + 1) == int(2 ** j - 1):
            borders.append("b")
        if 2 ** j <= i % 2 ** (j + 2) < 3 * 2 ** j and j != bracket.levels - 2:
            borders.append("r")
        return " ".join(borders)

    result = [u'<table class="bracket">']
    for i in range(len(slots[0])):
        result.append(u'<tr class="odd">')
        id, name = slots[0][i].label()
        result.append(u'<td rowspan="2">%s</td>' % id)
        result.append(u'<td rowspan="2" class="%(class)s">%(value)s</td>' % {
            'class': visible_borders(i, -1),
            'value': render_slot(get_slot(slots, i, -1)),
        })
        if i == 0:
            for j in range(bracket.levels - 1):
                result.append(u'<td class="halfline"></td>')
        result.append(u'</tr>')
        result.append(u'<tr class="even">')
        for j in range(bracket.levels - 1):
            result.append(u'<td rowspan="2" class="%(class)s">%(value)s</td>' % {
                'class': visible_borders(i, j),
                'value': render_slot(get_slot(slots, i, j)),
            })
        result.append(u'</tr>')
    result.append(u'</table>')
    return u'\n'.join(result)


@register.inclusion_tag('competition/snippets/tables.html')
def show_tables():
    tables = models.Table.objects.prefetch_related('bracketslot_set', 'group_set', 'group_set__category')
    return {'tables': tables}

@register.inclusion_tag('competition/snippets/table.html')
def show_table(table):
    return {
        'table': table,
        'player1': table.player1(),
        'player2': table.player2(),
        'occupied': table.occupied(),
    }

@register.inclusion_tag('competition/snippets/group.html', takes_context=True)
def show_group(context, group, members):
    return {
        'group': group,
        'members': members,
        'user': context['request'].user,
    }

@register.inclusion_tag('competition/snippets/match.html', takes_context=True)
def show_group_match(context, group):
    edit_form = None
    if context['request'].user.is_authenticated():
        if group.status == 0:
            edit_form = 'set_table'
    return {
        'id': group.id,
        'id_prefix': 'group',
        'player1': group.category.description,
        'player2': group.name,
        'available_tables': context['available_tables'],
        'edit_form': edit_form,
        }

@register.inclusion_tag('competition/snippets/match.html', takes_context=True)
def show_match(context, slots):
    slot1, slot2 = slots
    edit_form = None
    if context['request'].user.is_authenticated():
        if slot1.status == 0:
            edit_form = 'set_table'
        elif slot1.status == 1:
            edit_form = 'set_score'
    return {
        'id': slot1.winner_goes_to,
        'id_prefix': 'match',
        'player1': slot1.player,
        'player2': slot2.player,
        'category': slot1.player.category,
        'extra': '',
        'available_tables': context['available_tables'],
        'edit_form': edit_form,
    }

@register.inclusion_tag('competition/snippets/players.html', takes_context=True)
def show_players(context, category):
    players = player_models.Player.objects.filter(category=category).order_by('surname')
    return {
        'category': category,
        'players': players,
        'user': context['request'].user,
    }

@register.inclusion_tag('competition/snippets/groupscores.html')
def group_play_card(members):
    berger_tables = {
        3: [(2, 3), (1, 2), (3, 1)],
        4: [(1, 4), (2, 3), (4, 3), (1, 2), (2, 4), (3, 1)],
        5: [(2, 5), (3, 4), (5, 3), (1, 2), (3, 1), (4, 5), (1, 4), (2, 3), (4, 2), (5, 1)],
        6: [(1, 6), (2, 5), (3, 4), (6, 4), (5, 3), (1, 2), (2, 6), (3, 1), (4, 5), (6, 5), (1, 4), (2, 3), (3, 6), (4, 2), (5, 1)],
    }

    matches = []
    if 3 <= len(members) <= 6:
        for p1, p2 in berger_tables[len(members)]:
            matches.append((members[p1 - 1], members[p2 - 1]))

    return {
        'members': members,
        'matches': matches,
    }
