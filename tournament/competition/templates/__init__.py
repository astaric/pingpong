from django.template import Template

from ..models import BracketSlot


def render_bracket(bracket):
    slots = BracketSlot.objects.filter(bracket=bracket).order_by('id')
    slots = list(slots.values('id', 'level', 'transition__group__name', 'transition__place'))
    if not slots:
        return Template('')

    for s in slots:
        g, p = s['transition__group__name'], s['transition__place']
        s['gp'] = '%s%s' % (g, p) if g and p else ''

    rounds = max([b['level'] for b in slots])
    bt = []
    bs = slots.__iter__()
    bt.append('<div class="bracket">')
    bt.append('<h2>%s</h2>' % bracket.name)
    bt.append('<div class="tournament%d-wrap">' % 2 ** rounds)

    def r(location='top'):
        b = bs.next()
        winner = ' winner%d' % (b['level'] + 1) if b['level'] == rounds else ''
        bt.append('<div class="round%d-%s%s">%s</div>' % (b['level'] + 1, location, winner, b['gp']))
        if b['level'] == 1:
            b1, b2 = bs.next(), bs.next()
            style = 'style="border: 0px;" ' if not (b1['gp'] or b2['gp']) else ''
            bt.append('<div %sclass="round%d-top">%s</div>' % (style, b1['level'] + 1, b1['gp']))
            bt.append('<div %sclass="round%d-bottom">%s</div>' % (style, b2['level'] + 1, b2['gp']))
        else:
            bt.append('<div class="round%d-topwrap">' % (b['level']))
            r('top')
            bt.append('</div>')
            bt.append('<div class="round%d-bottomwrap">' % (b['level']))
            r('bottom')
            bt.append('</div>')
    r()
    bt.append('</div>')
    bt.append('</div>')

    return Template('\n'.join(bt))
