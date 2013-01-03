from django.contrib import admin

from . import models


class GroupAdmin(admin.ModelAdmin):
    pass


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


class GroupToBracketTransitionInline(admin.TabularInline):
    model = models.GroupToBracketTransition


class BracketSlotAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}  # Return empty perms dict thus hiding the model from admin index.

    inlines = (
        GroupToBracketTransitionInline,
    )


class BracketAdmin(admin.ModelAdmin):
    change_form_template = 'competition/bracket_admin_change.html'


class SetScoreAdmin(admin.ModelAdmin):
    pass


class TableAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.GroupMember, GroupMemberAdmin)
admin.site.register(models.Bracket, BracketAdmin)
admin.site.register(models.BracketSlot, BracketSlotAdmin)
#admin.site.register(models.GroupToBracketTransition, GroupToBracketTransitionAdmin)
admin.site.register(models.SetScore, SetScoreAdmin)
admin.site.register(models.Table, TableAdmin)
