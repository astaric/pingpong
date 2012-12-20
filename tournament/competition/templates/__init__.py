from django.template import Template

from ..models import BracketSlot

class Slot(object):
    def __init__(self, slot):
        self.level = slot['level'] + 1
        g, p = slot['transition__group__name'], slot['transition__place']
        n, s = slot['player__name'], slot['player__surname']

        label = []
        if g and p:
            label.append('%s%s' % (g, p))
        if n:
            label.append(n)
        if s:
            label.append(s)

        self.label = ' '.join(label)


def render_bracket(bracket):
    slots = BracketSlot.objects.filter(bracket=bracket).order_by('id')
    slots = list(slots.values('id', 'level',
                              'transition__group__name', 'transition__place',
                              'player__name', 'player__surname'))

    rounds = 0
    for i,s in enumerate(slots):
        rounds = max(rounds, s['level'])
        slots[i] = Slot(s)

    bt = []
    try:
        bs = slots.__iter__()
        bt.append('<div class="bracket">')
        bt.append('<h2>%s</h2>' % bracket.name)
        bt.append('<div class="tournament%d-wrap">' % 2 ** rounds)

        def r(location='top'):
            b = bs.next()
            winner = ' winner%d' % b.level if (b.level - 1) == rounds else ''
            bt.append('<div class="round%d-%s%s">%s</div>' % (b.level, location, winner, b.label))
            if b.level == 2:
                b1, b2 = bs.next(), bs.next()
                style = 'style="border: 0px;" ' if not (b1.label or b2.label) else ''
                bt.append('<div %sclass="round%d-top">%s</div>' % (style, b1.level, b1.label))
                bt.append('<div %sclass="round%d-bottom">%s</div>' % (style, b2.level, b2.label))
            else:
                bt.append('<div class="round%d-topwrap">' % (b.level - 1))
                r('top')
                bt.append('</div>')
                bt.append('<div class="round%d-bottomwrap">' % (b.level - 1))
                r('bottom')
                bt.append('</div>')
        r()
        bt.append('</div>')
        bt.append('</div>')
    except StopIteration:
        pass

    return Template('\n'.join(bt))