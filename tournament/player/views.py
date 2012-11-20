from django.http import HttpResponse
from django.shortcuts import render_to_response, render, get_object_or_404

from . import models

def index(request):
    categories = models.Category.objects.all()
    players_by_categories = [
        (category, category.player_set.order_by('surname', 'name'))
        for category in categories
    ]
    return render(request, "index.html", {"categories": players_by_categories})

def details(request, id):
    player = get_object_or_404(models.Player, id=id)

    return render_to_response("details.html", {"player": player})


match_template = ('','','','','','','','','','','','','','','','','','','',
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