# poker_session/admin.py
from django.contrib import admin
from .models import PokerSession, Casino, PlayerTag, PlayerProfile, PlayerTendency,\
    PlayerObservation, ExploitTag, PlayerExploit, PokerNote, PokerNoteKeyword, StopIt
from django.db.models import Sum, F
from django.template.response import TemplateResponse

@admin.register(PokerSession)
class PokerSessionAdmin(admin.ModelAdmin):
    list_display = ['player', 'casino', 'stakes', 'hours', 'win_loss', 'win_rate_per_hour']
    list_filter = ['player', 'casino', ]
    search_fields = ['player__username', 'casino__name']
    date_hierarchy = 'date'
    ordering = [ 'date']

    def changelist_view(self, request, extra_context=None):
        # Provide aggregated totals for the current changelist queryset
        extra_context = extra_context or {}
        response = super().changelist_view(request, extra_context=extra_context)

        # When the default response is a TemplateResponse, we can add totals
        if isinstance(response, TemplateResponse):
            try:
                qs = response.context_data['cl'].queryset
                aggregates = qs.aggregate(
                    total_sessions=Sum('id'),
                    total_profit=Sum(F('cash_out') - F('buy_in')),
                    total_hours=Sum('hours'),
                )
                response.context_data['totals'] = {
                    'total_sessions': aggregates.get('total_sessions') or 0,
                    'total_profit': aggregates.get('total_profit') or 0,
                    'total_hours': aggregates.get('total_hours') or 0,
                }
            except Exception:
                # Fail silently if aggregates cannot be computed
                response.context_data['totals'] = None

        return response

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

@admin.register(ExploitTag)
class ExploitTagAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


@admin.register(PlayerExploit)
class PlayerExploitAdmin(admin.ModelAdmin):
    list_display = ("player", "tag", "strength", "confidence", "updated")
    search_fields = ("player__display_name", "tag__name", "note")
    list_filter = ("confidence",)


@admin.register(PokerNote)
class PokerNoteAdmin(admin.ModelAdmin):
    list_display = ("player", "title", "is_important", "updated")
    search_fields = ("title", "note", "keywords__name", "player__username")
    list_filter = ("is_important", "keywords")


@admin.register(PokerNoteKeyword)
class PokerNoteKeywordAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(StopIt)
class StopItAdmin(admin.ModelAdmin):
    list_display = ("stop", "state", "fails")
    list_display_links = ("stop", "state")
    search_fields = ("stop", "text")
  