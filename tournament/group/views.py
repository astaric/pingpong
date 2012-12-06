from django.http import HttpResponse
from django.shortcuts import render_to_response, render, get_object_or_404

from . import models
from ..player import models as player_models


def index(request):
    categories = player_models.Category.objects.all()

    return render(request, "group_index.html", {"categories": list(categories)})


def details(request, category_id):
    category = get_object_or_404(player_models.Category, id=category_id)
    groups = list(models.Group.objects.filter(category=category))
    for group in groups:
        group.member_list = list(group.members.order_by('-leader', 'player__surname'))

    return render(request, 'group_details.html', {'category': category, 'groups': groups})


match_template = ('',) * 19 + (
    '+-----------------------------------------------------------------+----------+',
    '|                                                                 | Miza     |',
    '+-----------------------------------------------------------------+----------+',
    '|                                                                            |',
    '+----------+----------+----------+----------+----------+----------+----------+',
    '|          |          |          |          |          | Skupaj:  |          |',
    '+----------+----------+----------+----------+----------+----------+----------+',
)


def print_match(request, id=0):
    template = map(list, match_template)
    template[20][2:66] = "Anze Staric".ljust(64)
    template[22][2:66] = "Filip Evgen Trdan Staric".ljust(64)
    template[20][-4:-2] = "15".rjust(2)
    template = map(lambda x: u"".join(x), template)

    return HttpResponse(u"\n".join(template), content_type="text/plain; charset=utf-8")
