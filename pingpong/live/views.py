import re

from django.core.exceptions import ValidationError
from django.forms import CharField, HiddenInput
from django.forms.models import modelformset_factory, ModelForm
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from pingpong.live.forms import UpcomingMatchesFromset
from pingpong.models import Category, Match


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
                scores = map(int, match.groups())
                self.instance.set_score(*scores)
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


def upcoming_matches(request):
    try:
        category = Category.objects.all()[:1].get()
    except Category.DoesNotExist:
        return redirect('category_add')

    group_matches = Match.ready_group_matches()
    bracket_matches = Match.ready_bracket_matches()
    doubles_matches = Match.ready_doubles_matches()

    if request.method == 'POST':
        formset = UpcomingMatchesFromset(request.POST)
        if formset.is_valid():
            instances = formset.save()
            matches_to_print = [instance for instance in instances
                                if instance is not None and instance.group is None]

            if matches_to_print:
                from pingpong.printing.helpers import print_matches
                print_matches(matches_to_print)
            return redirect(upcoming_matches)
    else:
        formset = UpcomingMatchesFromset(queryset=bracket_matches | group_matches | doubles_matches)

    return render(request, 'upcoming_matches.html', {
        'category': category,
        'formset': formset,
        'group_matches': group_matches,
        'bracket_matches': bracket_matches,
        'doubles_matches': doubles_matches,
    })
