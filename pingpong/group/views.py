from collections import defaultdict
from django.core.urlresolvers import reverse
from django.db.models import Count
from django import forms
from django.forms import CharField, Form, HiddenInput, ModelForm
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory, BaseFormSet
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import View
from pingpong.bracket.helpers import create_brackets
from pingpong.bracket.models import Bracket, BracketSlot
from pingpong.models import Category, Player, Match, Group, GroupMember
from pingpong.printing.helpers import print_groups


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
    leader = CharField(required=False)

    id = CharField(widget=HiddenInput)
    name = CharField(widget=ReadOnlyWidget)
    surname = CharField(widget=ReadOnlyWidget)


class BaseLeaderFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        has_leaders = False
        for form in self.forms:
            if form.cleaned_data['leader']:
                has_leaders = True
        if not has_leaders:
            raise forms.ValidationError("You have to select at least one leader.")


SelectLeadersFormSet = formset_factory(SelectLeadersForm, formset=BaseLeaderFormSet, extra=0)


class GroupsView(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        categories = Category.objects.annotate(player_count=Count('players'))

        group_members = GroupMember.for_category(category)
        if category.type == Category.SINGLE and len(group_members) == 0:
            formset = SelectLeadersFormSet(
                initial=Player.objects.order_by('id').filter(category=category).values('id', 'name', 'surname'))
            return render(request, 'pingpong/create_groups.html',
                          dict(category=category,
                               formset=formset,
                               categories=categories))
        else:
            brackets = Bracket.objects.filter(category=category)
            return render(request, 'pingpong/groups.html',
                          dict(category=category,
                               categories=categories,
                               group_members=GroupMember.for_category(category),
                               brackets=brackets))

    def post(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)

        if 'recreate_brackets' in request.POST:
            Bracket.objects.filter(category=category).delete()
            create_brackets(category)
            return redirect(reverse('groups', kwargs=dict(category_id=category.id)))

        if 'recreate_matches' in request.POST:
            matches = defaultdict(list)
            Match.objects.filter(player1_bracket_slot__bracket__category__type=1).delete()
            for bs in BracketSlot.objects.filter(bracket__category__type=1):
                if bs.winner_goes_to_id:
                    matches[bs.winner_goes_to_id].append(bs)
            for s in matches.values():
                if len(s) != 2:
                    continue
                s1, s2 = s
                Match.objects.create(status=Match.DOUBLE, player1_bracket_slot=s1, player2_bracket_slot=s2, player1=s1.player, player2=s2.player)
            print matches
            return redirect(reverse('groups', kwargs=dict(category_id=category.id)))

        formset = SelectLeadersFormSet(request.POST)
        if formset.is_valid():
            sorted_forms = sorted((f for f in formset.forms if f.cleaned_data['leader']), key=lambda x: x.cleaned_data['leader'])
            leader_ids = [int(f.cleaned_data['id']) for f in sorted_forms]
            leaders = [Player.objects.get(id=id) for id in leader_ids]
            category.create_groups_from_leaders(leaders)
            create_brackets(category)

            print_groups(category)

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
            Bracket.objects.filter(category=category).delete()

        return redirect(reverse('groups', kwargs=dict(category_id=category.id)))

    return render(request, 'pingpong/delete_groups.html',
                  dict(category=category))
