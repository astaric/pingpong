from django.core.urlresolvers import reverse
from django.db.models import Count
from django.forms import CharField, Form, BooleanField, HiddenInput
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.safestring import mark_safe
from pingpong.group.helpers import create_groups_from_leaders
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

    return redirect(reverse('groups_list', kwargs=dict(category_id=category.id)))


class ReadOnlyWidget(HiddenInput):
    is_hidden = False

    def render(self, name, value, attrs=None):
        return mark_safe(value) + super(ReadOnlyWidget, self).render(name, value, attrs)


class SelectLeadersForm(Form):
    leader = BooleanField(required=False)

    id = CharField(widget=HiddenInput)
    name = CharField(widget=ReadOnlyWidget)
    surname = CharField(widget=ReadOnlyWidget)


def list_groups(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    categories = Category.objects.annotate(player_count=Count('players'))
    return render(request, 'pingpong/groups.html',
                  dict(category=category,
                       categories=categories,
                       group_members=GroupMember.for_category(category)))


def create_groups(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    SelectLeadersFormSet = formset_factory(SelectLeadersForm, extra=0)
    if request.method == 'POST':
        formset = SelectLeadersFormSet(request.POST)
        if formset.is_valid():
            leader_ids = [int(f.cleaned_data['id']) for f in formset.forms if f.cleaned_data['leader']]
            leaders = Player.objects.filter(id__in=leader_ids)
            create_groups_from_leaders(category, leaders)
            return redirect(reverse('groups_list', kwargs=dict(category_id=category.id)))
    else:
        formset = SelectLeadersFormSet(initial=Player.objects.order_by('id').filter(category=category).values('id', 'name', 'surname'))
    categories = Category.objects.annotate(player_count=Count('players'))
    return render(request, 'pingpong/groups_create.html',
                  dict(formset=formset,
                       categories=categories))


def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    return render(request, 'pingpong/group_edit.html',
                  dict(group=group))


def delete_groups(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        if 'yes' in request.POST:
            Group.objects.filter(category=category).delete()
            return redirect(reverse('groups_create', kwargs=dict(category_id=category.id)))
        else:
            return redirect(reverse('groups_list', kwargs=dict(category_id=category.id)))

    return render(request, 'pingpong/groups_delete.html',
                  dict(category=category))
