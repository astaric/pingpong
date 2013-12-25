import re

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import CharField, HiddenInput, Form
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, ModelForm, ModelChoiceField
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from pingpong.models import Table, Category, Match, Group
from pingpong.printing.helpers import print_matches


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

    return render(request, 'current_matches.html', {
        'category': category,
        'matches': matches,
        'formset': formset,
    })


class UpcomingMatchForm(Form):
    id = CharField(widget=HiddenInput, required=False)
    group = CharField(widget=HiddenInput, required=False)
    description = CharField(widget=HiddenInput, required=False)

    table = ModelChoiceField(required=False, queryset=Table.objects.filter(all_matches__isnull=True))


def upcoming_matches(request):
    try:
        category = Category.objects.all()[:1].get()
    except Category.DoesNotExist:
        return redirect('category_add')

    match_groups = Match.objects.filter(status=Match.READY, group__isnull=False).values('group').distinct()

    bracket_matches = []
    for match in Match.objects.filter(status=Match.READY, group__isnull=True):
        b = match.player1_bracket_slot.bracket.name[0]
        l = match.player1_bracket_slot.level
        c = match.player1.category.name
        bracket_matches.append(dict(id=match.id, description=mark_safe('%s <b>%s</b> %s %s : %s' % (b, l, c, match.player1, match.player2)), table=match.table))

    group_matches = [dict(group=group.id, description=group, table=None) for group in
                     Group.objects.filter(id__in=match_groups)]
    double_matches = []
    for m in Match.objects.filter(status=Match.DOUBLE).exclude(Q(player1__isnull=True) | Q(player2__isnull=True)).select_related('player1', 'player2'):
        d1, d2 = m.player1.double, m.player2.double
        blocking_matches = Match.objects.filter(Q(player1=d1.player1) | Q(player1=d1.player2) | Q(player1=d2.player1) | Q(player1=d2.player2) |
                                                Q(player2=d1.player1) | Q(player2=d1.player2) | Q(player2=d2.player1) | Q(player2=d2.player2), status__lt=Match.COMPLETE)
        if not blocking_matches:
            b = m.player1_bracket_slot.bracket.name[0]
            l = m.player1_bracket_slot.level
            c = m.player1.category.name
            double_matches.append(dict(id=m.id, description=mark_safe('%s <b>%s</b> %s %s : %s' % (b, l, c, m.player1, m.player2)), table=m.table))

    UpcomingMatchesFromset = formset_factory(UpcomingMatchForm, extra=0)
    if request.method == 'POST':
        formset = UpcomingMatchesFromset(request.POST)
        if formset.is_valid():
            matches_to_print = []
            for form in formset:
                if form.cleaned_data['table']:
                    if form.cleaned_data['group']:
                        Match.objects.filter(group=form.cleaned_data['group']).update(table=form.cleaned_data['table'],
                                                                                      status=Match.PLAYING,
                                                                                      start_time=now())
                    elif form.cleaned_data['id']:
                        match = Match.objects.get(id=form.cleaned_data['id'])
                        match.table = form.cleaned_data['table']
                        match.save()
                        matches_to_print.append(match)

            if matches_to_print:
                print_matches(matches_to_print)
            return redirect(upcoming_matches)
    else:
        formset = UpcomingMatchesFromset(initial=group_matches + bracket_matches + double_matches)

    return render(request, 'upcoming_matches.html', {
        'category': category,
        'formset': formset,
    })
