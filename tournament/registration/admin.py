import itertools

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ..competition import actions as group_actions
from .models import Player, Category
from ..competition import models as group_models
from . import views


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
                                                                       lambda x: x.category)}

        for category, leaders in category_leaders.items():
            group_actions.create_groups_from_leaders(category.id, leaders)
            group_actions.create_brackets(category)
    create_groups_from_leaders.short_description = _("Create groups")


class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('player', 'group', 'place', 'leader')
    list_editable = ['place']
    list_filter = ['group']
    ordering = ('group', 'place', '-leader', 'player__surname')

    def queryset(self, request):
        return self.model.objects.exclude(group=None)

    def __init__(self, *args, **kwargs):
        super(GroupMemberAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


class CategoryAdmin(admin.ModelAdmin):
    ordering = ('gender', 'min_age')
    prepopulated_fields = {"name": ("gender", "min_age", "max_age")}


admin.site.register(Player, PlayerAdmin)
admin.site.register(group_models.GroupMember, GroupMemberAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.admin_view(views.player_details)
