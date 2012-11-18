from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ..models import Player, Category, Group

def refresh_categories(modeladmin, request, queryset):
    queryset.update(category=None)
    for category in Category.objects.all():
        Player.matching_category(category, queryset).update(category=category)
refresh_categories.short_description = _("Refresh categories")

def create_groups(modeladmin, request, queryset):
    Group.create_from_leaders(queryset)
create_groups.short_description = _("Create groups")


class PlayerAdmin(admin.ModelAdmin):
    actions = [refresh_categories, create_groups]
    list_display = ['__unicode__', 'category', 'group', 'group_member_no', 'group_leader']
    list_editable = ['group_member_no']
    list_filter = ['category', 'group']

    def save_model(self, request, obj, form, change):
        obj.update_category()
        obj.save()