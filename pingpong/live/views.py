import itertools
import re

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.forms import CharField, HiddenInput, Form
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, ModelForm, ModelChoiceField
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from pingpong.bracket.models import BracketSlot
from pingpong.group.models import Group
from pingpong.models import Table, Category, Match


class ReadOnlyWidget(HiddenInput):
    is_hidden = False

    def __init__(self, model=None):
        super(ReadOnlyWidget, self).__init__()
        self.model = model

    def render(self, name, value, attrs=None):
        if self.model:
            value = self.model.objects.get(id=value)
        return mark_safe(value) + super(ReadOnlyWidget, self).render(name, value, attrs)


class CurrentMatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ()

    score = CharField(required=False)

    def clean(self):
        cleaned_data = ModelForm.clean(self)

        score = cleaned_data.get('score', None)
        if score:
            match = re.match(r'(\d+)[^\d]+(\d+)', score)
            if match:
                self.instance.player1_score, self.instance.player2_score = map(int, match.groups())
            else:
                raise ValidationError('Invalid score.')
        return cleaned_data


def current_matches(request):
    try:
        category = Category.objects.all()[:1].get()
    except Category.DoesNotExist:
        return redirect('category_add')

    matches = Match.objects.filter(status=Match.PLAYING, group__isnull=True)
    UpcomingMatchesFromset = modelformset_factory(Match, form=CurrentMatchForm, extra=0)
    if request.method == 'POST':
        formset = UpcomingMatchesFromset(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(current_matches)
    else:
        formset = UpcomingMatchesFromset(queryset=matches)

    return render(request, 'current_matches.html',
                  {
                      'category': category,
                      'matches': matches,
                      'formset': formset,

                  })


class UpcomingMatchForm(Form):
    id = CharField(widget=HiddenInput, required=False)
    group = CharField(widget=HiddenInput, required=False)
    description = CharField(widget=HiddenInput, required=False)

    table = ModelChoiceField(required=False, queryset=Table.objects.filter(matches__isnull=True))


def upcoming_matches(request):
    try:
        category = Category.objects.all()[:1].get()
    except Category.DoesNotExist:
        return redirect('category_add')

    match_groups = Match.objects.filter(status=Match.READY, group__isnull=False).values('group').distinct()
    all_matches = [dict(group=group.id, description=group, table=None) for group in Group.objects.filter(id__in=match_groups)]
    all_matches.extend(
        dict(id=match.id, description='%s : %s' % (match.player1, match.player2), table=match.table)
        for match in Match.objects.filter(status=Match.READY, group__isnull=True)
    )
    UpcomingMatchesFromset = formset_factory(UpcomingMatchForm, extra=0)
    if request.method == 'POST':
        formset = UpcomingMatchesFromset(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data['table']:
                    if form.cleaned_data['group']:
                        Match.objects.filter(group=form.cleaned_data['group']).update(table=form.cleaned_data['table'],
                                                                                      status=Match.PLAYING)
                    elif form.cleaned_data['id']:
                        match = Match.objects.get(id=form.cleaned_data['id'])
                        match.table = form.cleaned_data['table']
                        match.save()
            return redirect(upcoming_matches)
    else:
        formset = UpcomingMatchesFromset(initial=all_matches)

    return render(request, 'upcoming_matches.html', {
        'category': category,
        'matches': matches,
        'formset': formset,
    })


def matches(request, filter=''):
    try:
        category = Category.objects.all()[:1].get()
    except Category.DoesNotExist:
        return redirect('category_add')

    if filter == 'upcoming':
        groups = Group.objects.filter(status=0).select_related('category') \
            .annotate(member_count=Count("members")) \
            .order_by('member_count', 'id')

        single_matches = BracketSlot.objects.filter(status=0, bracket__category__gender__lt=2) \
            .with_two_players() \
            .select_related('player', 'bracket__category')
        single_matches = [(a, list(b)) for a, b in itertools.groupby(single_matches, lambda x: x.winner_goes_to_id)]
        single_matches = [(match, slots) for match, slots in single_matches if len(slots) == 2]

        #pair_matches = BracketSlot.objects.available_pairs().filter(status=0, bracket__category__gender__gte=2)\
        #                                         .select_related('player', 'bracket__category')
        #pair_matches = [(a, list(b)) for a, b in itertools.groupby(pair_matches, lambda x:x.winner_goes_to_id)]
        #pair_matches = [(match, slots) for match, slots in pair_matches if len(slots) == 2]
    else:
        groups = Group.objects.filter(status=1).select_related('category')

        single_matches = BracketSlot.objects.filter(status=1, bracket__category__gender__lt=2) \
            .select_related('player', 'bracket__category')
        single_matches = [(a, list(b)) for a, b in itertools.groupby(single_matches, lambda x: x.winner_goes_to_id)]
        single_matches = [(match, slots) for match, slots in single_matches if len(slots) == 2]

        #pair_matches = BracketSlot.objects.filter(status=1, bracket__category__gender__gte=2)\
        #                                         .select_related('player', 'bracket__category')
        #pair_matches = [(a, list(b)) for a, b in itertools.groupby(pair_matches, lambda x:x.winner_goes_to_id)]
        #pair_matches = [(match, slots) for match, slots in pair_matches if len(slots) == 2]

    available_tables = Table.objects.annotate(count1=Count('bracketslot'), count2=Count('group')) \
        .filter(count1=0, count2=0) \
        .order_by('id')
    return render(request, 'matches.html',
                  {
                      'category': category,
                      'mode': filter,
                      'matches': single_matches,
                      'groups': groups,
                      #'pairs': pair_matches,
                      'available_tables': available_tables,
                  })