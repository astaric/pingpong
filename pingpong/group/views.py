from django.core.urlresolvers import reverse
from django.forms import CharField, Form, BooleanField, HiddenInput
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.safestring import SafeText, mark_safe
from pingpong.group.models import GroupMember, Group
from pingpong.models import Category, Player


def index(request):
    try:
        category = Category.objects.all()[0]
    except IndexError:
        return redirect(reverse('category_add'))

    group_members = GroupMember.for_category(category)
    if len(group_members) == 0:
        return redirect(reverse('groups_create', kwargs=dict(category_id=category.id)))

    return render(request, 'pingpong/category.html',
                  dict(category=category,
                       group_members=group_members))


class ReadOnlyWidget(HiddenInput):
    is_hidden = False
    def render(self, name, value, attrs=None):
        return mark_safe(value) + super(ReadOnlyWidget, self).render(name, value, attrs)


class SelectLeadersForm(Form):
    leader = BooleanField()

    id = CharField(widget=HiddenInput)
    name = CharField(widget=ReadOnlyWidget)
    surname = CharField(widget=ReadOnlyWidget)


def create_groups(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    PlayerFormSet = formset_factory(SelectLeadersForm)
    formset = PlayerFormSet(initial=Player.objects.order_by('id').filter(category=category).values('id', 'name', 'surname'))
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
