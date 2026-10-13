"""Inventory of the raw CSVs: grain, keys, metric family and normalisation phase."""

import pandas as pd

from src.data.loaders import PLAYER_KEY, load_raw, raw_columns

# name: (metric family, phase used for per-30 normalisation)
# phase "tip" = minutes in possession, "otip" = minutes out of possession,
# "suffix" = taken from the column suffix (_tip / _otip / _all).
METRIC_FILES = {
    "physical": ("Physical", "suffix"),
    "off_ball_runs": ("Off-ball runs", "tip"),
    "line_breaking_options": ("Passing options", "tip"),
    "passes_to_off_ball_runs": ("Passing", "tip"),
    "line_breaking_passes": ("Passing", "tip"),
    "possessions": ("Possessions", "tip"),
    "on_ball_engagements": ("Pressure", "otip"),
    "pressing_engagements": ("Pressure", "otip"),
    "pressure_engagements": ("Pressure", "otip"),
    "counter_press_engagements": ("Pressure", "otip"),
    "recovery_press_engagements": ("Pressure", "otip"),
}

OTHER_FILES = {
    "competition_editions": ("Reference", "competition edition", "-"),
    "competition_power_rankings": ("Reference", "competition", "-"),
    "player_performance_metadata": ("Line-ups and minutes", "player x match", "-"),
}


def inventory() -> pd.DataFrame:
    rows = []
    for name, (family, grain, phase) in OTHER_FILES.items():
        rows.append(_row(name, family, grain, phase))
    for name, (family, phase) in METRIC_FILES.items():
        rows.append(_row(name, family, "player x match", phase.upper() if phase != "suffix" else "by column suffix"))
    return pd.DataFrame(rows)


def _row(name: str, family: str, grain: str, phase: str) -> dict:
    columns = raw_columns(name)
    has_matches = "match_id" in columns
    ids = load_raw(name, columns=["match_id"]) if has_matches else load_raw(name)
    return {
        "file": name,
        "metric family": family,
        "grain": grain,
        "player key (raw name)": PLAYER_KEY.get(name, "player_id") if has_matches else "-",
        "per-30 minutes": phase,
        "rows": len(ids),
        "columns": len(columns),
        "matches": ids["match_id"].nunique() if has_matches else None,
    }
