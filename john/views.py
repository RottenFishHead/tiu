from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
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
