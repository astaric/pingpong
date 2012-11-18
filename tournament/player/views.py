from django.shortcuts import render_to_response, render

from . import models

def list(request):
    categories = models.Category.objects.all()
    players = models.Player.objects.all().order_by('category')
    players_by_categories = [
        (category, players.filter(category=category))
        for category in categories
    ]
    print players_by_categories
    return render(request, "list.html", {"categories": players_by_categories})

def show(request, id):
    player = models.Player.objects.get(id=id)
    return render_to_response("show.html", {"player": player})

