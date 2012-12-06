from collections import defaultdict, deque
from math import ceil, log
import itertools
import string

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from ..models import Player, PlayerByGroup, Category, Group, GroupMember, Bracket, Match, GroupToBracketTransition
from ..utils import alternate, group, shuffled


class PlayerAdmin(admin.ModelAdmin):
    actions = ['refresh_categories', 'create_groups_from_leaders']
    list_display = ['__unicode__', 'category']
    list_filter = ['category']

    def refresh_categories(self, request, queryset):
        selected_ids = list(queryset.values_list('id', flat=True))
        queryset = Player.objects.filter(id__in=selected_ids)
        queryset.update(category=None)
        for category in Category.objects.all():
            queryset.matching_category(category).update(category=category)
    refresh_categories.short_description = _("Refresh categories")

    def create_groups_from_leaders(self, request, leaders):
        category_leaders = {category: list(leaders)
                            for category, leaders in itertools.groupby(leaders.order_by('category'),
                                                                       lambda x: x.category_id)}
        Group.objects.filter(category__in=category_leaders.keys()).delete()

        for category, leaders in category_leaders.items():
            self.create_groups_for_category(category, leaders)

    def create_groups_for_category(self, category, leaders):
        groups = deque(())
        members = []
        clubs = defaultdict(set)

        for i, leader in enumerate(leaders):
            group = Group.objects.create(name=string.ascii_uppercase[i], category_id=category)
            groups.append(group)
            members.append(GroupMember(player=leader, group=group, leader=True))
            if leader.club:
                clubs[group].add(leader.club)

        leader_ids = [l.id for l in leaders]
        unallocated_players = deque(shuffled(
            Player.objects.filter(category=category).exclude(id__in=leader_ids)))

        tried = 0
        while unallocated_players:
            group = groups[0]
            player = unallocated_players.popleft()
            if player.club:
                if player.club in clubs[group]:
                    unallocated_players.append(player)
                    tried += 1
                    if tried > len(unallocated_players):
                        raise ValueError("Weird data")
                    continue
                else:
                    clubs[group].add(player.club)
                    tried = 0

            members.append(GroupMember(player=player, group=group))
            groups.rotate(-1)

        GroupMember.objects.bulk_create(members)
    create_groups_from_leaders.short_description = _("Create groups")

    def create_single_elimination_bracket(self, levels, **kwargs):
        brackets = [[] for i in range(levels)]

        def recursively_create_brackets(parent, level):
            if level < 0:
                return
            for i in range(2):
                bracket = Bracket.objects.create(level=level, winner_goes_to=parent, **kwargs)
                brackets[level].append(bracket)
                recursively_create_brackets(bracket, level - 1)
        finale = Bracket.objects.create(level=levels - 1, **kwargs)
        brackets[-1].append(finale)
        recursively_create_brackets(finale, levels - 2)
        return brackets

    def create_group_transitions(self, groups, **kwargs):
        # We currently assume that the groups contain up to 4
        # players, first two players go to the winners bracket
        # and the last two players go to the losers bracket.
        groups = list(groups.annotate(Count('groupmember')))
        for group in groups:
            assert group.groupmember__count <= 4

        bracket_levels = int((ceil(log(len(groups), 2)))) + 1
        winner_brackets = self.create_single_elimination_bracket(levels=bracket_levels, **kwargs)
        loser_brackets = self.create_single_elimination_bracket(levels=bracket_levels, **kwargs)

        transitions = []
        # Add dummy groups so the group count is equal to bracket size
        groups = groups + [Group(name="?")] * (len(winner_brackets[0]) - len(groups))
        for brackets, places in ((winner_brackets, (1, 2)), (loser_brackets, (3, 4))):
            for bracket, group, place in zip(alternate(brackets[0], brackets[0]),
                                             alternate(groups, groups[::-1]),
                                             itertools.cycle(places)):
                if group.id and place <= group.groupmember__count:
                    transitions.append(
                        GroupToBracketTransition.objects.create(group=group, place=place, bracket=bracket))
        return transitions


class PlayerByGroupAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'group', 'group_member_no', 'group_leader')
    list_editable = ['group_member_no']
    list_filter = ['group']
    ordering = ('group', 'group_member_no', '-group_leader', 'surname')

    def queryset(self, request):
        return self.model.objects.exclude(group=None)

    def __init__(self, *args, **kwargs):
        super(PlayerByGroupAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerByGroup, PlayerByGroupAdmin)
