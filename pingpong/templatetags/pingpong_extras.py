from itertools import groupby

from django import template
from django.db.models import Count, Q
from django.template import TemplateSyntaxError, NodeList, Context
from django.template.loader import render_to_string

from pingpong.dashboard.forms import UpcomingMatchesFromset, GroupScoresFormset, SetScoreForm
from pingpong.models import Category, GroupMember, Table, Match, Bracket
from pingpong.signup.forms import CategoryEditForm
from pingpong.signup.views import players_formset


register = template.Library()


@register.inclusion_tag('pingpong/snippets/category_list.html', takes_context=True)
def list_categories(context, category):
    context['categories'] = Category.objects \
        .order_by('id') \
        .annotate(player_count=Count('players'))
    return context


@register.inclusion_tag('pingpong/snippets/edit_category_form.html', takes_context=True)
def edit_category(context, category):
    if 'category_fields_form' in context:
        category_fields = context['category_fields_form']
    else:
        category_fields = CategoryEditForm(instance=category, prefix='category_fields')

    return {
        'modal': False,
        'category': category,
        'category_fields_form': category_fields,
    }


@register.inclusion_tag('pingpong/snippets/edit_players_form.html', takes_context=True)
def edit_category_players(context, category):
    if 'players_formset' in context:
        players = context['players_formset']
    else:
        players = players_formset(category)

    return {
        'modal': False,
        'category': category,
        'players_formset': players,
    }


@register.inclusion_tag('pingpong/snippets/groups.html')
def show_groups(category):
    members = GroupMember.for_category(category)
    return {
        'group_members': members,
    }


@register.inclusion_tag('pingpong/snippets/group.html')
def show_group(group, members=None):
    if members is None:
        members = GroupMember.for_group(group)

    return {
        'group': group,
        'members': members,
    }


@register.inclusion_tag('pingpong/snippets/brackets.html')
def show_brackets(category):
    brackets = Bracket.objects.filter(category=category).order_by('id')

    return {
        'brackets': brackets,
    }


@register.tag
def panel(parser, token):
    bits = list(token.split_contents())
    if len(bits) == 1:
        bits.append('True')
    if len(bits) == 2:
        modal = parser.compile_filter(bits[1])
    else:
        raise TemplateSyntaxError("%r takes at most one argument" % bits[0])

    title = parser.parse(('body', 'footer', 'endpanel',))
    body = footer = NodeList()
    token = parser.next_token()
    if token.contents == 'body':
        body = parser.parse(('footer', 'endpanel',))
        token = parser.next_token()
    if token.contents == 'footer':
        footer = parser.parse(('endpanel',))
    parser.delete_first_token()
    return PanelNode(title, body, footer, modal)


class PanelNode(template.Node):
    def __init__(self, title, body, footer, modal):
        self.title = title
        self.body = body
        self.footer = footer
        self.modal = modal

    def render(self, context):
        modal = self.modal.resolve(context, True)
        if modal is None:
            modal = True
        if modal:
            template = 'pingpong/dialogs/modal.html'
        else:
            template = 'pingpong/dialogs/panel.html'

        return render_to_string(template, Context(dict(
            title=self.title.render(context),
            body=self.body.render(context),
            footer=self.footer.render(context),
        )))


@register.inclusion_tag('pingpong/snippets/tables.html', takes_context=True)
def show_tables(context):
    tables = Table.objects.order_by('display_order')
    matches = Match.objects \
        .filter(status=Match.PLAYING) \
        .order_by('table') \
        .select_related('player1', 'player2', 'player1__category', 'group')
    matches = {
        table_id: list(matches)
        for table_id, matches in groupby(matches, key=lambda x: x.table_id)
    }

    for table in tables:
        table._current_matches = matches.get(table.id, [])

    context['tables'] = tables
    return context


@register.inclusion_tag('pingpong/snippets/upcoming_matches.html', takes_context=True)
def upcoming_matches(context):
    if 'formset' in context:
        formset = context['formset']
    else:
        formset = UpcomingMatchesFromset(
            queryset=Match.ready_group_matches() | Match.ready_bracket_matches() | Match.ready_doubles_matches())
    context.update({
        'formset': formset,
        'group_matches': Match.ready_group_matches(),
        'bracket_matches': Match.ready_bracket_matches(),
        'doubles_matches': Match.ready_doubles_matches()
    })
    return context


@register.inclusion_tag('pingpong/snippets/match_history.html', takes_context=True)
def match_history(context, limit=None):
    matches = Match.objects \
        .filter(status=Match.COMPLETE) \
        .filter(Q(group__isnull=True) ^ Q(player1__isnull=True, player2__isnull=True)) \
        .order_by('-end_time')
    if limit:
        matches = matches[:limit]
    context.update({
        'old_matches': matches
    })
    return context


@register.inclusion_tag('pingpong/snippets/set_group_scores_form.html', takes_context=True)
def set_group_scores_form(context, group=None, css_only=False):
    if 'formset' in context:
        formset = context['formset']
    else:
        formset = GroupScoresFormset(queryset=GroupMember.for_group(group))
    context.update({
        'group': group,
        'css_only': css_only,
        'formset': formset,
    })

    return context


@register.inclusion_tag('pingpong/snippets/set_score_form.html', takes_context=True)
def set_score_form(context, match=None, css_only=False):
    context.update({
        'modal': False,
        'match': match,
        'form': SetScoreForm(instance=match),
        'css_only': css_only,
    })
    return context


@register.inclusion_tag('pingpong/snippets/set_table_form.html')
def set_table_form(match, modal=False):
    return {
        'modal': modal,
        'match': match,
        'tables': Table.objects.order_by('display_order').extra(
            select={
                "occupied": "SELECT COUNT(*) FROM pingpong_match m WHERE m.table_id=pingpong_table.id AND m.status = 2"
            }
        )
    }
