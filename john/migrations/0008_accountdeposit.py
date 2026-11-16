from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("john", "0007_alter_mileageentry_amount_alter_workentry_amount"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountDeposit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, help_text="Positive amount of money deposited.", max_digits=10)),
                ("date", models.DateField(default=django.utils.timezone.localdate, help_text="Date the deposit was received.")),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("ACH", "ACH / Direct deposit"),
                            ("TRANSFER", "Account transfer"),
                            ("CHECK", "Check"),
                            ("CASH", "Cash"),
                            ("OTHER", "Other"),
                        ],
                        default="ACH",
                        help_text="How the deposit was made.",
                        max_length=10,
                    ),
                ),
                (
                    "memo",
                    models.CharField(
                        blank=True,
                        help_text="Short description (e.g. 'Paycheck', 'Transfer from savings').",
                        max_length=255,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "account",
                    models.ForeignKey(
                        help_text="Which account the money was deposited into.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deposits",
                        to="john.account",
                    ),
                ),
            ],
            options={
                "verbose_name": "Account deposit",
                "verbose_name_plural": "Account deposits",
                "ordering": ["-date", "-id"],
            },
        ),
    ]
