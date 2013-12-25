from django.contrib import admin

from .models import Player, Category, GroupMember, Group


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'category']
    ordering = ['id']
    list_filter = ['category']


class CategoryAdmin(admin.ModelAdmin):
    ordering = ('gender', 'min_age')
    prepopulated_fields = {"name": ("gender", "min_age", "max_age")}


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


class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    fields = ('player', 'leader', 'place')
    #readonly_fields = ('player', 'leader')
    extra = 0

    def queryset(self, request):
        return self.model.objects.order_by('group', 'place', '-leader', 'player__surname')


class GroupAdmin(admin.ModelAdmin):
    ordering = ('category', 'id')

    inlines = (
        GroupMemberInline,
    )

    class Media:
        css = {'all': ('css/hide_admin_original.css',)}

admin.site.register(Player, PlayerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Group, GroupAdmin)
