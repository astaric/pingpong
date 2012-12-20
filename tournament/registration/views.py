from django.shortcuts import render, get_object_or_404

from . import models
from . import forms


def index(request):
    categories = models.Category.objects.all()
    players_by_categories = [
        (category, category.player_set.order_by('surname', 'name'))
        for category in categories
    ]
    return render(request, "index.html", {"categories": players_by_categories})


def player_details(request, id):
    player = get_object_or_404(models.Player, id=id)

    return render(request, "player/details.html", {"player": player})


def player_edit(request, player_id):
    player = get_object_or_404(models.Player, id=player_id)
    if request.POST:
        form = forms.PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
    else:
        form = forms.PlayerForm(instance=player)

    return render(request, 'player/edit.html', {'player': player,
                                                'form': form})
