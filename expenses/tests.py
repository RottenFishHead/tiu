from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import FixedExpenseForm
from .models import FixedExpense


class ScheduledFixedExpenseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bill-user", password="password")
        self.client.force_login(self.user)

    def test_fixed_expense_form_accepts_exact_due_date(self):
        form = FixedExpenseForm(data={
            "name": "Annual insurance",
            "frequency": "ON",
            "amount": "125.00",
            "day_to_pay": "",
            "due_date": "2026-02-20",
            "created": "2026-01-15",
        })

        self.assertTrue(form.is_valid(), form.errors)
        fixed_expense = form.save()
        self.assertEqual(fixed_expense.due_date, date(2026, 2, 20))
        self.assertIsNone(fixed_expense.day_to_pay)

    @patch("expenses.views.timezone.localdate", return_value=date(2026, 1, 15))
    def test_fixed_expense_list_hides_scheduled_expense_until_its_due_month(self, _today):
        fixed_expense = FixedExpense.objects.create(
            name="Annual insurance",
            frequency="ON",
            amount="125.00",
            due_date=date(2026, 2, 20),
        )

        response = self.client.get(reverse("expenses:fixed_expense_list"))
        self.assertNotIn(fixed_expense, response.context["fixed_expenses"])

        with patch("expenses.views.timezone.localdate", return_value=date(2026, 2, 1)):
            response = self.client.get(reverse("expenses:fixed_expense_list"))
        self.assertIn(fixed_expense, response.context["fixed_expenses"])
