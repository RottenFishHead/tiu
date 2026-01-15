from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
import json
from .models import Bill, Account, BillPayment, WorkEntry, MileageEntry
from .forms import BillForm, PayBillForm, WorkEntryForm, MileageEntryForm
from datetime import timedelta, date
from django.db.models import Sum, Q
from decimal import Decimal
import calendar



def _due_date_for_month(due_day: int, year: int, month: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    safe_day = min(due_day, last_day)
    return date(year, month, safe_day)

def dashboard(request):
    today = timezone.localdate()
    year, month = today.year, today.month
    current_month_name = today.strftime("%B")

    # ===== Bills (recurring, due_day-based) =====
    bills = (
        Bill.objects.filter(active=True)
        .select_related("account")
        .prefetch_related("payments")
    )

    overdue = []
    due_soon = []
    upcoming = []
    total_unpaid = Decimal("0.00")
    total_overdue = Decimal("0.00")
    total_due_soon = Decimal("0.00")
    soon_threshold = today + timedelta(days=7)

    for bill in bills:
        bill.due_date = _due_date_for_month(bill.due_day, year, month)
        bill.days_until_due = (bill.due_date - today).days
        bill.paid_this_month = bill.payments.filter(
            date_paid__year=year,
            date_paid__month=month,
        ).exists()

        if bill.paid_this_month:
            bill.due_status = "paid"
        else:
            total_unpaid += bill.amount
            if bill.due_date < today:
                bill.due_status = "overdue"
                overdue.append(bill)
                total_overdue += bill.amount
            elif bill.due_date <= soon_threshold:
                bill.due_status = "soon"
                due_soon.append(bill)
                total_due_soon += bill.amount
            else:
                bill.due_status = "upcoming"
                upcoming.append(bill)

    # Bills paid this month (history)
    paid_this_month = BillPayment.objects.select_related("bill", "account").filter(
        date_paid__year=year,
        date_paid__month=month,
    ).order_by("-date_paid")

    total_paid_this_month = (
        paid_this_month.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    )
    paid_this_month_count = paid_this_month.count()

    # ===== Hours this month =====
    work_entries = WorkEntry.objects.filter(date__year=year, date__month=month)
    work_summary = work_entries.aggregate(
        total_hours=Sum("hours"),
        total_amount=Sum("amount"),
    )
    hours_this_month = work_summary["total_hours"] or Decimal("0.00")
    hours_amount_this_month = work_summary["total_amount"] or Decimal("0.00")

    # ===== Mileage this month =====
    mileage_entries = MileageEntry.objects.filter(date__year=year, date__month=month)
    mileage_summary = mileage_entries.aggregate(
        total_miles=Sum("miles"),
        total_amount=Sum("amount"),
    )
    miles_this_month = mileage_summary["total_miles"] or Decimal("0.00")
    mileage_amount_this_month = mileage_summary["total_amount"] or Decimal("0.00")

    context = {
        "today": today,
        "current_month_name": current_month_name,
        "current_year": year,

        "total_unpaid": total_unpaid,
        "total_overdue": total_overdue,
        "total_due_soon": total_due_soon,

        "overdue_bills": overdue[:5],
        "due_soon_bills": due_soon[:5],
        "paid_this_month": paid_this_month[:5],
        "total_paid_this_month": total_paid_this_month,
        "paid_this_month_count": paid_this_month_count,

        # New bits:
        "hours_this_month": hours_this_month,
        "hours_amount_this_month": hours_amount_this_month,
        "miles_this_month": miles_this_month,
        "mileage_amount_this_month": mileage_amount_this_month,
    }
    return render(request, "john/dashboard.html", context)


def bill_list(request):
    today = timezone.localdate()
    current_day = today.day
    soon_threshold_day = (today + timedelta(days=7)).day

    # Get all active bills
    active_bills = Bill.objects.filter(active=True).order_by("due_day")
    
    # Get bills paid this month
    paid_bill_ids_this_month = BillPayment.objects.filter(
        date_paid__year=today.year,
        date_paid__month=today.month,
    ).values_list('bill_id', flat=True)

    # Unpaid bills this month
    bills = active_bills.exclude(id__in=paid_bill_ids_this_month)

    # Annotate each bill with helper attributes for the template
    for bill in bills:
        # Calculate days until due (approximate, within current month)
        if bill.due_day >= current_day:
            bill.days_until_due = bill.due_day - current_day
        else:
            # Bill is overdue this month
            bill.days_until_due = -(current_day - bill.due_day)
        
        # Store absolute value for display
        bill.days_until_due_abs = abs(bill.days_until_due)
        
        if bill.due_day < current_day:
            bill.due_status = "overdue"
        elif bill.due_day <= current_day + 7:
            bill.due_status = "soon"
        else:
            bill.due_status = "upcoming"

    context = {
        "bills": bills,
        "today": today,
    }
    return render(request, "john/bill_list.html", context)


def paid_bills(request):
    """
    Show all paid bills, filter/sortable by month and year.
    """
    payments = BillPayment.objects.select_related('bill', 'account').all()

    # GET parameters: ?year=2025&month=12
    year = request.GET.get("year")
    month = request.GET.get("month")

    if year:
        payments = payments.filter(date_paid__year=year)
    if month:
        payments = payments.filter(date_paid__month=month)

    payments = payments.order_by("-date_paid", "bill__name")

    # For dropdowns
    years = (
        BillPayment.objects
        .dates("date_paid", "year", order="DESC")
    )
    months = (
        BillPayment.objects
        .dates("date_paid", "month", order="ASC")
    )

    context = {
        "payments": payments,
        "years": years,
        "months": months,
        "selected_year": year,
        "selected_month": month,
    }
    return render(request, "john/paid_bills.html", context)


def bill_create(request):
    """
    Create a new bill.
    """
    if request.method == "POST":
        form = BillForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("john:bill_list")
    else:
        form = BillForm()
    return render(request, "john/bill_form.html", {"form": form, "title": "Add Bill"})


def bill_detail(request, pk):
    """
    View detailed information about a bill including payment history.
    """
    bill = get_object_or_404(Bill, pk=pk)
    payments = BillPayment.objects.filter(bill=bill).select_related('account').order_by('-date_paid')
    
    context = {
        "bill": bill,
        "payments": payments,
    }
    return render(request, "john/bill_detail.html", context)


def bill_edit(request, pk):
    """
    Edit an existing bill.
    """
    bill = get_object_or_404(Bill, pk=pk)

    if request.method == "POST":
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            return redirect("john:bill_list")
    else:
        form = BillForm(instance=bill)

    return render(
        request,
        "john/bill_form.html",
        {"form": form, "title": f"Edit Bill: {bill.name}"},
    )


def pay_bill(request, pk):
    """
    Button flow to mark a bill as paid.
    - GET: show a simple form with date_paid (default = today) and receipt upload.
    - POST: create a BillPayment record for this bill.
    """
    bill = get_object_or_404(Bill, pk=pk)

    if request.method == "POST":
        form = PayBillForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.bill = bill
            payment.account = bill.account
            # Don't override amount - use what's in the form
            if not payment.date_paid:
                payment.date_paid = timezone.localdate()
            payment.save()
            return redirect("john:paid_bills")
    else:
        initial = {
            "date_paid": timezone.localdate(),
            "amount": bill.amount,  # Default to bill amount, but user can change
        }
        form = PayBillForm(initial=initial)

    return render(request, "john/pay_bill.html", {"bill": bill, "form": form})


def time_entries(request):
    """
    List work entries (hours) with optional month/year filter and totals.
    """
    entries = WorkEntry.objects.all().order_by("-date", "-id")

    year = request.GET.get("year")
    month = request.GET.get("month")

    if year:
        entries = entries.filter(date__year=year)
    if month:
        entries = entries.filter(date__month=month)

    total_hours = entries.aggregate(total=Sum("hours"))["total"] or Decimal("0.00")
    total_amount = entries.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    years = WorkEntry.objects.dates("date", "year", order="DESC")
    months = WorkEntry.objects.dates("date", "month", order="ASC")

    context = {
        "entries": entries,
        "total_hours": total_hours,
        "total_amount": total_amount,
        "years": years,
        "months": months,
        "selected_year": year,
        "selected_month": month,
    }
    return render(request, "john/time_list.html", context)


def time_entry_create(request):
    """
    Create a new work entry.
    """
    if request.method == "POST":
        form = WorkEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("john:time_entries")
    else:
        form = WorkEntryForm(
            initial={
                "date": timezone.localdate(),
                "hourly_rate": Decimal("30.00"),
            }
        )

    return render(request, "john/time_form.html", {"form": form})


def time_entry_edit(request, pk):
    """
    Edit an existing work entry.
    """
    entry = WorkEntry.objects.get(pk=pk)
    if request.method == "POST":
        form = WorkEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("john:time_entries")
    else:
        form = WorkEntryForm(instance=entry)
    return render(request, "john/time_form.html", {"form": form, "entry": entry})


def time_entry_delete(request, pk):
    """
    Delete a work entry.
    """
    entry = WorkEntry.objects.get(pk=pk)
    if request.method == "POST":
        entry.delete()
        return redirect("john:time_entries")
    return render(request, "john/time_confirm_delete.html", {"entry": entry})


def mileage_entries(request):
    """
    List mileage entries with optional month/year filter and totals.
    """
    entries = MileageEntry.objects.all().order_by("-date", "-id")

    year = request.GET.get("year")
    month = request.GET.get("month")

    if year:
        entries = entries.filter(date__year=year)
    if month:
        entries = entries.filter(date__month=month)

    total_miles = entries.aggregate(total=Sum("miles"))["total"] or Decimal("0.00")
    total_amount = entries.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    years = MileageEntry.objects.dates("date", "year", order="DESC")
    months = MileageEntry.objects.dates("date", "month", order="ASC")

    context = {
        "entries": entries,
        "total_miles": total_miles,
        "total_amount": total_amount,
        "years": years,
        "months": months,
        "selected_year": year,
        "selected_month": month,
    }
    return render(request, "john/mileage_list.html", context)


def mileage_entry_create(request):
    """
    Create a new mileage entry.
    """
    if request.method == "POST":
        form = MileageEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("john:mileage_entries")
    else:
        form = MileageEntryForm(
            initial={
                "date": timezone.localdate(),
                "rate_per_mile": Decimal("0.655"),
            }
        )

    return render(request, "john/mileage_form.html", {"form": form})


def mileage_entry_edit(request, pk):
    """
    Edit an existing mileage entry.
    """
    entry = MileageEntry.objects.get(pk=pk)
    if request.method == "POST":
        form = MileageEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("john:mileage_entries")
    else:
        form = MileageEntryForm(instance=entry)
    return render(request, "john/mileage_form.html", {"form": form, "entry": entry})


def mileage_entry_delete(request, pk):
    """
    Delete a mileage entry.
    """
    entry = MileageEntry.objects.get(pk=pk)
    if request.method == "POST":
        entry.delete()
        return redirect("john:mileage_entries")
    return render(request, "john/mileage_confirm_delete.html", {"entry": entry})


def export_john_data(request):
    """
    Export all John app data to JSON format for PostgreSQL import.
    """
    from django.core.serializers import serialize
    
    data = {
        'accounts': json.loads(serialize('json', Account.objects.all())),
        'bills': json.loads(serialize('json', Bill.objects.all())),
        'bill_payments': json.loads(serialize('json', BillPayment.objects.all())),
        'work_entries': json.loads(serialize('json', WorkEntry.objects.all())),
        'mileage_entries': json.loads(serialize('json', MileageEntry.objects.all())),
        'account_withdrawals': json.loads(serialize('json', AccountWithdrawal.objects.all())),
    }
    
    response = JsonResponse(data, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="john_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response


def export_work_entries_json(request):
    """
    Export only work entries to JSON.
    """
    from django.core.serializers import serialize
    entries = WorkEntry.objects.all().order_by('-date')
    data = json.loads(serialize('json', entries))
    
    response = JsonResponse(data, safe=False, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="work_entries_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response


def export_mileage_entries_json(request):
    """
    Export only mileage entries to JSON.
    """
    from django.core.serializers import serialize
    entries = MileageEntry.objects.all().order_by('-date')
    data = json.loads(serialize('json', entries))
    
    response = JsonResponse(data, safe=False, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="mileage_entries_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response


def monthly_summary(request):
    """
    Summary report for a period:
    - type=month (default): filter by year + month
    - type=week: filter by a start_date and include 7 days

    Shows:
      - total bill payments
      - total hours + reimbursement
      - total mileage + reimbursement
      - grand total reimbursement
    """
    today = timezone.localdate()
    summary_type = request.GET.get("type", "month")
    if summary_type not in ("month", "week"):
        summary_type = "month"

    # Defaults
    year = None
    month = None
    start_date = None
    end_date = None

    # Build filters per summary type
    if summary_type == "week":
        # Week: use start_date param or Monday of current week
        start_param = request.GET.get("start_date")
        if start_param:
            try:
                start_date = date.fromisoformat(start_param)
            except ValueError:
                start_date = today - timedelta(days=today.weekday())
        else:
            start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

        period_label = f"Week of {start_date} to {end_date}"

        payment_filter = {"date_paid__range": (start_date, end_date)}
        work_filter = {"date__range": (start_date, end_date)}
        mileage_filter = {"date__range": (start_date, end_date)}

    else:
        # Month: use year/month params or current month
        year_param = request.GET.get("year")
        month_param = request.GET.get("month")

        try:
            year = int(year_param) if year_param else today.year
        except (TypeError, ValueError):
            year = today.year

        try:
            month = int(month_param) if month_param else today.month
        except (TypeError, ValueError):
            month = today.month

        period_label = date(year, month, 1).strftime("%B %Y")

        payment_filter = {"date_paid__year": year, "date_paid__month": month}
        work_filter = {"date__year": year, "date__month": month}
        mileage_filter = {"date__year": year, "date__month": month}

    # ====== Bill payments in period ======
    payments = BillPayment.objects.select_related("bill", "account").filter(
        **payment_filter
    )

    payments_total = (
        payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    )
    payments_count = payments.count()

    # Optional breakdowns (you can surface in template later if you want)
    totals_by_account = (
        payments.values("account__name")
        .annotate(total_amount=Sum("amount"))
        .order_by("account__name")
    )
    totals_by_type = (
        payments.values("bill__is_auto_pay")
        .annotate(total_amount=Sum("amount"))
        .order_by("bill__is_auto_pay")
    )

    # ====== Work hours in period ======
    work_entries = WorkEntry.objects.filter(**work_filter)
    work_summary = work_entries.aggregate(
        total_hours=Sum("hours"),
        total_amount=Sum("amount"),
    )
    hours_total = work_summary["total_hours"] or Decimal("0.00")
    hours_amount_total = work_summary["total_amount"] or Decimal("0.00")

    # ====== Mileage in period ======
    mileage_entries = MileageEntry.objects.filter(**mileage_filter)
    mileage_summary = mileage_entries.aggregate(
        total_miles=Sum("miles"),
        total_amount=Sum("amount"),
    )
    miles_total = mileage_summary["total_miles"] or Decimal("0.00")
    mileage_amount_total = mileage_summary["total_amount"] or Decimal("0.00")

    # Grand total reimbursement (hours + mileage)
    grand_total_reimbursement = (
        hours_amount_total + mileage_amount_total
    ).quantize(Decimal("0.01"))

    context = {
        "today": today,
        "summary_type": summary_type,
        "period_label": period_label,

        # For month UI
        "selected_year": year,
        "selected_month": month,

        # For week UI
        "start_date": start_date,
        "end_date": end_date,

        # Payments
        "payments": payments.order_by("-date_paid", "bill__name"),
        "payments_total": payments_total,
        "payments_count": payments_count,
        "totals_by_account": totals_by_account,
        "totals_by_type": totals_by_type,

        # Hours
        "work_entries": work_entries.order_by("-date"),
        "hours_total": hours_total,
        "hours_amount_total": hours_amount_total,

        # Mileage
        "mileage_entries": mileage_entries.order_by("-date"),
        "miles_total": miles_total,
        "mileage_amount_total": mileage_amount_total,

        # Combined
        "grand_total_reimbursement": grand_total_reimbursement,
    }
    return render(request, "john/monthly_summary.html", context)


def export_john_data(request):
    """
    Export all John app data to JSON format for PostgreSQL import.
    """
    from django.core.serializers import serialize
    from datetime import datetime
    
    data = {
        'accounts': json.loads(serialize('json', Account.objects.all())),
        'bills': json.loads(serialize('json', Bill.objects.all())),
        'bill_payments': json.loads(serialize('json', BillPayment.objects.all())),
        'work_entries': json.loads(serialize('json', WorkEntry.objects.all())),
        'mileage_entries': json.loads(serialize('json', MileageEntry.objects.all())),
    }
    
    response = JsonResponse(data, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="john_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response


def export_work_entries_json(request):
    """
    Export only work entries to JSON.
    """
    from django.core.serializers import serialize
    from datetime import datetime
    
    entries = WorkEntry.objects.all().order_by('-date')
    data = json.loads(serialize('json', entries))
    
    response = JsonResponse(data, safe=False, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="work_entries_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response


def export_mileage_entries_json(request):
    """
    Export only mileage entries to JSON.
    """
    from django.core.serializers import serialize
    from datetime import datetime
    
    entries = MileageEntry.objects.all().order_by('-date')
    data = json.loads(serialize('json', entries))
    
    response = JsonResponse(data, safe=False, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="mileage_entries_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response


def monthly_compensation_report(request):
    """
    View showing time and driving data with compensation grouped by month.
    """
    from django.db.models.functions import TruncMonth
    from datetime import datetime
    
    # Get year filter if provided
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    # Get all work entries and mileage entries
    work_entries = WorkEntry.objects.all()
    mileage_entries = MileageEntry.objects.all()
    
    # Apply filters if provided
    if year:
        work_entries = work_entries.filter(date__year=year)
        mileage_entries = mileage_entries.filter(date__year=year)
    if month:
        work_entries = work_entries.filter(date__month=month)
        mileage_entries = mileage_entries.filter(date__month=month)
    
    # Group by month
    work_by_month = work_entries.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_hours=Sum('hours'),
        total_amount=Sum('amount')
    ).order_by('-month')
    
    mileage_by_month = mileage_entries.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_miles=Sum('miles'),
        total_amount=Sum('amount')
    ).order_by('-month')
    
    # Combine data by month
    monthly_data = {}
    
    for entry in work_by_month:
        month_key = entry['month']
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'month': month_key,
                'hours': Decimal('0.00'),
                'hours_amount': Decimal('0.00'),
                'miles': Decimal('0.00'),
                'mileage_amount': Decimal('0.00'),
            }
        monthly_data[month_key]['hours'] = entry['total_hours'] or Decimal('0.00')
        monthly_data[month_key]['hours_amount'] = entry['total_amount'] or Decimal('0.00')
    
    for entry in mileage_by_month:
        month_key = entry['month']
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'month': month_key,
                'hours': Decimal('0.00'),
                'hours_amount': Decimal('0.00'),
                'miles': Decimal('0.00'),
                'mileage_amount': Decimal('0.00'),
            }
        monthly_data[month_key]['miles'] = entry['total_miles'] or Decimal('0.00')
        monthly_data[month_key]['mileage_amount'] = entry['total_amount'] or Decimal('0.00')
    
    # Calculate totals for each month
    for month_key in monthly_data:
        monthly_data[month_key]['total_compensation'] = (
            monthly_data[month_key]['hours_amount'] + 
            monthly_data[month_key]['mileage_amount']
        )
    
    # Convert to sorted list
    monthly_list = sorted(monthly_data.values(), key=lambda x: x['month'], reverse=True)
    
    # Get available years for filter
    all_years = WorkEntry.objects.dates('date', 'year', order='DESC')
    all_months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    context = {
        'monthly_data': monthly_list,
        'years': all_years,
        'months': all_months,
        'selected_year': year,
        'selected_month': month,
    }
    
    return render(request, 'john/monthly_compensation_report.html', context)


def export_monthly_compensation_pdf(request):
    """
    Export monthly compensation report to PDF using ReportLab.
    """
    from django.http import HttpResponse
    from django.db.models.functions import TruncMonth
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    import io
    
    # Get year and month filters
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    # Get data
    work_entries = WorkEntry.objects.all()
    mileage_entries = MileageEntry.objects.all()
    
    if year:
        work_entries = work_entries.filter(date__year=year)
        mileage_entries = mileage_entries.filter(date__year=year)
    if month:
        work_entries = work_entries.filter(date__month=month)
        mileage_entries = mileage_entries.filter(date__month=month)
    
    # Group by month
    work_by_month = work_entries.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_hours=Sum('hours'),
        total_amount=Sum('amount')
    ).order_by('-month')
    
    mileage_by_month = mileage_entries.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_miles=Sum('miles'),
        total_amount=Sum('amount')
    ).order_by('-month')
    
    # Combine data
    monthly_data = {}
    
    for entry in work_by_month:
        month_key = entry['month']
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'month': month_key,
                'hours': Decimal('0.00'),
                'hours_amount': Decimal('0.00'),
                'miles': Decimal('0.00'),
                'mileage_amount': Decimal('0.00'),
            }
        monthly_data[month_key]['hours'] = entry['total_hours'] or Decimal('0.00')
        monthly_data[month_key]['hours_amount'] = entry['total_amount'] or Decimal('0.00')
    
    for entry in mileage_by_month:
        month_key = entry['month']
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'month': month_key,
                'hours': Decimal('0.00'),
                'hours_amount': Decimal('0.00'),
                'miles': Decimal('0.00'),
                'mileage_amount': Decimal('0.00'),
            }
        monthly_data[month_key]['miles'] = entry['total_miles'] or Decimal('0.00')
        monthly_data[month_key]['mileage_amount'] = entry['total_amount'] or Decimal('0.00')
    
    # Calculate totals
    for month_key in monthly_data:
        monthly_data[month_key]['total_compensation'] = (
            monthly_data[month_key]['hours_amount'] + 
            monthly_data[month_key]['mileage_amount']
        )
    
    monthly_list = sorted(monthly_data.values(), key=lambda x: x['month'], reverse=True)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Title
    title = Paragraph("Monthly Compensation Report", title_style)
    elements.append(title)
    
    # Period info
    period_text = ""
    if year and month:
        period_text = f"Period: {calendar.month_name[int(month)]} {year}"
    elif year:
        period_text = f"Period: {year}"
    else:
        period_text = "Period: All Time"
    
    period_style = ParagraphStyle('Period', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, textColor=colors.grey)
    elements.append(Paragraph(period_text, period_style))
    elements.append(Paragraph(f"Generated: {timezone.now().strftime('%B %d, %Y %I:%M %p')}", period_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Table data
    data = [['Month', 'Total Hours', 'Hours Comp.', 'Total Miles', 'Mileage Comp.', 'Total Comp.']]
    
    grand_hours = Decimal('0.00')
    grand_hours_amount = Decimal('0.00')
    grand_miles = Decimal('0.00')
    grand_mileage_amount = Decimal('0.00')
    grand_total = Decimal('0.00')
    
    for item in monthly_list:
        data.append([
            item['month'].strftime('%B %Y'),
            f"{float(item['hours']):.2f}",
            f"${float(item['hours_amount']):.2f}",
            f"{float(item['miles']):.2f}",
            f"${float(item['mileage_amount']):.2f}",
            f"${float(item['total_compensation']):.2f}"
        ])
        grand_hours += item['hours']
        grand_hours_amount += item['hours_amount']
        grand_miles += item['miles']
        grand_mileage_amount += item['mileage_amount']
        grand_total += item['total_compensation']
    
    # Add totals row
    if monthly_list:
        data.append([
            'Grand Total',
            f"{float(grand_hours):.2f}",
            f"${float(grand_hours_amount):.2f}",
            f"{float(grand_miles):.2f}",
            f"${float(grand_mileage_amount):.2f}",
            f"${float(grand_total):.2f}"
        ])
    
    # Create table
    table = Table(data, colWidths=[1.8*inch, 0.9*inch, 1*inch, 0.9*inch, 1*inch, 1*inch])
    
    # Table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
    ])
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value from the buffer and create response
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f'compensation_report'
    if year and month:
        filename += f'_{year}_{month}'
    elif year:
        filename += f'_{year}'
    filename += '.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
