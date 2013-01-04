from django import template
from django.db.models import Max

from .. import models

register = template.Library()


def id(x):
    return x


def render_bracket(bracket_info, label=id, hide_missing=True):
    rounds, slots = bracket_info
    bt = []
    try:
        bs = slots.__iter__()
        bt.append('<div class="tournament%d-wrap">' % 2 ** rounds)

        def r(location='top'):
            b = bs.next()
            winner = ' winner%d' % b.level if (b.level - 1) == rounds else ''
            bt.append('<div class="round%d-%s%s">%s</div>' % (b.level + 1, location, winner, label(b)))
            if b.level == 1:
                b1, b2 = bs.next(), bs.next()
                style = 'style="border: 0px;" ' if hide_missing and b1.empty() and b2.empty() else ''
                bt.append('<div %sclass="round%d-top">%s</div>' % (style, b1.level + 1, label(b1)))
                bt.append('<div %sclass="round%d-bottom">%s</div>' % (style, b2.level + 1, label(b2)))
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


@register.simple_tag()
def bracket(bracket_info):
    def label(x):
        template = (
            '<div style="float:left; text-align:left; width:20px; padding-right: 5px; padding-left: 5px;">%s</div>'
            '<div style="text-align:left; ">%s</div>'
        )
        return template % x.label()

    return render_bracket(bracket_info, label, hide_missing=True)


@register.simple_tag()
def bracket_from_id(bracket_id):
    rounds = models.Bracket.objects.filter(id=bracket_id).values() \
                                   .annotate(rounds=Max('bracketslot__level'))[0]['rounds']
    slots = models.BracketSlot.objects.filter(bracket_id=bracket_id)\
                                      .select_related('transition', 'player')\
                                      .prefetch_related('transition__group')\
                                      .order_by('id')

    def label(x):
        template = '<div style="text-align:left; padding-left:10px;"><a href="%(admin_url)s">%(label)s</a></div>'
        params = {
            'admin_url': x.get_admin_url(),
            'label': '%s (%s)' % (x.id, ' '.join(x.label())),
        }
        return template % params

    return render_bracket((rounds, slots), label=label, hide_missing=False)
