"""File access. This is the only module that reads or writes CSVs."""

from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
DERIVED_DIR = ROOT / "data" / "derived"
CATALOGUE_PATH = ROOT / "data" / "metric_catalogue.csv"
GLOSSARY_PATH = ROOT / "glossary" / "dynamic_events_aggregates_guide.html"
ROLE_MAPPING_PATH = ROOT / "data" / "role_mapping.csv"
PROFILES_PATH = ROOT / "data" / "profiles.csv"

# The player key has a different name in some raw files; it is always
# returned as `player_id`.
PLAYER_KEY = {
    "passes_to_off_ball_runs": "player_in_possession_id",
    "line_breaking_passes": "player_in_possession_id",
    "player_performance_metadata": "id",
}


def raw_columns(name: str) -> list[str]:
    """Column names of a raw CSV, with the player key renamed."""
    return list(load_raw(name, nrows=0).columns)


def load_raw(name: str, columns: list[str] | None = None, nrows: int | None = None) -> pd.DataFrame:
    """Load `data/raw/<name>.csv`. `columns` uses the renamed player key."""
    rename = {PLAYER_KEY.get(name, "player_id"): "player_id"}
    usecols = None if columns is None else (lambda c: rename.get(c, c) in columns)
    df = pd.read_csv(RAW_DIR / f"{name}.csv", usecols=usecols, nrows=nrows)
    return df.rename(columns=rename)


def write_derived(df: pd.DataFrame, name: str) -> Path:
    """Write a derived table to `data/derived/<name>_<timestamp>.csv`."""
    stamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    path = DERIVED_DIR / f"{name}_{stamp}.csv"
    df.to_csv(path, index=False)
    return path


def latest_derived(name: str) -> Path | None:
    """Path of the newest derived file for `name`, or None."""
    paths = sorted(DERIVED_DIR.glob(f"{name}_*.csv"))
    return paths[-1] if paths else None


def load_derived(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def read_glossary() -> str:
    """Text of the SkillCorner aggregates guide (HTML)."""
    return GLOSSARY_PATH.read_text(encoding="utf-8")


def load_catalogue_file() -> pd.DataFrame | None:
    """The stored metric catalogue, or None if it has not been built yet."""
    if not CATALOGUE_PATH.exists():
        return None
    return pd.read_csv(CATALOGUE_PATH, keep_default_na=False)


def save_catalogue_file(df: pd.DataFrame) -> None:
    df.to_csv(CATALOGUE_PATH, index=False)


def load_stored(path: Path) -> pd.DataFrame | None:
    """A stored settings table (role mapping, profiles), or None if it does not exist yet."""
    if not path.exists():
        return None
    return pd.read_csv(path, keep_default_na=False)


def save_stored(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
