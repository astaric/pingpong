from django.shortcuts import render, redirect, get_object_or_404

from pingpong.live.forms import UpcomingMatchesFromset, CurrentMatchesFromset
from pingpong.models import Category, Match, Table


def current_matches(request):
    try:
        category = Category.objects.all()[:1].get()
    except Category.DoesNotExist:
        return redirect('category_add')

    current_matches = Match.current_matches()
    if request.method == 'POST':
        formset = CurrentMatchesFromset(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('current_matches')
    else:
        formset = CurrentMatchesFromset(queryset=current_matches)

    return render(request, 'current_matches.html', {
        'category': category,
        'matches': current_matches,
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
            return redirect('upcoming_matches')
    else:
        formset = UpcomingMatchesFromset(queryset=bracket_matches | group_matches | doubles_matches)

    return render(request, 'upcoming_matches.html', {
        'category': category,
        'formset': formset,
        'group_matches': group_matches,
        'bracket_matches': bracket_matches,
        'doubles_matches': doubles_matches,
    })


def set_score(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    return render(request, 'pingpong/dashboard/set_score.html', dict(
        table=table
    ))
