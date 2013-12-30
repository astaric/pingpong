from django.core.urlresolvers import reverse
from django.db.models import Count
from django.db.models.deletion import Collector
from django.shortcuts import render, get_object_or_404, redirect

from pingpong.bracket.helpers import create_pair_brackets
from pingpong.bracket.models import Bracket
from pingpong.models import Category, Player, Double, Group
from pingpong.signup.forms import PlayerFormSet, SimpleCategoryForm, CategoryForm, DoubleFormSet


def index(request):
    try:
        category = Category.objects.all()[0]
        return redirect(reverse('category_edit', kwargs=dict(category_id=category.id)))
    except IndexError:
        pass

    return redirect(reverse('category_add'))


def edit_category(request, category_id):
    category = get_object_or_404(Category.objects.annotate(Count('bracket'), Count('group')),
                                 id=category_id)

    if category.type == Category.SINGLE:
        return edit_single_category(request, category)
    else:
        return edit_double_category(request, category)


def edit_single_category(request, category):
    if request.method == 'POST':
        if 'delete_brackets' in request.POST:
            Bracket.objects.filter(category=category).delete()
            return redirect(reverse("category_edit", kwargs=dict(category_id=category.id)))

        formset = PlayerFormSet(request.POST, queryset=Player.objects.order_by('id').filter(category=category),
                                prefix='player')
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
    if request.method == 'POST':
        if 'delete' in request.POST:
            return redirect(reverse("category_delete", kwargs=dict(category_id=category.id)))

        formset = DoubleFormSet(request.POST, queryset=Double.objects.order_by('id').filter(category=category),
                                prefix='player')
        form = SimpleCategoryForm(request.POST, instance=category, prefix='category')

        if 'create_brackets' in request.POST:
            if formset.is_valid():
                create_pair_brackets(category, seeds=formset.seeds())
                return redirect(reverse("groups", kwargs=dict(category_id=category.id)))

        if form.is_valid() and formset.is_valid():
            form.save()

            instances = formset.save(commit=False)
            for instance in instances:
                if instance.category_id is None:
                    instance.category = category
                instance.save()
            return redirect(reverse("category_edit", kwargs=dict(category_id=category.id)))
    else:
        formset = DoubleFormSet(queryset=Double.objects.order_by('id').filter(category=category), prefix='player')
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

    return render(request, 'pingpong/confirm_deletion.html', dict(
        object_type=category._meta.verbose_name,
        object_description=u'%s (%s)' % (category.description, category.name),
        related_objects=get_related_objects([category]),
    ))


def delete_groups(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    groups = category.group_set.all()

    if request.method == 'POST':
        if 'yes' in request.POST:
            groups.delete()
        return redirect(reverse('category_edit', kwargs=dict(category_id=category.id)))

    return render(request, 'pingpong/confirm_deletion.html', dict(
        object_type=Group._meta.verbose_name_plural,
        object_description=groups,
        related_objects=get_related_objects(groups),
    ))


def delete_brackets(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    brackets = category.bracket_set.all()

    if request.method == 'POST':
        if 'yes' in request.POST:
            brackets.delete()
        return redirect(reverse('category_edit', kwargs=dict(category_id=category.id)))

    return render(request, 'pingpong/confirm_deletion.html', dict(
        object_type=Bracket._meta.verbose_name_plural,
        object_description=brackets,
        related_objects=get_related_objects(brackets),
    ))


def get_related_objects(obj):
    collector = Collector(using='default')
    collector.collect(obj)
    return [(model._meta.verbose_name_plural, instance) for model, instance in collector.instances_with_model()]
