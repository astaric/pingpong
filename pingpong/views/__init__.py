from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import redirect
from pingpong.models import Category


def index(request):
    try:
        category = Category.objects.all()[0:1].get()
        return redirect(reverse('category', kwargs=dict(category_id=category.id)))
    except Category.DoesNotExist:
        return redirect(reverse('category_add'))
