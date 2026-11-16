# app_name/forms.py
from django import forms
from .models import PokerSession, PlayerProfile, PlayerTendency, PlayerExploit, PokerNote, PokerNoteKeyword, StopIt
from datetime import date
from decimal import Decimal
from .fields import STAKES_CHOICES

class PokerSessionForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
    )
    class Meta:
        model = PokerSession
        fields = [
            'player',
            'casino',
            'stakes',
            'date',
            'hours',
            'buy_in',
            'cash_out',
            'timer_status',
            'timer_started_at_ms',
            'timer_elapsed_ms',
            'timer_paused_ms',
            'timer_completed_at_ms',
        ]
        widgets = {
            'timer_status': forms.HiddenInput(),
            'timer_started_at_ms': forms.HiddenInput(),
            'timer_elapsed_ms': forms.HiddenInput(),
            'timer_paused_ms': forms.HiddenInput(),
            'timer_completed_at_ms': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'date':
                field.widget.attrs['class'] = 'form-control'
            else:
                current = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (current + ' form-control').strip()

        if not self.instance.pk and not self.is_bound and not self.initial.get('date'):
            self.initial['date'] = date.today().isoformat()
        if not self.instance.pk and not self.is_bound and 'cash_out' not in self.initial:
            self.initial['cash_out'] = ''

        self.fields['hours'].help_text = 'Timer starts on first save and stops when cash out is entered; hours auto-fill from elapsed time.'
        self.fields['hours'].required = False
        self.fields['hours'].widget.attrs['min'] = 0
        self.fields['hours'].widget.attrs['step'] = '0.01'

        self.fields['buy_in'].widget.attrs['step'] = '1'
        self.fields['buy_in'].widget.attrs['min'] = '0'
        self.fields['cash_out'].widget.attrs['step'] = '1'
        self.fields['cash_out'].widget.attrs['min'] = '0'

        self.fields['cash_out'].required = False
        self.fields['timer_status'].required = False
        self.fields['timer_started_at_ms'].required = False
        self.fields['timer_elapsed_ms'].required = False
        self.fields['timer_paused_ms'].required = False
        self.fields['timer_completed_at_ms'].required = False

    def clean_hours(self):
        hours = self.cleaned_data.get('hours')
        if hours in (None, ''):
            return Decimal('0.00')
        return hours

    def clean_cash_out(self):
        raw_cash_out = ""
        if self.is_bound:
            raw_cash_out = str(self.data.get(self.add_prefix('cash_out'), "")).strip()

        cash_out = self.cleaned_data.get('cash_out')
        if cash_out in (None, ''):
            cash_out = 0

        # Treat cash-out as explicitly entered only when meaningful input was provided.
        # This avoids auto-completing timers from model/form default values like "0".
        has_nonzero_cash_out = cash_out not in (None, 0)
        changed_this_submit = 'cash_out' in getattr(self, 'changed_data', [])
        self._cash_out_has_entry = (raw_cash_out != "") and (has_nonzero_cash_out or changed_this_submit)

        return cash_out

    def save(self, commit=True):
        session = super().save(commit=False)
        session._cash_out_has_entry = getattr(self, '_cash_out_has_entry', False)
        if commit:
            session.save()
            self.save_m2m()
        return session
        
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
            base = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (base + " form-control").strip()

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


class PlayerTendencyEditForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = PlayerTendency
        fields = ["value", "sample_size", "confidence", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap()
        
class PlayerExploitEditForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = PlayerExploit
        fields = ["strength", "confidence", "note"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs["class"] = "form-control"


class PokerNoteForm(BootstrapMixin, forms.ModelForm):
    keywords = forms.CharField(
        required=False,
        help_text="Add comma-separated tags such as: bluff, river, live read",
    )

    class Meta:
        model = PokerNote
        fields = ["session", "title", "note", "is_important", "keywords"]
        widgets = {
            "note": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Type your note here. You can add suit symbols like ♥ ♦ ♠ ♣.",
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self._bootstrap()
        self.fields["is_important"].widget.attrs["class"] = "form-check-input"

        if self.user:
            self.fields["session"].queryset = PokerSession.objects.filter(player=self.user).order_by("-date", "-id")

        if self.instance.pk:
            self.fields["keywords"].initial = ", ".join(self.instance.keywords.values_list("name", flat=True))

    def clean_keywords(self):
        raw = self.cleaned_data.get("keywords", "")
        if not raw:
            return []

        parts = [part.strip().lower() for part in raw.split(",")]
        unique_parts = []
        seen = set()
        for part in parts:
            if part and part not in seen:
                seen.add(part)
                unique_parts.append(part)
        return unique_parts

    def save(self, commit=True):
        keyword_names = self.cleaned_data.get("keywords", [])
        note = super().save(commit=False)
        if self.user and not note.player_id:
            note.player = self.user

        if commit:
            note.save()
            keyword_objects = [PokerNoteKeyword.objects.get_or_create(name=name)[0] for name in keyword_names]
            note.keywords.set(keyword_objects)
            self.save_m2m()
        return note


class StopItForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = StopIt
        fields = ["stop", "state", "fails"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap()