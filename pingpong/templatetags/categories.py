from django import template
from django.db.models import Count
from pingpong.bracket.models import Bracket
from pingpong.models import Category, GroupMember
from pingpong.signup.forms import CategoryEditForm
from pingpong.signup.views import players_formset

register = template.Library()

@register.inclusion_tag('pingpong/snippets/category_list.html')
def list_categories(category):
    categories = Category.objects.filter(type=category.type).annotate(player_count=Count('players'))
    return {
        'categories': categories
    }


@register.inclusion_tag('pingpong/snippets/edit_category_form.html', takes_context=True)
def edit_category(context, category):
    if 'category_fields_form' in context:
        category_fields = context['category_fields_form']
    else:
        category_fields = CategoryEditForm(instance=category, prefix='category_fields')

    return {
        'panel': True,
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
        'panel': True,
        'category': category,
        'players_formset': players,
    }


@register.inclusion_tag('pingpong/snippets/groups.html')
def show_groups(category):
    members = GroupMember.for_category(category)

    class AnonymousUser:
        @staticmethod
        def is_authenticated():
            return False

    return {
        'group_members': members,
        'user': AnonymousUser,
    }


@register.inclusion_tag('pingpong/snippets/brackets.html')
def show_brackets(category):
    brackets = Bracket.objects.filter(category=category)

    return {
        'brackets': brackets,
    }