from django.core.urlresolvers import reverse
from django.db.models import Count
from django.forms.models import modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from pingpong.models import Category, Player


def index(request):
    categories = Category.objects.all()

    return render(request, 'pingpong/category_list.html',
                  dict(categories=categories))


def edit_category(request, id, name=''):
    category = get_object_or_404(Category, id=id)

    PlayerFormSet = modelformset_factory(Player, extra=3, fields=['name', 'surname', 'club'])
    if request.method == 'POST':
        formset = PlayerFormSet(request.POST, queryset=Player.objects.order_by('id').filter(category=category))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                if instance.category_id is None:
                    instance.category = category
                instance.save()
            return redirect(reverse("signup_category", kwargs=dict(id=category.id, name=category.name)))
    else:
        formset = PlayerFormSet(queryset=Player.objects.order_by('id').filter(category=category))

    categories = Category.objects.annotate(player_count=Count('players__id'))
    return render(request, 'pingpong/edit_category.html',
                  dict(categories=categories,
                       category=category,
                       formset=formset))