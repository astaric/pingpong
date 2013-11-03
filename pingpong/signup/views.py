from django.shortcuts import render
from pingpong.models import Category


def index(request):
    categories = Category.objects.all()

    return render(request, 'pingpong/category_list.html',
                  dict(categories=categories))
