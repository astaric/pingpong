from django import template
from pingpong.models import Table, Player, GroupMember

register = template.Library()

@register.inclusion_tag('snippet/tables.html', takes_context=True)
def show_tables(context):
    tables = Table.objects.order_by('display_order').prefetch_related('bracketslot_set', 'group_set', 'group_set__category')
    return {
        'tables': tables,
    }


@register.inclusion_tag('snippet/table.html', takes_context=True)
def show_table(context, table):
    return {
        'table': table,
    }


@register.inclusion_tag('snippet/group.html', takes_context=True)
def show_group(context, group, members=None):
    if members is None:
        members = group.members.all()

    table_id = group.table.id if group.table is not None else None
    return {
        'table_id': table_id,
        'group': group,
        'members': members,
        'user': context['user'],
    }


@register.inclusion_tag('snippet/match.html', takes_context=True)
def show_group_match(context, group):
    edit_form = None
    if context['user'].is_authenticated():
        if group.status == 0:
            edit_form = 'set_table'
    return {
        'id': group.id,
        'id_prefix': 'group',
        'player1': group.category.description,
        'player2': group.name,
        'available_tables': context['available_tables'],
        'edit_form': edit_form,
    }


@register.inclusion_tag('snippet/match.html', takes_context=True)
def show_match(context, slots):
    slot1, slot2 = sorted(slots, key=lambda x:x.id)
    edit_form = None
    if context['user'].is_authenticated():
        if slot1.status == 0:
            edit_form = 'set_table'
        elif slot1.status == 1:
            edit_form = 'set_score'
    winners = slot1.bracket.name.startswith("F")
    return {
        'id': slot1.winner_goes_to,
        'id_prefix': 'match',
        'player1': slot1.player,
        'player2': slot2.player,
        'category': slot1.player.category,
        'extra': '',
        'available_tables': context['available_tables'],
        'edit_form': edit_form,
        'winners': winners,
    }


@register.inclusion_tag('snippet/players.html', takes_context=True)
def show_players(context, category):
    players = Player.objects.filter(category=category).order_by('surname')
    return {
        'category': category,
        'players': players,
        'user': context['user'],
    }

@register.inclusion_tag('snippet/category_groups.html', takes_context=True)
def show_groups(context, category):
    members = GroupMember.objects.filter(group__category=category).order_by('group', 'place', '-leader', 'player__surname')

    class AnonymousUser:
        @staticmethod
        def is_authenticated():
            return False

    return {
        'members': members,
        'user': AnonymousUser,
    }
