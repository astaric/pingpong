from django.shortcuts import render_to_response, render

from . import models

def list(request):
    categories = models.Category.objects.all()
    players_by_categories = [
        (category, category.player_set.order_by('surname', 'name'))
        for category in categories
    ]
    print players_by_categories
    return render(request, "list.html", {"categories": players_by_categories})

def show(request, id):
    player = models.Player.objects.get(id=id)
    return render_to_response("show.html", {"player": player})

