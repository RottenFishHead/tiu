from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from .fields import STAKES_CHOICES
from django.conf import settings
from django.utils import timezone   
    
class Casino(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)
    

class PokerSession(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player')
    casino = models.ForeignKey(Casino, on_delete=models.CASCADE)
    stakes = models.CharField(max_length=20, choices=STAKES_CHOICES)
    date = models.DateField()
    hours = models.IntegerField() 
    buy_in = models.IntegerField() 
    cash_out = models.IntegerField() 
    notes = models.TextField(max_length=5000, blank=True, null=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-date',)
    
    def __str__(self):
        return str(self.id)

    @property
    def win_loss(self):
        return self.cash_out - self.buy_in

    @property
    def win_rate_per_hour(self):
        if self.hours > 0:
            return self.win_loss / self.hours
        return 0
    
    def total_session_hours(self):
        total_hours = (self.clock_out - self.clock_in).seconds // 3600
        if self.break_start and self.break_end:
            break_hours = (self.break_end - self.break_start).seconds // 3600
            total_hours -= break_hours
        return total_hours

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