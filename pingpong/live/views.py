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

    group_matches = Match.ready_group_matches()
    bracket_matches = Match.ready_bracket_matches()
    doubles_matches = Match.ready_doubles_matches()

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
        formset = UpcomingMatchesFromset(initial=group_matches + bracket_matches + doubles_matches)

    return render(request, 'upcoming_matches.html', {
        'category': category,
        'formset': formset,
        'group_matches': group_matches,
        'bracket_matches': bracket_matches,
        'doubles_matches': doubles_matches,
    })
