# poker_session/admin.py
from django.contrib import admin
from .models import PokerSession, Casino, PlayerTag, PlayerProfile, PlayerTendency, PlayerObservation

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

class PlayerTendencyInline(admin.TabularInline):
    model = PlayerTendency
    extra = 0


class PlayerObservationInline(admin.TabularInline):
    model = PlayerObservation
    extra = 0
    fields = ("street", "situation", "action", "takeaway", "reliability", "happened_at", "created")
    readonly_fields = ("created",)
    
    
@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "approximate_age", "summary")
    search_fields = ("display_name", "summary", "description", "tags__name")
    list_filter = ("tags",)


@admin.register(PlayerObservation)
class PlayerObservationAdmin(admin.ModelAdmin):
    list_display = ("player", "street", "reliability", "created")
    search_fields = ("player__display_name", "action", "takeaway", "situation")
    list_filter = ("street", "reliability")


@admin.register(PlayerTendency)
class PlayerTendencyAdmin(admin.ModelAdmin):
    list_display = ("player", "metric", "street", "value", "sample_size", "confidence", "updated")
    search_fields = ("player__display_name", "metric", "note")
    list_filter = ("metric", "street", "confidence")


admin.site.register(PlayerTag)