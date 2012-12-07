from django.shortcuts import render, get_object_or_404

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

    return render(request, "details.html", {"player": player})
