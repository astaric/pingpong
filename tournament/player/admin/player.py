from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ..models import Player, PlayerByGroup, Category, Group

def refresh_categories(modeladmin, request, queryset):
    queryset.update(category=None)
    for category in Category.objects.all():
       queryset.matching_category(category).update(category=category)
refresh_categories.short_description = _("Refresh categories")

def create_groups(modeladmin, request, queryset):
    Group.create_from_leaders(queryset)
create_groups.short_description = _("Create groups")


class PlayerAdmin(admin.ModelAdmin):
    actions = [refresh_categories, create_groups]
    list_display = ['__unicode__', 'category']
    list_filter = ['category']

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