from django.contrib import admin
from .models import Expense, FixedExpense, Category, Budget,\
    Account, Debt, Payment, Savings

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ( 'category', 'name', 'amount', 'created', 'updated_at')
    list_filter = ('category', 'created')
    search_fields = ('name', 'user__username')  # Assuming User model has a 'username' field

# You can customize the display, filtering, and search options as needed

@admin.register(FixedExpense)
class FixedExpenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'frequency', 'autopay', 'amount', 'day_to_pay')
    list_filter = ('frequency', 'autopay', 'day_to_pay')
    search_fields = ('name', 'amount', 'day_to_pay')
    ordering = ('-day_to_pay',)
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Category, CategoryAdmin)

class BudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount')
    search_fields = ('category',)

admin.site.register(Budget, BudgetAdmin)

class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name',)

admin.site.register(Account, AccountAdmin)


class DebtAdmin(admin.ModelAdmin):
    list_display = ('name', 'owed', 'total_amount_paid')
    search_fields = ('name',)

admin.site.register(Debt, DebtAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('debt','savings', 'amount_paid',)
    search_fields = ('debt',)

admin.site.register(Payment, PaymentAdmin)

class SavingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal',)
    search_fields = ('name',)

admin.site.register(Savings, SavingsAdmin)