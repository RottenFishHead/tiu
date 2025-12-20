from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, FixedExpense, Category, Budget, Debt, Payment, Savings
from .forms import ExpenseForm, FixedExpenseForm, BudgetForm, PaymentForm
from django.utils import timezone
from django.db.models import Sum, F, DecimalField, Value
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils.timezone import now
import calendar
from datetime import datetime


@login_required(login_url='/account/login/')
def expense_list(request):
    current_month = timezone.now().month
    current_year = timezone.now().year

    # Get all expenses for the current month and year
    expenses = Expense.objects.filter(created__month=current_month, created__year=current_year)

    # Group expenses by category and calculate total expenses for each category
    expenses_by_category = expenses.values('category__name') \
        .annotate(total_category_expenses=Sum('amount'))

    # Group expenses by category for detailed listing
    grouped_expenses = {}
    for expense in expenses:
        category_name = expense.category.name
        if category_name not in grouped_expenses:
            grouped_expenses[category_name] = []
        grouped_expenses[category_name].append(expense)

    context = {
        'expenses': expenses,
        'current_month': current_month,
        'expenses_by_category': expenses_by_category,
        'total_expenses': expenses.aggregate(Sum('amount'))['amount__sum'],
        'grouped_expenses': grouped_expenses,
    }

    return render(request, 'expenses/expense_list.html', context)

@login_required(login_url='/account/login/')
def expense_detail(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    context = {'expense': expense}
    return render(request, 'expenses/expense_detail.html', context)

@login_required(login_url='/account/login/')
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expenses:expense-list')
    else:
        form = ExpenseForm()
    
    context = {'form': form}
    return render(request, 'expenses/expense_form.html', context)


@login_required(login_url='/account/login/')
def expense_update(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expenses:expense-list')
    else:
        form = ExpenseForm(instance=expense)

    context = {'form': form, 'expense': expense}
    return render(request, 'expenses/expense_form.html', context)

@login_required(login_url='/account/login/')
def expense_delete(request, expense_id):
    expense = get_object_or_404(Expense, pk=expense_id)
    expense.delete()
    return redirect('expenses:expense-list')


def monthly_expense_totals(request):
    # Get the current year
    current_year = datetime.now().year
    
    # Initialize a dictionary to hold monthly totals
    monthly_totals = {}
    
    # Loop through each month of the year
    for month in range(1, 13):
        # Get expenses for the current month and year
        expenses = Expense.objects.filter(created__year=current_year, created__month=month)
        
        # Calculate total expenses for the month
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        # Add the total to the dictionary
        month_name = calendar.month_name[month]
        
        # Add the total to the dictionary
        monthly_totals[month_name] = total_expenses
    
    # Pass the monthly totals to the template for rendering
    return render(request, 'expenses/monthly_totals.html', {'monthly_totals': monthly_totals})

def monthly_expenses_list(request, month):
    # Parse the month parameter from the URL or request data
    # Ensure month is an integer between 1 and 12
    try:
        month = int(month)
        if month < 1 or month > 12:
            raise ValueError("Month should be between 1 and 12")
    except ValueError:
        # Handle invalid month parameter, for example, redirect to an error page
        return render(request, 'error.html', {'error_message': 'Invalid month parameter'})
    
    # Get the current year
    current_year = datetime.now().year
    
    month_name = calendar.month_name[month]
    
    # Calculate total expenses for the month
# Get expenses for the specified month and year
    expenses = Expense.objects.filter(created__year=current_year, created__month=month)
    
    # Calculate total expenses for the month
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate total expenses for each category
    category_totals = expenses.values('category__name').annotate(total=Sum('amount'))
    
 # Group expenses by category
    category_list = expenses.values('category__name').annotate(total=Sum('amount'))
    
    # Get expenses for each category
    for category in category_list:
        category['expenses'] = Expense.objects.filter(created__year=current_year, created__month=month, category__name=category['category__name'])
    
    
    
    context={
        'category_totals': category_totals,
        'category_list': category_list,
        'expenses': expenses, 
        'month': month, 
        'month_name': month_name, 
        'current_year':current_year,
        'total_expenses': total_expenses,  
    }
    
    
    # Pass the list of expenses to the template for rendering
    return render(request, 'expenses/monthly_expenses_list.html', context)


@login_required(login_url='/account/login/')
def expense_overview(request):
    # Data for expense_list
    current_month = timezone.now().month
    current_year = timezone.now().year
    expenses = Expense.objects.filter(created__month=current_month, created__year=current_year)
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum']

    # Data for fixed_expense_list
    fixed_expenses = FixedExpense.objects.all()

    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'fixed_expenses': fixed_expenses,
    }

    return render(request, 'expenses/expense_overview.html', context)


#+++++++++++++Fixed Expenses +++++++++++++++++++++++++++++++++


@login_required(login_url='/account/login/')
def fixed_expense_list(request):
        fixed_expenses = FixedExpense.objects.all() 
        today = datetime.now().day
        total_amount = sum(fixed_expense.amount for fixed_expense in fixed_expenses)
        context = ({
            'fixed_expenses': fixed_expenses,
            'total_amount':total_amount,
            'today': today
        })
        return render(request, 'expenses/fixed_expense_list.html', context)

@login_required(login_url='/account/login/')
def fixed_expense_detail(request, pk):
    fixed_expense = get_object_or_404(FixedExpense, pk=pk)
    return render(request, 'expenses/fixed_expense_detail.html', {'fixed_expense': fixed_expense})

@login_required(login_url='/account/login/')
def fixed_expense_create(request):
    if request.method == 'POST':
        form = FixedExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expenses:fixed_expense_list')
    else:
        form = FixedExpenseForm()
    return render(request, 'expenses/fixed_expense_form.html', {'form': form})

@login_required(login_url='/account/login/')
def fixed_expense_update(request, pk):
    fixed_expense = get_object_or_404(FixedExpense, pk=pk)
    if request.method == 'POST':
        form = FixedExpenseForm(request.POST, instance=fixed_expense)
        if form.is_valid():
            form.save()
            return redirect('expenses:fixed_expense_list')
    else:
        form = FixedExpenseForm(instance=fixed_expense)
    return render(request, 'expenses/fixed_expense_form.html', {'form': form})

@login_required(login_url='/account/login/')
def fixed_expense_delete(request, pk):
    fixed_expense = get_object_or_404(FixedExpense, pk=pk)
    fixed_expense.delete()
    return redirect('expenses:fixed_expense_list')



@login_required(login_url='/account/login/')
def budget_list(request):
    budgets = Budget.objects.all()
    return render(request, 'expenses/budget_list.html', {'budgets': budgets})

@login_required(login_url='/account/login/')
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expenses:budget_list')
    else:
        form = BudgetForm()
    return render(request, 'expenses/budget_form.html', {'form': form, 'action': 'Create'})

@login_required(login_url='/account/login/')
def edit_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('expenses:budget_list')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'expenses/budget_form.html', {'form': form, 'action': 'Edit'})

@login_required(login_url='/account/login/')
def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    if request.method == 'POST':
        budget.delete()
        return redirect('expenses:budget_list')
    return render(request, 'expenses/budget_confirm_delete.html', {'budget': budget})

@login_required(login_url='/account/login/')
def calculate_budget_remaining(request):
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    categories = Category.objects.all()

    
    expenses = Expense.objects.filter(created__range=(first_day_of_month, last_day_of_month)) \
                              .values('category')\
                              .annotate(total_expenses=Coalesce(Sum('amount'), Value(0, output_field=DecimalField())))
    
    budgets = Budget.objects.all()\
                            .values('category')\
                            .annotate(total_budget=Coalesce(Sum('amount'), Value(0, output_field=DecimalField())))
    
    total_expenses_all = sum(item['total_expenses'] for item in expenses)
    total_budget_all = sum(item['total_budget'] for item in budgets)
    remaining_total = total_budget_all - total_expenses_all

    budget_remaining = []
    for category in categories:
        total_expenses = next((item['total_expenses'] for item in expenses if item['category'] == category.id), 0)
        total_budget = next((item['total_budget'] for item in budgets if item['category'] == category.id), 0)

        remaining_budget = total_budget - total_expenses
        budget_remaining.append({
            'category_name': category.name,
            'total_budget': total_budget,
            'total_expenses': total_expenses,
            'remaining_budget': remaining_budget
            
        })
    context={
            'budget_remaining': budget_remaining, 
             'total_expenses_all': total_expenses_all, 
             'total_budget_all': total_budget_all, 
             'remaining_total': remaining_total
        
    }

    return render(request, 'expenses/budget_expenses.html', context)

@login_required(login_url='/account/login/')
def yearly_budget_remaining(request):
    # Get the current year
    current_year = datetime.now().year

    # Get all categories
    categories = Category.objects.all()

    # Calculate the total expenses for each category in the current year
    expenses = Expense.objects.filter(created__year=current_year)\
                              .values('category')\
                              .annotate(total_expenses=Coalesce(Sum('amount'), Value(0, output_field=DecimalField())))

    # Get the budget for each category in the current year
    budgets = Budget.objects.filter(date__year=current_year)\
                            .values('category')\
                            .annotate(total_budget=Coalesce(Sum('amount'), Value(0, output_field=DecimalField())))

    # Create a list to store the remaining budget for each category
    budget_remaining = []

    # Calculate the remaining budget for each category
    for category in categories:
        total_expenses = next((item['total_expenses'] for item in expenses if item['category'] == category.id), 0)
        total_budget = next((item['total_budget'] for item in budgets if item['category'] == category.id), 0)

        remaining_budget = total_budget - total_expenses
        budget_remaining.append({
            'category_name': category.name,
            'total_budget': total_budget,
            'total_expenses': total_expenses,
            'remaining_budget': remaining_budget
        })

    # You can now pass the budget_remaining list to your template or use it as needed

    return render(request, 'expenses/yearly_budget_remaining.html', {'budget_remaining': budget_remaining})



@login_required(login_url='/account/login/')
def debt_list(request):
    debts = Debt.objects.all()
    context = {
        'debts': debts
    }

    return render(request, 'expenses/debt_list.html', context)

@login_required(login_url='/account/login/')
def debt_details(request, debt_id):
    debt = get_object_or_404(Debt, pk=debt_id)
    debt_left = debt.remaining_balance
    
    # Get John app earnings data if this is a van-related debt
    john_earnings = debt.remaining_after_john_earnings()
    
    context = {
        'debt': debt,
        'debt_left': debt_left,
        'john_earnings': john_earnings,
    }
    return render(request, 'expenses/debt_details.html', context)

@login_required(login_url='/account/login/')
def savings_list(request):
    savings = Savings.objects.all()
    context = {
        'savings': savings
    }

    return render(request, 'expenses/savings_list.html', context)


@login_required(login_url='/account/login/')
def savings_details(request, savings_id):
    saving = get_object_or_404(Savings, pk=savings_id)
    goal_left = (saving.goal - saving.total_amount_saved)
    context = {
        'saving': saving,
        'goal_left': goal_left
    }
    return render(request, 'expenses/saving_details.html', context)

@login_required(login_url='/account/login/')
def create_payment(request, debt_id):
    debt = get_object_or_404(Debt, pk=debt_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expenses:debt_list')  # Replace 'payment_list' with the URL name for your payment list view
    else:
        form = PaymentForm()
    return render(request, 'expenses/payment_form.html', {'form': form, 'debtor':debt})
