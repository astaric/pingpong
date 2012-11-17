from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Player, Category
from . import views

def refresh_categories(modeladmin, request, queryset):
    queryset.update(category=None)
    for category in Category.objects.all():
        queryset.filter(gender=category.gender,
                        age__gte=category.min_age,
                        age__lte=category.max_age).update(category=category)
refresh_categories.short_description = _("Refresh categories")

class PlayerAdmin(admin.ModelAdmin):
    actions = [refresh_categories]
    readonly_fields = ['category']

class CategoryAdmin(admin.ModelAdmin):
    ordering = ('gender', 'min_age')

admin.site.register(Player, PlayerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.admin_view(views.show)