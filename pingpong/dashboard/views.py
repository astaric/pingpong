import json
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from pingpong.dashboard.forms import SetScoreForm, SetTableForm, GroupScoresFormset
from pingpong.models import Match, Table, Group, GroupMember
from pingpong.printing.helpers import print_matches


def dashboard(request):
    return render(request, 'pingpong/dashboard/dashboard.html')


def match_history(request):
    return render(request, 'pingpong/dashboard/match_history.html')


@login_required
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
        match=match,
        form=SetScoreForm(instance=match),
    ))


@login_required
def set_table(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == "POST":
        form = SetTableForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            if match.group_id is None:
                print_matches(match)
            return redirect(reverse('dashboard'))

    if request.is_ajax():
        template = 'pingpong/dashboard/set_table_modal.html'
    else:
        template = 'pingpong/dashboard/set_table.html'
    return render(request, template, dict(
        match=match,
    ))


@login_required
@require_http_methods('POST')
def clear_table(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if not match.status == Match.PLAYING:
        raise ValidationError(
            "You can only clear table on matches that are currently playing.")

    if match.group_id is not None:
        Match.objects.filter(group=match.group_id).update(table=None,
                                                          status=Match.PENDING)

    match.table = None
    match.status = Match.READY
    match.save()

    return redirect(reverse('dashboard'))


def upcoming_matches(request):
    response_data = []
    response_data.extend([
        dict(id=match.id,
             type='Group',
             group=unicode(match.group))
        for match in Match.ready_group_matches()
    ])
    response_data.extend([
        dict(id=match.id,
             type='Bracket',
             player1=unicode(match.player1),
             player2=unicode(match.player2))
        for match in Match.ready_bracket_matches()
    ])
    response_data.extend([
        dict(id=match.id,
             type='Double',
             player1=unicode(match.player1),
             player2=unicode(match.player2))
        for match in Match.ready_doubles_matches()
    ])
    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


def tables(request):
    response_data = []
    for table in Table.objects.order_by('display_order'):
        match = table.current_matches()
        if match:
            match = match[0]
            response_data.append(dict(
                table_name=table.short_name,
                match_id=match.id,
                match=unicode(match),
            ))
        else:
            response_data.append(dict(table_name=table.short_name))

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


def match_details(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    response_data = dict(
        id=match.id,
        status=match.status
    )
    if match.group_id:
        response_data['group'] = unicode(match.group)
    else:
        response_data.update(dict(
            player1=unicode(match.player1),
            player2=unicode(match.player2),
        ))

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


@login_required
def set_group_scores(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        group_scores = GroupScoresFormset(request.POST)
        if group_scores.is_valid():
            group_scores.save()
            return redirect(reverse('dashboard'))
    else:
        group_scores = GroupScoresFormset(queryset=GroupMember.for_group(group))

    return render(request, 'pingpong/category/edit_group.html',
                  dict(group=group,
                       formset=group_scores))
