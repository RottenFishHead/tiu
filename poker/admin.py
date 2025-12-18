# poker_session/admin.py
from django.contrib import admin
from .models import PokerSession, Casino

@admin.register(PokerSession)
class PokerSessionAdmin(admin.ModelAdmin):
    list_display = ['player', 'casino', 'stakes', 'hours', 'buy_in', 'cash_out']
    list_filter = ['player', 'casino', ]
    search_fields = ['player__username', 'casino__name']
    date_hierarchy = 'date'
    ordering = [ 'date']

@admin.register(Casino)
class CasinoAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
