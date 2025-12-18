from django.urls import path
from .views import expense_list, expense_detail, expense_create, expense_update, expense_delete, monthly_expense_totals, monthly_expenses_list,\
    fixed_expense_list, fixed_expense_detail, fixed_expense_create, fixed_expense_update, fixed_expense_delete, \
        expense_overview, budget_list, create_budget, edit_budget, delete_budget, calculate_budget_remaining, \
            yearly_budget_remaining, debt_list, debt_details, savings_list, savings_details, create_payment
app_name = 'expenses' 

urlpatterns = [
    path('', expense_list, name='expense-list'),
    path('create/', expense_create, name='expense-create'), 
    path('<int:expense_id>/update/', expense_update, name='expense-update'),
    path('<int:expense_id>/delete/', expense_delete, name='expense-delete'),
    path('monthly-expense-totals/', monthly_expense_totals, name='monthly_expense_totals'),
    path('expenses/<int:month>/', monthly_expenses_list, name='monthly_expenses_list'),
    path('fixed-expenses/', fixed_expense_list, name='fixed_expense_list'),
    path('fixed-expenses/<int:pk>/', fixed_expense_detail, name='fixed_expense_detail'),
    path('fixed-expenses/create/', fixed_expense_create, name='fixed_expense_create'),
    path('fixed-expenses/<int:pk>/update/', fixed_expense_update, name='fixed_expense_update'),
    path('fixed-expenses/<int:pk>/delete/', fixed_expense_delete, name='fixed_expense_delete'),
    path('expense-overview/', expense_overview, name='expense-overview'),
    path('budget_list/', budget_list, name='budget_list'),
    path('budget_create/', create_budget, name='create_budget'),
    path('budgets_edit/<int:pk>/', edit_budget, name='edit_budget'),
    path('budgets_delete/<int:pk>/', delete_budget, name='delete_budget'),
    path('calculate_budget_remaining/', calculate_budget_remaining, name='calculate_budget_remaining'),
    path('yearly_budget_remaining/', yearly_budget_remaining, name='yearly_budget_remaining'),
    path('debt-list/', debt_list, name='debt_list'),
    path('debt-details/<int:debt_id>/', debt_details, name='debt_details'),
    path('savings-list/', savings_list, name='savings_list'),
    path('saving-details/<int:savings_id>/', savings_details, name='savings_details'),
    path('create_payment/', create_payment, name='create_payment'),
]