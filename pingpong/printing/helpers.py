import codecs
import os
from django.conf import settings
from django.template.loader import render_to_string
from pingpong.group.models import GroupMember


def html_group_card(category):
    members = GroupMember.objects.filter(group__category=category)\
                                        .select_related('group', 'player')\
                                        .order_by('group', '-leader', 'player__surname')
    return render_to_string('print_group.html', {'members': members})


def html_match_card(matches):
    return render_to_string('print_match.html', {'matches': matches})


def print_groups(category):
    if not settings.PRINT_DIRECTORY:
        return

    with codecs.open(os.path.join(settings.PRINT_DIRECTORY, 'category_%s_groups.html' % category.id), 'wb', encoding='utf8') as f:
        html = unicode(html_group_card(category))
        f.write(html)


def print_matches(matches):
    if not settings.PRINT_DIRECTORY:
        return

    match_ids = ','.join(str(m.id) for m in matches)

    with codecs.open(os.path.join(settings.PRINT_DIRECTORY, 'matches_%s.html' % match_ids), 'wb', encoding='utf8') as f:
        html = unicode(html_match_card(matches))
        f.write(html)