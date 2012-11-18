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

    def save_model(self, request, obj, form, change):
        try:
            category = Category.objects.get(gender=obj.gender,
                                            min_age__lte=obj.age,
                                            max_age__gte=obj.age)
            obj.category = category
        except Category.DoesNotExist:
            pass
        obj.save()

class CategoryAdmin(admin.ModelAdmin):
    ordering = ('gender', 'min_age')
    prepopulated_fields = {"name": ("gender","min_age", "max_age")}

admin.site.register(Player, PlayerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.admin_view(views.show)