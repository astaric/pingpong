from django.contrib import admin
from django import http
from django.core import urlresolvers
from django.db.models import Q

from . import models
from ..registration import models as registration_models


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
    model = models.GroupMember
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


class GroupToBracketTransitionInline(admin.TabularInline):
    model = models.GroupToBracketTransition


class BracketSlotAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}  # Return empty perms dict thus hiding the model from admin index.

    def get_form(self, request, obj=None, **kwargs):
        form = super(BracketSlotAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['player'].queryset = \
                registration_models.Player.objects.filter(Q(bracketslot__winner_goes_to=obj) | Q(id=obj.player_id))\
                                                  .distinct()
        return form

    inlines = (
        GroupToBracketTransitionInline,
    )

    def response_change(self, request, obj):
        if not obj:
            return super(BracketSlotAdmin, self).response_change(request, obj)

        return http.HttpResponseRedirect(urlresolvers.reverse('admin:competition_bracket_change', args=(obj.bracket_id,)))


class BracketAdmin(admin.ModelAdmin):
    change_form_template = 'competition/bracket_admin_change.html'
    ordering = ('category', 'id')

    class Media:
        css = {'all': ('css/competition_extras.css',)}


class SetScoreAdmin(admin.ModelAdmin):
    pass


class TableAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order']
    list_editable = ['display_order']


admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Bracket, BracketAdmin)
admin.site.register(models.BracketSlot, BracketSlotAdmin)
admin.site.register(models.SetScore, SetScoreAdmin)
admin.site.register(models.Table, TableAdmin)
