from django import forms
from .models import Bill, BillPayment, WorkEntry, MileageEntry


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", "form-check-input")
            else:
                existing = widget.attrs.get("class", "")
                widget.attrs["class"] = (existing + " form-control").strip()


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = [
            "name",
            "amount",
            "due_day",
            "is_auto_pay",
            "account",
            "notes",
        ]
        widgets = {
            "due_day": forms.NumberInput(attrs={"type": "number", "min": 1, "max": 31}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class PayBillForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = BillPayment
        fields = ["date_paid", "amount", "receipt_image", "notes"]
        widgets = {
            "date_paid": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "receipt_image": "Optional: upload a photo or PDF of the paid bill.",
        }

class WorkEntryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = WorkEntry
        fields = ["date", "start_time", "end_time", "hours", "hourly_rate", "description", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "start_time": "Enter start time to auto-calculate hours.",
            "end_time": "Enter end time to auto-calculate hours.",
            "hours": "Will be calculated from start/end time, or enter manually.",
        }


class MileageEntryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MileageEntry
        fields = ["date", "starting_mileage", "ending_mileage", "miles", "rate_per_mile", "description", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "starting_mileage": "Enter starting odometer reading to auto-calculate miles.",
            "ending_mileage": "Enter ending odometer reading to auto-calculate miles.",
            "miles": "Will be calculated from start/end mileage, or enter manually.",
        }
