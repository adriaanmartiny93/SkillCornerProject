"""Profiles: a name, a role, and a list of metrics each with a weight.

Stored in `data/profiles.csv`, one row per profile and metric.
"""

import pandas as pd

from src.data.loaders import PROFILES_PATH, load_stored, save_stored

COLUMNS = ["profile", "role", "file", "metric", "weight"]
STRONG_CORRELATION = 0.6


def load_profiles() -> pd.DataFrame:
    stored = load_stored(PROFILES_PATH)
    return pd.DataFrame(columns=COLUMNS) if stored is None else stored


def save_profile(name: str, role: str, metrics: pd.DataFrame) -> None:
    """Store a profile; `metrics` has the columns file, metric, weight. An existing profile with this name is replaced."""
    profiles = load_profiles()
    rows = metrics.assign(profile=name, role=role)[COLUMNS]
    save_stored(pd.concat([profiles[profiles["profile"] != name], rows], ignore_index=True), PROFILES_PATH)


def delete_profile(name: str) -> None:
    profiles = load_profiles()
    save_stored(profiles[profiles["profile"] != name], PROFILES_PATH)


def strong_pairs(correlations: pd.DataFrame, threshold: float = STRONG_CORRELATION) -> list[tuple[str, str, float]]:
    """Pairs of metrics with an absolute correlation of `threshold` or more."""
    names = list(correlations.columns)
    return [
        (a, b, correlations.at[a, b])
        for i, a in enumerate(names)
        for b in names[i + 1 :]
        if abs(correlations.at[a, b]) >= threshold
    ]
