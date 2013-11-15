from django.core.urlresolvers import reverse
from django.db.models import Count
from django import forms
from django.forms.models import modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from pingpong.bracket.helpers import create_pair_brackets
from pingpong.models import Category, Player, Double


def index(request):
    try:
        category = Category.objects.all()[0]
        return redirect(reverse('category_edit', kwargs=dict(category_id=category.id)))
    except IndexError:
        pass

    return redirect(reverse('category_add'))


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'type']


class SimpleCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if category.type == Category.SINGLE:
        return edit_single_category(request, category)
    else:
        return edit_double_category(request, category)


def edit_single_category(request, category):
    PlayerFormSet = modelformset_factory(Player, extra=10, fields=['name', 'surname', 'club'], can_delete=True)
    if request.method == 'POST':
        if 'delete' in request.POST:
            return redirect(reverse("category_delete", kwargs=dict(category_id=category.id)))

        formset = PlayerFormSet(request.POST, queryset=Player.objects.order_by('id').filter(category=category), prefix='player')
        form = SimpleCategoryForm(request.POST, instance=category, prefix='category')
        if form.is_valid() and formset.is_valid():
            form.save()

            instances = formset.save(commit=False)
            for instance in instances:
                if instance.category_id is None:
                    instance.category = category
                instance.save()
            return redirect(reverse("category_edit", kwargs=dict(category_id=category.id)))
    else:
        formset = PlayerFormSet(queryset=Player.objects.order_by('id').filter(category=category), prefix='player')
        form = SimpleCategoryForm(instance=category, prefix='category')

    categories = Category.objects.filter(type=category.type).annotate(player_count=Count('players'))
    return render(request, 'pingpong/category_edit.html',
                  dict(categories=categories,
                       category=category,
                       formset=formset,
                       form=form))


def edit_double_category(request, category):
    PlayerFormSet = modelformset_factory(Double, extra=10, fields=['player1', 'player2'], can_delete=True)
    if request.method == 'POST':
        if 'delete' in request.POST:
            return redirect(reverse("category_delete", kwargs=dict(category_id=category.id)))

        if 'create_brackets' in request.POST:
            create_pair_brackets(category)
            return redirect(reverse("groups", kwargs=dict(category_id=category.id)))

        formset = PlayerFormSet(request.POST, queryset=Double.objects.order_by('id').filter(category=category), prefix='player')
        form = SimpleCategoryForm(request.POST, instance=category, prefix='category')
        if form.is_valid() and formset.is_valid():
            form.save()

            instances = formset.save(commit=False)
            for instance in instances:
                if instance.category_id is None:
                    instance.category = category
                instance.save()
            return redirect(reverse("category_edit", kwargs=dict(category_id=category.id)))
    else:
        formset = PlayerFormSet(queryset=Double.objects.order_by('id').filter(category=category), prefix='player')
        form = SimpleCategoryForm(instance=category, prefix='category')

    categories = Category.objects.filter(type=category.type).annotate(player_count=Count('players'))
    return render(request, 'pingpong/category_edit.html',
                  dict(categories=categories,
                       category=category,
                       formset=formset,
                       form=form))


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            return redirect(reverse('category_edit', kwargs=dict(category_id=category.id)))
    else:
        form = CategoryForm()

    categories = Category.objects.annotate(player_count=Count('players'))
    return render(request, 'pingpong/category_add.html',
                  dict(form=form,
                       categories=categories))


def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        if 'yes' in request.POST:
            category.delete()
            return redirect(reverse('signup'))
        else:
            return redirect(reverse('category_edit', kwargs=dict(category_id=category.id)))

    return render(request, 'pingpong/category_delete.html',
                  dict(category=category))