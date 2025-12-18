# yourapp/admin.py
from django.contrib import admin
from .models import Income, Source

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'user', 'created')
    search_fields = ('amount', 'user__username')
    list_filter = ('source', 'user', 'created')
    date_hierarchy = 'created'


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'created')


admin.site.register(Source, SourceAdmin)