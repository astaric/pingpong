from django.shortcuts import render

from ..player import models as player_models


def index(request):
    categories = player_models.Category.objects.values_list('name', flat=True)

    return render(request, 'base.html', {'categories': categories})
