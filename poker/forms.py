# app_name/forms.py
from django import forms
from .models import PokerSession
from datetime import date
from .fields import STAKES_CHOICES

class PokerSessionForm(forms.ModelForm):
    date = forms.DateField(widget = forms.SelectDateWidget(),initial=date.today)
    class Meta:
        model = PokerSession
        fields = ['player', 'casino', 'stakes', 'date', 'hours', 'buy_in', 'cash_out']
        
class DateForm(forms.Form):
    start = forms.DateField(help_text="Must always include a date range",
        widget=forms.DateInput(attrs={'type': 'date', 'style':'width:150px;'}))
    end = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'style':'width:150px;'}))
    stakes = forms.TypedChoiceField(choices=STAKES_CHOICES)



from django import forms
from .models import (
    PlayerProfile,
    PlayerObservation,
    PlayerTendency,
    PlayerTag,
)


class BootstrapMixin:
    def _bootstrap(self):
        for name, field in self.fields.items():
            widget = field.widget
            base = widget.attrs.get("class", "")

            if isinstance(widget, forms.FileInput):
                widget.attrs["class"] = (base + " form-control").strip()
            elif isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs["class"] = (base + " form-check-input").strip()
            elif isinstance(widget, (forms.SelectMultiple,)):
                widget.attrs["class"] = (base + " form-select").strip()
            elif isinstance(widget, (forms.Select,)):
                widget.attrs["class"] = (base + " form-select").strip()
            else:
                widget.attrs["class"] = (base + " form-control").strip()

            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("rows", 3)


class PlayerProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = PlayerProfile
        fields = [
            "display_name",
            "image", 
            "approximate_age",
            "description",
            "summary",
            "tags",
       
        ]
        widgets = {
            "description": forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].queryset = PlayerTag.objects.order_by("name")
        self._bootstrap()


class PlayerObservationForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = PlayerObservation
        fields = [
            "street",
            "situation",
            "action",
            "takeaway",
            "reliability",
            "happened_at",
        ]
        widgets = {
            "happened_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap()



class PlayerTendencyForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = PlayerTendency
        fields = [
            "metric",
            "street",
            "value",
            "sample_size",
            "confidence",
            "note",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap()
