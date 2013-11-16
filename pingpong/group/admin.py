from django.contrib import admin
from django.contrib.admin import ModelAdmin
from pingpong.group.models import GroupMember, Group


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


class GroupAdmin(ModelAdmin):
    ordering = ('category', 'id')

    inlines = (
        GroupMemberInline,
    )

    class Media:
        css = {'all': ('css/hide_admin_original.css',)}

admin.site.register(Group, GroupAdmin)
