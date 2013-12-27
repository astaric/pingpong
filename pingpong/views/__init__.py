from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from pingpong.models import Category


def index(request):
    try:
        category = Category.objects.all()[0]
        return redirect(reverse('category_edit', kwargs=dict(category_id=category.id)))
    except IndexError:
        pass

    return redirect(reverse('category_add'))
