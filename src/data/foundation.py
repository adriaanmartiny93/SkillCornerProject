"""Base tables and normalisation rules that every later step builds on."""

import numpy as np
import pandas as pd

from src.data.catalogue import BEST_X, PER, metric_specs
from src.data.loaders import load_raw, write_derived
from src.data.roles import position_to_role

# A match counts for season aggregates if the player has at least this many
# minutes in it; a player-role row with fewer included matches is low sample.
DEFAULT_MIN_MATCH_MINUTES = 60
DEFAULT_MIN_MATCHES = 5

# One row of the player-season table.
SEASON_KEYS = [
    "competition_edition_id",
    "competition_name",
    "team_id",
    "team_name",
    "player_id",
    "player_name",
    "role",
]

MINUTES = {"all": "minutes_full_all", "tip": "minutes_full_tip", "otip": "minutes_full_otip"}

_BASE_COLUMNS = [
    "match_id",
    "match_date",
    "player_birthdate",
    "position",
    "physical_check_passed",
    *[c for c in SEASON_KEYS if c != "role"],
    *MINUTES.values(),
]


def player_matches() -> pd.DataFrame:
    """One row per player and match: team, competition, position, role, minutes."""
    df = load_raw("physical", columns=_BASE_COLUMNS)
    df["role"] = df["position"].map(position_to_role())
    return df


def player_seasons(
    matches: pd.DataFrame,
    min_match_minutes: float = DEFAULT_MIN_MATCH_MINUTES,
    min_matches: int = DEFAULT_MIN_MATCHES,
) -> pd.DataFrame:
    """One row per player x team x competition x role, with a low-sample flag."""
    included = matches[MINUTES["all"]] >= min_match_minutes
    matches = matches.assign(_included=included, _minutes=matches[MINUTES["all"]].where(included, 0))
    df = (
        matches.groupby(SEASON_KEYS, as_index=False)
        .agg(
            player_birthdate=("player_birthdate", "first"),
            matches=("match_id", "nunique"),
            matches_included=("_included", "sum"),
            minutes=(MINUTES["all"], "sum"),
            minutes_included=("_minutes", "sum"),
            minutes_tip=(MINUTES["tip"], "sum"),
            minutes_otip=(MINUTES["otip"], "sum"),
        )
        .round({"minutes": 2, "minutes_included": 2, "minutes_tip": 2, "minutes_otip": 2})
    )
    df["min_match_minutes"] = min_match_minutes
    df["min_matches"] = min_matches
    df["low_sample"] = df["matches_included"] < min_matches
    return df


def run_player_pipeline(
    min_match_minutes: float = DEFAULT_MIN_MATCH_MINUTES, min_matches: int = DEFAULT_MIN_MATCHES
):
    """Recalculate the player-season table and write it to data/derived/."""
    seasons = player_seasons(player_matches(), min_match_minutes, min_matches)
    return write_derived(seasons, "player_seasons")


def rate_column(name: str, metric: str) -> str:
    """Name of the rate column: `<metric>_p30`, `_p90`, or `_season` if not per minute."""
    per = metric_specs(name).at[metric, "per"]
    return f"{metric}_p{PER[per][1]}" if per in PER else f"{metric}_season"


def match_values(name: str, metrics: list[str], matches: pd.DataFrame) -> pd.DataFrame:
    """Player-match base rows with the chosen metrics of one raw file.

    Metrics with calculation "total" also get their rate for that match
    (`<metric>_p90` or `_p30`): match value divided by match minutes. A
    calculated metric is the raw column named in its `source`, under its own name.

    Only matches covered by the file are kept. A player without a row in a
    covered match gets 0 for totals and weights. For physical metrics, rows
    that failed the physical check are left out.
    """
    specs = metric_specs(name).loc[metrics]
    sources = specs["source"].unique()
    weights = [w for w in specs["weight"].unique() if w and w not in matches and w not in sources]
    values = load_raw(name, columns=["match_id", "player_id", *sources, *weights])
    if name == "physical":
        base = matches[matches["physical_check_passed"]]
    else:
        base = matches[matches["match_id"].isin(values["match_id"].unique())]
    df = base.merge(values, on=["match_id", "player_id"], how="left")
    for metric, source in specs["source"].items():
        if metric != source:
            df[metric] = df[source]
    summed = specs.index[specs["calculation"].isin(["total", "ratio"])]
    zero = [*summed, *weights]
    df[zero] = df[zero].fillna(0)
    for metric in specs.index[specs["calculation"] == "total"]:
        phase, number = PER[specs.at[metric, "per"]]
        minutes = df[MINUTES[phase]]
        df[rate_column(name, metric)] = df[metric] / minutes.where(minutes > 0) * number
    return df


def season_rates(
    values: pd.DataFrame,
    name: str,
    metrics: list[str],
    min_match_minutes: float = DEFAULT_MIN_MATCH_MINUTES,
) -> pd.DataFrame:
    """Season values per player x team x competition x role.

    `values` is the output of `match_values`. How each metric is calculated
    comes from the metric catalogue. Metrics with `match_filter` only use
    matches with at least `min_match_minutes` minutes; a total is the plain
    mean of the match rates of those matches. An average of best x also gets
    `<metric>_matches`: the number of matches it is built from (x, or fewer if
    the player has fewer).
    """
    specs = metric_specs(name)
    keys = [values[key] for key in SEASON_KEYS]
    included = values[MINUTES["all"]] >= min_match_minutes
    out = included.groupby(keys).sum().to_frame("matches_included")
    for metric in metrics:
        calculation, weight, match_filter, inverse, best_x = specs.loc[
            metric, ["calculation", "weight", "match_filter", "inverse", "best_x"]
        ]
        used = included if match_filter else pd.Series(True, index=values.index)
        column = values[metric].where(used)
        if calculation == "total":
            season = values[rate_column(name, metric)].where(used).groupby(keys).mean()
        elif calculation == "ratio":
            total = values[weight].where(used).groupby(keys).sum()
            season = column.groupby(keys).sum() / total.where(total > 0)
        elif calculation == "average" and weight:
            total = values[weight].where(column.notna()).groupby(keys).sum()
            season = (column * values[weight]).groupby(keys).sum() / total.where(total > 0)
        elif calculation == "average":
            season = column.groupby(keys).mean()
        elif calculation == BEST_X:
            # Best = highest, or lowest for lower-is-better metrics.
            rank = column.groupby(keys).rank(method="first", ascending=bool(inverse))
            best = column.where(rank <= best_x)
            season = best.groupby(keys).mean()
            out[f"{metric}_matches"] = best.groupby(keys).count()
        else:
            season = column.groupby(keys).agg(calculation)
        out[rate_column(name, metric)] = season
    return out.reset_index()


def standardise(
    df: pd.DataFrame,
    columns: list[str],
    by: tuple[str, ...] = ("competition_edition_id", "role"),
) -> pd.DataFrame:
    """Add `<column>_z` and `<column>_pct` within each group of `by`.

    Rows flagged `low_sample` are left out of the reference (mean, spread and
    ranking) but still get a score.
    """
    df = df.copy()
    for column in columns:
        df[f"{column}_z"] = np.nan
        df[f"{column}_pct"] = np.nan
    for _, group in df.groupby(list(by)):
        reference = group[~group["low_sample"]] if "low_sample" in group else group
        for column in columns:
            ref = np.sort(reference[column].dropna().to_numpy())
            if len(ref) < 2:
                continue
            values = group[column]
            std = ref.std(ddof=0)
            if std > 0:
                df.loc[group.index, f"{column}_z"] = (values - ref.mean()) / std
            pct = np.searchsorted(ref, values.to_numpy(), side="right") / len(ref) * 100
            df.loc[group.index, f"{column}_pct"] = np.where(values.isna(), np.nan, pct)
    return df
