from django.contrib import admin
from django.utils import timezone

from .models import Account, Bill, AccountWithdrawal, BillPayment,WorkEntry \
    , MileageEntry


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "institution", "number_last4", "is_active")
    list_filter = ("is_active", "institution")
    search_fields = ("name", "institution", "number_last4")
    ordering = ("name",)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "amount",
        "due_day",
        "is_auto_pay",
        "account",
        "active",
        "created_at",
    )
    list_filter = ("active", "is_auto_pay", "account", "due_day", "created_at")
    search_fields = ("name", "account__name", "notes")
    ordering = ("active", "due_day", "name")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("account",)


@admin.register(AccountWithdrawal)
class AccountWithdrawalAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "date", "method", "bill", "memo")
    list_filter = ("account", "method", "date", "created_at")
    search_fields = ("account__name", "bill__name", "memo")
    date_hierarchy = "date"
    ordering = ("-date", "-id")
    autocomplete_fields = ("account", "bill")


@admin.register(BillPayment)
class BillPaymentAdmin(admin.ModelAdmin):
    list_display = ("bill", "account", "amount", "date_paid", "has_receipt")
    list_filter = ("account", "bill__is_auto_pay", "date_paid", "created_at")
    search_fields = ("bill__name", "account__name", "notes")
    date_hierarchy = "date_paid"
    ordering = ("-date_paid", "-id")
    autocomplete_fields = ("bill", "account")
    readonly_fields = ("created_at", "updated_at")

    def has_receipt(self, obj):
        return bool(obj.receipt_image)
    has_receipt.boolean = True
    has_receipt.short_description = "Receipt?"


@admin.register(WorkEntry)
class WorkEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "hours", "hourly_rate", "amount", "description")
    list_filter = ("date", "hourly_rate", "created_at")
    search_fields = ("description", "notes")
    date_hierarchy = "date"
    ordering = ("-date", "-id")


@admin.register(MileageEntry)
class MileageEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "miles", "rate_per_mile", "amount", "description")
    list_filter = ("date", "rate_per_mile", "created_at")
    search_fields = ("description", "notes")
    date_hierarchy = "date"
    ordering = ("-date", "-id")