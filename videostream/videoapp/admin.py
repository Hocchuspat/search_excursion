from django.contrib import admin

# admin.py
from django.contrib import admin
from .models import Excursion, Favorite

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'excursion')
    search_fields = ('user__username', 'excursion__title')

admin.site.register(Excursion)
admin.site.register(Favorite, FavoriteAdmin)


