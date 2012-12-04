from collections import defaultdict, deque
import string

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ..models import Player, PlayerByGroup, Category, Group
from ..utils import shuffled


class PlayerAdmin(admin.ModelAdmin):
    actions = ['refresh_categories', 'create_groups']
    list_display = ['__unicode__', 'category']
    list_filter = ['category']

    def refresh_categories(self, request, queryset):
        queryset.update(category=None)
        for category in Category.objects.all():
            queryset.matching_category(category).update(category=category)
    refresh_categories.short_description = _("Refresh categories")

    def create_groups_from_leaders(self, request, leaders):
        category_leaders = defaultdict(list)
        for player in leaders:
            category_leaders[player.category_id].append(player)
        Group.objects.filter(category__in=category_leaders.keys()).delete()

        for category in category_leaders.keys():
            leaders = category_leaders[category]
            group_members = defaultdict(list)

            for i, leader in enumerate(leaders):
                group = Group.objects.create(name=string.ascii_uppercase[i], category_id=category)
                group_members[group].append(leader)

            leader_ids = [p.id for p in leaders]
            others = Player.objects.filter(category=category).exclude(id__in=leader_ids)
            unallocated_players = deque(shuffled(others))
            groups = deque(group_members.keys())
            tried = 0
            while unallocated_players:
                player = unallocated_players.popleft()
                if any(other.club == player.club for other in group_members[groups[0]] if other.club):
                    unallocated_players.append(player)
                    tried += 1
                    if tried > len(unallocated_players):
                        raise ValueError("Weird data")
                    continue
                else:
                    tried = 0
                group_members[groups[0]].append(player)
                groups.rotate(-1)

            Player.objects.filter(id__in=leader_ids).update(group_leader=True)
            Player.objects.filter(category=category).exclude(id__in=leader_ids).update(group_leader=False)
            for group in group_members.keys():
                member_ids = [p.id for p in group_members[group]]
                Player.objects.filter(id__in=member_ids).update(group=group)
    create_groups_from_leaders.short_description = _("Create groups")


class PlayerByGroupAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'group', 'group_member_no', 'group_leader')
    list_editable = ['group_member_no']
    list_filter = ['group']
    ordering = ('group', 'group_member_no', '-group_leader')

    def queryset(self, request):
        return self.model.objects.exclude(group=None)

    def __init__(self, *args, **kwargs):
        super(PlayerByGroupAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerByGroup, PlayerByGroupAdmin)