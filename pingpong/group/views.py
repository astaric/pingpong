from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import redirect, render, get_object_or_404
from pingpong.group.models import GroupMember, Group
from pingpong.models import Category, Player


def index(request):
    try:
        category = Category.objects.all()[0]
    except IndexError:
        return redirect(reverse('category_add'))

    group_members = GroupMember.for_category(category)
    if len(group_members) == 0:
        return redirect(reverse('groups_create', kwargs=dict(id=category.id)))

    return render(request, 'pingpong/category.html',
                  dict(category=category,
                       group_members=group_members))


def create_groups(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    PlayerFormSet = modelformset_factory(Player, extra=3, fields=['name', 'surname', 'club'])
    formset = PlayerFormSet(queryset=Player.objects.order_by('id').filter(category=category), prefix='players')
    return render(request, 'pingpong/groups_create.html',
                  dict(formset=formset))


def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    return render(request, 'pingpong/group_edit.html',
                  dict(group=group))


def delete_groups(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    return render(request, 'pingpong/groups_delete.html',
                  dict(category=category))
