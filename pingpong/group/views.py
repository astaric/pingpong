from django.core.urlresolvers import reverse
from django.db.models import Count
from django import forms
from django.forms import CharField, Form, BooleanField, HiddenInput, ModelForm
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory, BaseFormSet
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import View
from pingpong.bracket.helpers import create_brackets
from pingpong.bracket.models import Bracket
from pingpong.group.helpers import create_groups_from_leaders, berger_tables
from pingpong.group.models import GroupMember, Group
from pingpong.models import Category, Player, Match
from pingpong.printing.helpers import print_groups, print_matches


def index(request):
    try:
        category = Category.objects.all()[0]
    except IndexError:
        return redirect(reverse('category_add'))

    return redirect(reverse('groups', kwargs=dict(category_id=category.id)))


class ReadOnlyWidget(HiddenInput):
    is_hidden = False

    def render(self, name, value, attrs=None):
        return mark_safe(value) + super(ReadOnlyWidget, self).render(name, value, attrs)


class SelectLeadersForm(Form):
    leader = BooleanField(required=False)

    id = CharField(widget=HiddenInput)
    name = CharField(widget=ReadOnlyWidget)
    surname = CharField(widget=ReadOnlyWidget)


class BaseArticleFormSet(BaseFormSet):
    def clean(self):
        """Checks that no two articles have the same title."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        has_leaders = False
        for form in self.forms:
            if form.cleaned_data['leader']:
                has_leaders = True
        if not has_leaders:
            raise forms.ValidationError("You have to select at least one leader.")


SelectLeadersFormSet = formset_factory(SelectLeadersForm, formset=BaseArticleFormSet, extra=0)


class GroupsView(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        categories = Category.objects.annotate(player_count=Count('players'))

        group_members = GroupMember.for_category(category)
        if len(group_members) == 0:
            formset = SelectLeadersFormSet(
                initial=Player.objects.order_by('id').filter(category=category).values('id', 'name', 'surname'))
            return render(request, 'pingpong/create_groups.html',
                          dict(category=category,
                               formset=formset,
                               categories=categories))
        else:
            matches = Match.objects.filter(group__category=category)
            print_matches(matches)
            brackets = Bracket.objects.filter(category=category)
            return render(request, 'pingpong/groups.html',
                          dict(category=category,
                               categories=categories,
                               group_members=GroupMember.for_category(category),
                               brackets=brackets))

    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        formset = SelectLeadersFormSet(request.POST)
        if formset.is_valid():
            leader_ids = [int(f.cleaned_data['id']) for f in formset.forms if f.cleaned_data['leader']]
            leaders = Player.objects.filter(id__in=leader_ids)
            create_groups_from_leaders(category, leaders)
            create_brackets(category)

            return redirect(reverse('groups', kwargs=dict(category_id=category.id)))

        categories = Category.objects.annotate(player_count=Count('players'))
        return render(request, 'pingpong/create_groups.html',
                      dict(category=category,
                           formset=formset,
                           categories=categories))

class GroupScoresForm(ModelForm):
    class Meta:
        model = GroupMember
        fields = ['id', 'place']


def edit_group(request, category_id, group_id):
    category = get_object_or_404(Category, id=category_id)
    group = get_object_or_404(Group, id=group_id)

    groups = Group.objects.filter(category_id=group.category_id).annotate(member_count=Count('members'))
    members = GroupMember.for_group(group)

    GroupScoresFormset = modelformset_factory(GroupMember, form=GroupScoresForm, extra=0)
    if request.method == 'POST':
        formset = GroupScoresFormset(request.POST, queryset=members)
        if formset.is_valid():
            formset.save()
            return redirect(reverse('groups', kwargs=dict(category_id=category.id)))
    else:
        formset = GroupScoresFormset(queryset=members)


    matches = Match.objects.filter(group=group).select_related('player1', 'player2')
    return render(request, 'pingpong/group_edit.html',
                  dict(category=category,
                       group=group,
                       groups=groups,
                       group_members=members,
                       matches=matches, formset=formset))


def delete_groups(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        if 'yes' in request.POST:
            Group.objects.filter(category=category).delete()

        return redirect(reverse('groups', kwargs=dict(category_id=category.id)))

    return render(request, 'pingpong/delete_groups.html',
                  dict(category=category))
