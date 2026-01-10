from .models import Street, TendencyMetric

# Tendencies = stat-like, tracked by (metric + street)
TENDENCY_PRESETS = [
    # --- Preflop ---
    {"metric": TendencyMetric.VPIP,            "street": Street.PREFLOP, "label": "VPIP High"},
    {"metric": TendencyMetric.PFR,             "street": Street.PREFLOP, "label": "PFR High"},
    {"metric": TendencyMetric.THREE_BET,       "street": Street.PREFLOP, "label": "3-Bets Light"},
    {"metric": TendencyMetric.FOLD_TO_3BET,    "street": Street.PREFLOP, "label": "Folds to 3-Bet"},
    {"metric": TendencyMetric.CALLS_3BET,      "street": Street.PREFLOP, "label": "Calls 3-Bets"},

    # --- Flop ---
    {"metric": TendencyMetric.CBET_FLOP,           "street": Street.FLOP, "label": "C-Bets Flop"},
    {"metric": TendencyMetric.FOLD_TO_CBET_FLOP,   "street": Street.FLOP, "label": "Folds to Flop C-Bet"},
    {"metric": TendencyMetric.XR_FLOP,             "street": Street.FLOP, "label": "Check-Raises Flop"},

    # --- Turn ---
    {"metric": TendencyMetric.BARREL_TURN,       "street": Street.TURN, "label": "Barrels Turn"},
    {"metric": TendencyMetric.FOLD_TO_TURN_BET,  "street": Street.TURN, "label": "Folds to Turn Bet"},

    # --- River ---
    {"metric": TendencyMetric.VALUE_HEAVY_RIVER, "street": Street.RIVER, "label": "Value-Heavy River Raises"},
    {"metric": TendencyMetric.BLUFFY_RIVER,      "street": Street.RIVER, "label": "Bluffy River"},
]
# Exploit tags = pure “how do I print money vs this player”
EXPLOIT_PRESETS = [
    {"name": "Overfolds to flop c-bet", "desc": "C-bet wide; small sizing prints"},
    {"name": "Overcalls flop, folds turn", "desc": "Double barrel turn"},
    {"name": "Calls too wide pre", "desc": "Iso bigger; value thinner"},
    {"name": "Never bluffs river", "desc": "Fold to river aggression"},
    {"name": "Value-only river raise", "desc": "Big folds vs raises"},
    {"name": "Hates folding pairs", "desc": "Value bet thin; fewer bluffs"},
]