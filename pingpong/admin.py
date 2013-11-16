from django.contrib import admin

from .models import Player, Category


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'category']
    ordering = ['id']
    list_filter = ['category']


class CategoryAdmin(admin.ModelAdmin):
    ordering = ('gender', 'min_age')
    prepopulated_fields = {"name": ("gender", "min_age", "max_age")}


admin.site.register(Player, PlayerAdmin)
admin.site.register(Category, CategoryAdmin)
