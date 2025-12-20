from django.db import models
from django.utils import timezone
from decimal import Decimal



class Account(models.Model):
    """
    Which account a bill is paid from (checking, credit card, etc.).
    """
    name = models.CharField(max_length=100)
    institution = models.CharField(max_length=100, blank=True)
    number_last4 = models.CharField(
        max_length=4,
        blank=True,
        help_text="Last 4 digits, optional, for reference only.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.institution})" if self.institution else self.name


class Bill(models.Model):
    """
    A recurring monthly bill.
    - due_day = day of the month it's due (1–31)
    - Whether it's 'paid this month' is tracked via BillPayment records.
    """
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    due_day = models.PositiveSmallIntegerField(
        default=1,
        help_text="Day of the month this bill is due (1–31).",
    )
    is_auto_pay = models.BooleanField(
        default=False,
        help_text="Checked if this bill is paid automatically each month.",
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="bills",
    )

    notes = models.TextField(blank=True)

    active = models.BooleanField(
        default=True,
        help_text="Uncheck if this bill is no longer active.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["active", "due_day", "name"]

    def __str__(self):
        return f"{self.name} (day {self.due_day})"


class AccountWithdrawal(models.Model):
    """
    Any money leaving an account (bill payment, cash withdrawal, transfer out, etc.).
    Can optionally be linked to a specific Bill.
    """
    METHOD_ACH = "ACH"
    METHOD_CARD = "CARD"
    METHOD_CHECK = "CHECK"
    METHOD_CASH = "CASH"
    METHOD_OTHER = "OTHER"

    METHOD_CHOICES = [
        (METHOD_ACH, "ACH / Bank transfer"),
        (METHOD_CARD, "Debit / Credit card"),
        (METHOD_CHECK, "Check"),
        (METHOD_CASH, "Cash"),
        (METHOD_OTHER, "Other"),
    ]

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="withdrawals",
        help_text="Which account the money came out of.",
    )
    bill = models.ForeignKey(
        Bill,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="withdrawals",
        help_text="Optional: link to the bill this withdrawal paid.",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Positive amount of money withdrawn.",
    )
    date = models.DateField(
        default=timezone.localdate,
        help_text="Date the money actually left the account.",
    )
    method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        default=METHOD_ACH,
        help_text="How the withdrawal was made.",
    )
    memo = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short description (e.g. 'Electric bill', 'ATM withdrawal').",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Account withdrawal"
        verbose_name_plural = "Account withdrawals"

    def __str__(self):
        return f"{self.account} - {self.date} - ${self.amount}"


class BillPayment(models.Model):
    """
    A single month's payment of a recurring bill.
    This is how we know if a bill is 'paid this month' and keep history.
    """
    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="bill_payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField(default=timezone.localdate)
    receipt_image = models.ImageField(
        upload_to="bills/receipts/",
        null=True,
        blank=True,
        help_text="Upload an image/PDF of the paid bill or receipt.",
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_paid", "-id"]
        verbose_name = "Bill payment"
        verbose_name_plural = "Bill payments"

    def __str__(self):
        return f"{self.bill} paid {self.date_paid} - ${self.amount}"


class WorkEntry(models.Model):
    """
    Track hours worked for reimbursement.
    Default rate is $30/hour.
    """
    date = models.DateField(default=timezone.localdate)
    description = models.CharField(max_length=255, blank=True)
    start_time = models.TimeField(null=True, blank=True, help_text="Start time of work.")
    end_time = models.TimeField(null=True, blank=True, help_text="End time of work.")
    hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total hours worked (calculated or manual).",
    )
    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("30.00"),
        help_text="Reimbursement rate per hour.",
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        help_text="Computed reimbursement amount (hours × rate).",
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Work entry"
        verbose_name_plural = "Work entries"

    def save(self, *args, **kwargs):
        # Calculate hours from start/end time if both are provided
        if self.start_time and self.end_time:
            from datetime import datetime, timedelta
            start = datetime.combine(self.date, self.start_time)
            end = datetime.combine(self.date, self.end_time)
            # Handle overnight shifts
            if end < start:
                end += timedelta(days=1)
            delta = end - start
            self.hours = Decimal(str(delta.total_seconds() / 3600)).quantize(Decimal("0.01"))
        
        if self.hours is not None and self.hourly_rate is not None:
            self.amount = (self.hours * self.hourly_rate).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} – {self.hours}h @ ${self.hourly_rate}/h"


class MileageEntry(models.Model):
    """
    Track mileage for reimbursement.
    You can adjust the default rate per mile if needed.
    """
    date = models.DateField(default=timezone.localdate)
    description = models.CharField(max_length=255, blank=True)
    starting_mileage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Starting odometer reading.",
    )
    ending_mileage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ending odometer reading.",
    )
    miles = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total miles driven (calculated or manual).",
    )
    rate_per_mile = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=Decimal("0.210"),
        help_text="Reimbursement rate per mile.",
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        help_text="Computed reimbursement amount (miles × rate).",
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Mileage entry"
        verbose_name_plural = "Mileage entries"

    def save(self, *args, **kwargs):
        # Calculate miles from starting/ending mileage if both are provided
        if self.starting_mileage is not None and self.ending_mileage is not None:
            self.miles = (self.ending_mileage - self.starting_mileage).quantize(Decimal("0.01"))
        
        if self.miles is not None and self.rate_per_mile is not None:
            self.amount = (self.miles * self.rate_per_mile).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} – {self.miles} miles @ ${self.rate_per_mile}/mile"
