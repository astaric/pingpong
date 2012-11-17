from django.shortcuts import render_to_response, render

from . import models

def list(request):
    players = models.Player.objects.all()
    return render(request, "list.html", {"players": players})

def show(request, id):
    player = models.Player.objects.get(id=id)
    return render_to_response("show.html", {"player": player})

