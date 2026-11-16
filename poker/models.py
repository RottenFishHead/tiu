from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from .fields import STAKES_CHOICES
from django.conf import settings
from django.utils import timezone   
from decimal import Decimal
    
class Casino(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)
    

class PokerSession(models.Model):
    TIMER_IDLE = "idle"
    TIMER_RUNNING = "running"
    TIMER_PAUSED = "paused"
    TIMER_COMPLETED = "completed"

    TIMER_STATUS_CHOICES = [
        (TIMER_IDLE, "Idle"),
        (TIMER_RUNNING, "Running"),
        (TIMER_PAUSED, "Paused"),
        (TIMER_COMPLETED, "Completed"),
    ]

    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player')
    casino = models.ForeignKey(Casino, on_delete=models.CASCADE)
    stakes = models.CharField(max_length=20, choices=STAKES_CHOICES)
    date = models.DateField()
    hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"), blank=True)
    buy_in = models.IntegerField() 
    cash_out = models.IntegerField(default=0, blank=True) 
    timer_status = models.CharField(max_length=20, choices=TIMER_STATUS_CHOICES, default=TIMER_COMPLETED)
    timer_started_at_ms = models.BigIntegerField(null=True, blank=True)
    timer_elapsed_ms = models.BigIntegerField(default=0)
    timer_paused_ms = models.BigIntegerField(default=0)
    timer_completed_at_ms = models.BigIntegerField(null=True, blank=True)
    notes = models.TextField(max_length=5000, blank=True, null=True)
    selected_stop = models.ForeignKey("StopIt", on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")
    created = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-date',)
    
    def __str__(self):
        return str(self.id)

    @staticmethod
    def _now_ms():
        return int(timezone.now().timestamp() * 1000)

    def save(self, *args, **kwargs):
        is_create = self.pk is None

        if is_create and not self.timer_started_at_ms:
            self.timer_started_at_ms = self._now_ms()
            self.timer_status = self.TIMER_RUNNING

        cash_out_has_entry = getattr(self, "_cash_out_has_entry", None)
        if cash_out_has_entry is None:
            cash_out_has_entry = self.cash_out not in (None, 0)

        should_complete = (
            not is_create
            and
            bool(self.timer_started_at_ms)
            and bool(cash_out_has_entry)
            and self.timer_status != self.TIMER_COMPLETED
        )

        if should_complete:
            if not self.timer_completed_at_ms:
                self.timer_completed_at_ms = self._now_ms()

            started_ms = int(self.timer_started_at_ms or 0)
            completed_ms = int(self.timer_completed_at_ms or started_ms)
            paused_ms = int(self.timer_paused_ms or 0)
            derived_elapsed_ms = max(0, completed_ms - started_ms - paused_ms)
            stored_elapsed_ms = int(self.timer_elapsed_ms or 0)
            elapsed_ms = max(derived_elapsed_ms, stored_elapsed_ms)

            self.timer_elapsed_ms = elapsed_ms
            self.timer_status = self.TIMER_COMPLETED
            self.hours = (Decimal(elapsed_ms) / Decimal("3600000")).quantize(Decimal("0.01"))

        super().save(*args, **kwargs)

    @property
    def win_loss(self):
        return self.cash_out - self.buy_in

    @property
    def win_rate_per_hour(self):
        if self.hours > 0:
            return self.win_loss / self.hours
        return 0

class PlayerTag(models.Model):
    """
    Flexible labels like: NIT, LAG, Station, Maniac, Reg, OMC, etc.
    """
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=20, blank=True, help_text="Optional UI hint (e.g. 'red', '#ff0000').")

    def __str__(self):
        return self.name


class PlayerProfile(models.Model):
    # Identity / matching
    display_name = models.CharField(max_length=120, help_text="What you call them (e.g., 'Hat Guy', 'Mike').")
    casino = models.ForeignKey(Casino, on_delete=models.SET_NULL, null=True, blank=True)
    approximate_age = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, help_text="Physical / behavior identifiers (non-sensitive).")
    image = models.ImageField(upload_to='player_images/', null=True, blank=True)
    # Quick summary for list views
    summary = models.CharField(max_length=240, blank=True, help_text="One-line take (e.g., 'Loose passive station; never bluffs river').")
    tags = models.ManyToManyField(PlayerTag, blank=True, related_name="players")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["display_name"])
        ]
        

    def __str__(self):
        return f"{self.display_name}"


class Street(models.TextChoices):
    PREFLOP = "pre", "Preflop"
    FLOP = "flop", "Flop"
    TURN = "turn", "Turn"
    RIVER = "river", "River"


class TendencyMetric(models.TextChoices):
    # --- Preflop core ---
    VPIP = "vpip", "VPIP (plays lots of hands)"
    PFR = "pfr", "PFR (raises preflop)"
    THREE_BET = "3bet", "3-bet frequency"
    FOLD_TO_3BET = "fold_to_3bet", "Folds to 3-bet"
    CALLS_3BET = "calls_3bet", "Calls 3-bets"

    # --- Flop core ---
    CBET_FLOP = "cbet_flop", "C-bet flop"
    FOLD_TO_CBET_FLOP = "fold_to_cbet_flop", "Folds to flop c-bet"
    XR_FLOP = "xr_flop", "Check-raise flop"

    # --- Turn core ---
    BARREL_TURN = "barrel_turn", "Barrels turn"
    FOLD_TO_TURN_BET = "fold_to_turn_bet", "Folds to turn bet"

    # --- River core ---
    VALUE_HEAVY_RIVER = "value_heavy_river", "River raises = value-heavy"
    BLUFFY_RIVER = "bluffy_river", "Bluffy on river"

class PlayerTendency(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="tendencies")
    metric = models.CharField(max_length=40, choices=TendencyMetric.choices)
    street = models.CharField(max_length=10, choices=Street.choices, blank=True)

    # Store as a percent (0-100) or score (0-10) depending on metric;
    # you can standardize later.
    value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # How sure are you? sample_size gives weight.
    sample_size = models.PositiveIntegerField(default=0)
    confidence = models.PositiveSmallIntegerField(default=1, help_text="1-5 subjective confidence.")

    note = models.CharField(max_length=240, blank=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["player", "metric"]),
        ]   
        constraints = [
            models.UniqueConstraint(fields=["player", "metric", "street"], name="uniq_player_metric_street")
        ]

    def __str__(self):
        return f"{self.player} {self.metric} {self.street or ''}".strip()

class PlayerObservation(models.Model):
    """
    Atomic observation: "he 3-bet light from BB vs BTN", "slowplays sets", etc.
    These are gold because they age well even if your numeric estimates change.
    """
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="observations")
    session = models.ForeignKey(PokerSession, on_delete=models.SET_NULL, null=True, blank=True)
    street = models.CharField(max_length=10, choices=Street.choices, blank=True)
    situation = models.CharField(max_length=120, blank=True, help_text="e.g., 'BTN vs BB SRP', '3bet pot OOP'")
    action = models.CharField(max_length=200, help_text="What happened (short, structured).")
    takeaway = models.CharField(max_length=240, blank=True, help_text="Your exploit / adjustment.")

    # Optional simple “strength” / reliability marker
    reliability = models.PositiveSmallIntegerField(default=3, help_text="1-5 how trustworthy this read is.")
    happened_at = models.DateTimeField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["player", "-created"])
        ]

    def __str__(self):
        return f"{self.player}: {self.action[:60]}"
    
class ExploitTag(models.Model):
    """
    Button-driven exploit statements (the real money).
    """
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class PlayerExploit(models.Model):
    player = models.ForeignKey("PlayerProfile", on_delete=models.CASCADE, related_name="exploits")
    tag = models.ForeignKey(ExploitTag, on_delete=models.CASCADE, related_name="player_links")

    # Button presses reinforce it
    strength = models.PositiveSmallIntegerField(default=1)   # 1–10
    confidence = models.PositiveSmallIntegerField(default=3) # 1–5
    note = models.CharField(max_length=240, blank=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["player", "tag"], name="uniq_player_exploit_tag")
        ]

    def __str__(self):
        return f"{self.player} - {self.tag}"


class PokerNoteKeyword(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PokerNote(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="poker_notes")
    session = models.ForeignKey(PokerSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="poker_notes")
    title = models.CharField(max_length=140, blank=True)
    note = models.TextField(max_length=5000)
    is_important = models.BooleanField(default=False)
    keywords = models.ManyToManyField(PokerNoteKeyword, blank=True, related_name="notes")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_important", "-updated"]
        indexes = [
            models.Index(fields=["player", "-updated"], name="poker_poker_player__d8cb53_idx"),
            models.Index(fields=["player", "is_important"], name="poker_poker_player__84b2af_idx"),
        ]

    def __str__(self):
        return self.title or f"Note #{self.pk}"
    
class StopIt(models.Model):
    stop = models.CharField(max_length=250, unique=True)
    state = models.CharField(max_length=20, default="leak", choices=[("leak", "Leak"), ("working", "Working"), ("mastered", "Mastered")])
    fails = models.IntegerField(default=0, choices=[(i, i) for i in range(51)])
    text = models.TextField(blank=True, help_text="Optional notes about this stop-it.")
    
    class Meta:
        ordering = ["stop"]

    def __str__(self):
        return self.stop