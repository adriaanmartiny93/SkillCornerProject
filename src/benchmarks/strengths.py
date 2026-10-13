"""Strongest metrics of a player: z-scores against a stored mean and spread per competition, role and metric."""

import pandas as pd

from src.benchmarks.usefulness import events_per_match
from src.data.catalogue import load_catalogue
from src.data.foundation import SEASON_KEYS, match_values, rate_column, season_rates
from src.data.loaders import write_derived

# A z-score is within these groups.
BY = ["competition_edition_id", "role"]


def _catalogue() -> pd.DataFrame:
    """The full-match metrics; first-half and second-half metrics are left out."""
    catalogue = load_catalogue()
    return catalogue[catalogue["scope"] == "full"]


def _season_values(catalogue: pd.DataFrame, matches: pd.DataFrame, min_match_minutes: float):
    """Per file: its name and the season values, one row per player-season row and one column per metric."""
    for file, rows in catalogue.groupby("file", sort=False):
        names = rows["metric"].tolist()
        specs = rows.set_index("metric")
        rates = season_rates(match_values(file, names, matches), file, names, min_match_minutes)
        columns = [rate_column(file, name, specs) for name in names]
        yield file, rates.set_index(SEASON_KEYS)[columns].set_axis(names, axis=1).rename_axis(columns="metric")


def metric_reference(seasons: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Mean and spread of every full-match metric, per competition and role.

    One row per competition, role, file and metric, with `mean`, `std` and
    `players`: the number of reference players behind them. Reference players
    are the rows of `seasons` that are not low sample. `events_per_match` is
    the output of `usefulness.events_per_match` for the role (empty for
    physical metrics). The mean of a lower-is-better metric is not flipped.
    """
    min_match_minutes = seasons["min_match_minutes"].iloc[0]
    reference = pd.MultiIndex.from_frame(seasons.loc[~seasons["low_sample"], SEASON_KEYS])
    out = []
    for file, values in _season_values(_catalogue(), matches, min_match_minutes):
        groups = values[values.index.isin(reference)].groupby(level=BY)
        stats = {"mean": groups.mean().stack(), "std": groups.std(ddof=0).stack(), "players": groups.count().stack()}
        out.append(pd.DataFrame(stats).reset_index().assign(file=file))
    df = pd.concat(out, ignore_index=True)
    df = df.merge(events_per_match(seasons, matches), on=["file", "metric", "role"], how="left")
    return df[[*BY, "file", "metric", "mean", "std", "players", "events_per_match"]]


def run_metric_reference(seasons: pd.DataFrame, matches: pd.DataFrame):
    """Calculate the metric reference and write it to data/derived/."""
    return write_derived(metric_reference(seasons, matches), "metric_reference")


def player_strengths(player: pd.DataFrame, matches: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    """Season value and z-score of every full-match metric for a few rows of the player-season table.

    `player` holds the rows to calculate (one per role), `reference` is the
    output of `metric_reference`. One row per role, file and metric. For
    lower-is-better metrics the z-score is flipped, so higher is always
    better. There is no z-score with fewer than two reference players or
    without a spread.
    """
    catalogue = _catalogue()
    own = matches.merge(player[SEASON_KEYS], on=SEASON_KEYS)
    values = pd.concat(
        [
            wide.stack().rename("value").reset_index().assign(file=file)
            for file, wide in _season_values(catalogue, own, player["min_match_minutes"].iloc[0])
        ],
        ignore_index=True,
    )
    df = values.merge(reference, on=[*BY, "file", "metric"], how="left")
    df = df.merge(catalogue[["file", "metric", "category", "per", "inverse"]], on=["file", "metric"])
    z = (df["value"] - df["mean"]) / df["std"].where((df["std"] > 0) & (df["players"] >= 2))
    df["z"] = z.where(~df["inverse"], -z)
    return df


def strongest(strengths: pd.DataFrame, min_events: float | None = None, n: int = 10) -> pd.DataFrame:
    """The `n` highest z-scores per role and category of the output of `player_strengths`.

    With `min_events`, only metrics with at least that many events per match
    for the median player of the role are kept; physical metrics always are.
    A metric that is in several files of a category is listed once, from
    on_ball_engagements if it is there.
    """
    df = strengths.dropna(subset="z")
    if min_events is not None:
        df = df[df["events_per_match"].fillna(min_events) >= min_events]
    first = (df["file"] != "on_ball_engagements").to_numpy().argsort(kind="stable")
    df = df.iloc[first].drop_duplicates(["role", "category", "metric"])
    return df.sort_values("z", ascending=False).groupby(["role", "category"]).head(n)
