from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import redirect
from pingpong.models import Category


def index(request):
    try:
        category = Category.objects.annotate(Count('bracket'), Count('group'))[0:1].get()

        if category.group__count > 0:
            pass
        elif category.bracket__count > 0:
            pass
        else:
            return redirect(reverse('category_edit', kwargs=dict(category_id=category.id)))
    except Category.DoesNotExist:
        return redirect(reverse('category_add'))
