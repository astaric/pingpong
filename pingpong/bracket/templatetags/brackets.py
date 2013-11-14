from collections import defaultdict
from django import template
from pingpong.bracket.models import BracketSlot

register = template.Library()

@register.simple_tag()
def show_bracket(bracket, admin_view=False):
    slots = defaultdict(list)
    for slot in BracketSlot.objects.filter(bracket=bracket)\
                                          .select_related('transition', 'player')\
                                          .prefetch_related('transition__group')\
                                          .order_by('level', 'id'):
        slots[bracket.levels - 1 - slot.level].append(slot)

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
            cls = " playing" if slot.table else ""
            name = u'<div class="player%s">%s</div>' % (cls, name)
        if score != '':
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