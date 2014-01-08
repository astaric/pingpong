from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from pingpong.dashboard.forms import UpcomingMatchesFromset, SetScoreForm
from pingpong.models import Match


def dashboard(request):
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
            return redirect('dashboard')
    else:
        formset = UpcomingMatchesFromset(queryset=bracket_matches | group_matches | doubles_matches)

    return render(request, 'pingpong/dashboard/dashboard.html', {
        'formset': formset,
        'group_matches': group_matches,
        'bracket_matches': bracket_matches,
        'doubles_matches': doubles_matches,
    })


def set_score(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == 'POST':
        set_score_form = SetScoreForm(request.POST, instance=match)
        if set_score_form.is_valid():
            set_score_form.save()
            return redirect(reverse('dashboard'))

    if request.is_ajax():
        template = 'pingpong/snippets/set_score_form.html'
    else:
        template = 'pingpong/dashboard/set_score.html'
    return render(request, template, dict(
        matches=[match],
    ))


@require_http_methods('POST')
def clear_table(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if not match.status == Match.PLAYING:
        raise ValidationError("You can only clear table on matches that are currently playing.")

    if match.group_id is not None:
        Match.objects.filter(group=match.group_id).update(table=None, status=Match.PENDING)

    match.table = None
    match.status = Match.READY
    match.save()

    return redirect(reverse('dashboard'))
