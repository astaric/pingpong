from django import template

from ..models import BracketSlot

register = template.Library()


@register.simple_tag()
def bracket(bracket_info):
    rounds, slots = bracket_info

    bt = []
    try:
        bs = slots.__iter__()
        bt.append('<div class="tournament%d-wrap">' % 2 ** rounds)

        def r(location='top'):
            b = bs.next()
            winner = ' winner%d' % b.level if (b.level - 1) == rounds else ''
            bt.append('<div class="round%d-%s%s">%s</div>' % (b.level + 1, location, winner, b.label()))
            if b.level == 1:
                b1, b2 = bs.next(), bs.next()
                style = 'style="border: 0px;" ' if not (b1.label() or b2.label()) else ''
                bt.append('<div %sclass="round%d-top">%s</div>' % (style, b1.level + 1, b1.label()))
                bt.append('<div %sclass="round%d-bottom">%s</div>' % (style, b2.level + 1, b2.label()))
            else:
                bt.append('<div class="round%d-topwrap">' % b.level)
                r('top')
                bt.append('</div>')
                bt.append('<div class="round%d-bottomwrap">' % b.level)
                r('bottom')
                bt.append('</div>')
        r()
        bt.append('</div>')
    except StopIteration:
        pass

    return '\n'.join(bt)
