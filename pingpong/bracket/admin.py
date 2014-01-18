from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect
from pingpong.models import Player, Bracket, BracketSlot, GroupToBracketTransition


class GroupToBracketTransitionInline(admin.TabularInline):
    model = GroupToBracketTransition


class BracketSlotAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}  # Return empty perms dict thus hiding the model from admin index.

    def get_form(self, request, obj=None, **kwargs):
        form = super(BracketSlotAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['player'].queryset = \
                Player.objects.filter(category__type=1)
        return form

    inlines = (
        GroupToBracketTransitionInline,
    )

    def response_change(self, request, obj):
        if not obj:
            return super(BracketSlotAdmin, self).response_change(request, obj)

        return redirect(reverse('admin:bracket_bracket_change', args=(obj.bracket_id,)))


class BracketAdmin(admin.ModelAdmin):
    change_form_template = 'competition/bracket_admin_change.html'
    ordering = ('category', 'id')

    class Media:
        css = {'all': ('css/competition_extras.css',)}


admin.site.register(Bracket, BracketAdmin)
admin.site.register(BracketSlot, BracketSlotAdmin)
