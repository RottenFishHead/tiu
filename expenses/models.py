from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db.models import Sum


FREQUENCY_CHOICES = (
    ('WK', 'Weekly'), #Confirmation on Creation is DONE
    ('PT', 'Monthly'), #DONE
    ('ON', 'Once')
)
class PAYMENT_CHOICES(models.TextChoices):
    AUTOMATIC = 'AU', 'Automatic' 
    MANUAL = 'MN', 'Manual'
    
class Category(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
class Account(models.Model):
    name = models.CharField(max_length=50,  blank=False, null=False)
    
    def __str__(self):
        return self.name

    
class FixedExpense(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE,  blank=True, null=True)
    name = models.CharField(max_length=50,  blank=False, null=False)
    frequency = models.CharField(max_length=3, choices=FREQUENCY_CHOICES)
    autopay = models.BooleanField(default=True, verbose_name='Autopay')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    day_to_pay = models.IntegerField(blank=False, null=False)
    created = models.DateField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    @property
    def fixed_amount_paid(self):
        return sum(payment.amount_paid for payment in self.payments.all())

    @property
    def is_paid(self):
        return "Yes" if now().day > self.day_to_pay else "No"
    
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,verbose_name='Purchaser')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,  blank=False, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE,  blank=True, null=True)
    name = models.CharField(max_length=50,  blank=False, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.name
    
class Budget(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE,  blank=False, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    
def __str__(self):
        return f"{self.date} - {self.amount}"


class Debt(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owed = models.DecimalField(max_digits=10, decimal_places=2)
    due_by = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.owed}"

    @property
    def total_amount_paid(self):
        return sum(payment.amount_paid for payment in self.payments.all())
    
class Savings(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    goal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.goal}"
    
    @property
    def total_amount_saved(self):
        return sum(payment.amount_paid for payment in self.payments.all())

class Payment(models.Model):
    debt = models.ForeignKey(Debt, related_name='payments', on_delete=models.CASCADE, blank=True, null=True)
    savings = models.ForeignKey(Savings, related_name='payments', on_delete=models.CASCADE, blank=True, null=True)
    fixed_expense = models.ForeignKey(FixedExpense, related_name='payments', on_delete=models.CASCADE, blank=True, null=True)
    savings = models.ForeignKey(Savings, related_name='payments', on_delete=models.CASCADE, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.debt:
            return f"Payment of {self.amount_paid} on Debt - {self.debt}"
        elif self.savings:
            return f"Payment of {self.amount_paid} on Savings - {self.savings}"
        elif self.fixed_expense:
            return f"Payment of {self.amount_paid} on Fixed Expense - {self.fixed_expense}"

    