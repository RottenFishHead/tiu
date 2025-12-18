from django import forms
from .models import Expense, FixedExpense, Budget, Payment

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['user', 'category', 'name', 'amount', 'created']
        # Optionally, you can customize the widgets or add additional validation here

    # You can add custom validation methods or override default behavior here if needed
    
class FixedExpenseForm(forms.ModelForm):
    class Meta:
        model = FixedExpense
        fields = '__all__'


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'description']
        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['debt', 'savings', 'fixed_expense', 'amount_paid']