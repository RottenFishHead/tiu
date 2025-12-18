# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .forms import IncomeForm
from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import Income
from expenses.models import Expense, FixedExpense
from datetime import datetime, date



def income_list(request):
    incomes = Income.objects.all()
    return render(request, 'income/income_list.html', {'incomes': incomes})

def income_detail(request, pk):
    income = get_object_or_404(Income, pk=pk)
    return render(request, 'income/income_detail.html', {'income': income})

def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user  # Assuming you are using authentication
            income.save()
            return redirect('income:income_list')
    else:
        form = IncomeForm()
    return render(request, 'income/income_form.html', {'form': form})

def income_edit(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user  # Assuming you are using authentication
            income.save()
            return redirect('income:income_detail', pk=income.pk)
    else:
        form = IncomeForm(instance=income)
    return render(request, 'income/income_form.html', {'form': form})

def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk)
    income.delete()
    return redirect('income:income_list')


@login_required
def monthly_income_view(request):

    # Calculate the start and end dates for the current month
    today = datetime.today()
    start_date = date(today.year, today.month, 1)
    end_date = date(today.year, today.month, today.day)

    # Filter incomes for the current user and current month
    monthly_incomes = Income.objects.filter(created__range=(start_date, end_date)
    )
    total_monthly_income = monthly_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
  # Filter expenses for the current user and current month
    monthly_expenses = Expense.objects.filter(created__range=(start_date, end_date))
    total_monthly_expenses = monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Filter fixed_expenses for the current user
    fixed_expenses = FixedExpense.objects.all()
    total_fixed_expenses = fixed_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_all_expenses = total_fixed_expenses + total_monthly_income

    # Calculate the net income
    net_income = total_monthly_income - (total_monthly_expenses + total_fixed_expenses)
    

    context = {
        'monthly_incomes': monthly_incomes,
        'total_monthly_income': total_monthly_income,
        'monthly_expenses': monthly_expenses,
        'total_monthly_expenses': total_monthly_expenses,
        'fixed_expenses': fixed_expenses,
        'total_fixed_expenses': total_fixed_expenses,
        'net_income': net_income,
        'start_date': start_date,
        'end_date': end_date,
        'total_all_expenses': total_all_expenses
    }

    return render(request, 'income/monthly_income.html', context)
