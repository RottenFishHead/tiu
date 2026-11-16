from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .forms import BillForm
from .models import Account, Bill


class ScheduledBillTests(TestCase):
    def setUp(self):
        self.account = Account.objects.create(name="Checking")

    def test_bill_form_accepts_exact_due_date_without_monthly_day(self):
        form = BillForm(data={
            "name": "Annual insurance",
            "amount": "125.00",
            "due_day": "",
            "scheduled_date": "2026-02-20",
            "account": self.account.pk,
            "notes": "",
        })

        self.assertTrue(form.is_valid(), form.errors)
        bill = form.save()
        self.assertEqual(bill.scheduled_date, date(2026, 2, 20))
        self.assertIsNone(bill.due_day)

    @patch("john.views.timezone.localdate", return_value=date(2026, 1, 15))
    def test_bill_list_hides_scheduled_bill_until_its_due_month(self, _today):
        bill = Bill.objects.create(
            name="Annual insurance",
            amount="125.00",
            scheduled_date=date(2026, 2, 20),
            account=self.account,
        )

        response = self.client.get(reverse("john:bill_list"))
        self.assertNotIn(bill, response.context["bills"])

        with patch("john.views.timezone.localdate", return_value=date(2026, 2, 1)):
            response = self.client.get(reverse("john:bill_list"))
        bills = response.context["bills"]
        self.assertEqual([listed_bill.pk for listed_bill in bills], [bill.pk])
        self.assertEqual(bills[0].due_date, date(2026, 2, 20))

    @patch("john.views.timezone.localdate", return_value=date(2026, 1, 15))
    def test_dashboard_shows_scheduled_bill_in_its_due_month(self, _today):
        bill = Bill.objects.create(
            name="Annual insurance",
            amount="125.00",
            scheduled_date=date(2026, 2, 20),
            account=self.account,
        )

        response = self.client.get(reverse("john:dashboard"))
        self.assertNotIn(bill.pk, [item.pk for item in response.context["due_soon_bills"]])

        with patch("john.views.timezone.localdate", return_value=date(2026, 2, 20)):
            response = self.client.get(reverse("john:dashboard"))
        self.assertIn(bill.pk, [item.pk for item in response.context["due_soon_bills"]])
