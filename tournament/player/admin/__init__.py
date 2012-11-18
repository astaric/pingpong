from django.contrib import admin

from player import PlayerAdmin

from ..models import Player, Category
from .. import views


class CategoryAdmin(admin.ModelAdmin):
    ordering = ('gender', 'min_age')
    prepopulated_fields = {"name": ("gender","min_age", "max_age")}

admin.site.register(Player, PlayerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.admin_view(views.show)