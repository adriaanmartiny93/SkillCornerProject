"""Benchmarks: season value, percentile and z-score per metric, and profile scores."""

import pandas as pd

from src.benchmarks.profiles import load_profiles
from src.data.catalogue import metric_specs
from src.data.foundation import SEASON_KEYS, match_values, rate_column, season_rates, standardise
from src.data.loaders import write_derived


def metric_id(file: str, metric: str) -> str:
    """Column name of a metric in a benchmark table; the same metric name can be in several files."""
    return f"{file}.{metric}"


def benchmark(metrics: pd.DataFrame, seasons: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Season value, percentile and z-score of each metric, per row of the player-season table.

    `metrics` has the columns file and metric (raw or calculated). Per metric
    the result has `<file>.<metric>` (season value), `..._pct` and `..._z`,
    within competition and role. For lower-is-better metrics the percentile
    and z-score are flipped, so higher is always better; the season value is
    not changed.
    """
    min_match_minutes = seasons["min_match_minutes"].iloc[0]
    df = seasons[[*SEASON_KEYS, "matches_included", "low_sample"]]
    ids, inverse = [], []
    for file, rows in metrics.groupby("file", sort=False):
        names = rows["metric"].unique().tolist()
        specs = metric_specs(file)
        rates = season_rates(match_values(file, names, matches), file, names, min_match_minutes)
        columns = {rate_column(file, name): metric_id(file, name) for name in names}
        df = df.merge(rates.rename(columns=columns)[[*SEASON_KEYS, *columns.values()]], on=SEASON_KEYS, how="left")
        ids += columns.values()
        inverse += [metric_id(file, name) for name in names if specs.at[name, "inverse"]]
    signed = df.copy()
    signed[inverse] = -signed[inverse]
    scores = standardise(signed, ids).drop(columns=df.columns)
    return pd.concat([df, scores], axis=1)


def profile_score(benchmarks: pd.DataFrame, profile: pd.DataFrame) -> pd.DataFrame:
    """The rows of the profile's role, with `score` (weighted mean of the z-scores) and its percentile.

    `profile` holds the rows of one profile. A player without a value for one
    of the metrics gets no score.
    """
    df = benchmarks[benchmarks["role"] == profile["role"].iloc[0]].copy()
    columns = [f"{metric_id(file, metric)}_z" for file, metric in zip(profile["file"], profile["metric"])]
    weights = profile["weight"].to_numpy()
    df["score"] = (df[columns] * weights).sum(axis=1, skipna=False) / weights.sum()
    return standardise(df, ["score"]).drop(columns="score_z")


def run_benchmarks(seasons: pd.DataFrame, matches: pd.DataFrame):
    """Benchmark every metric that is in at least one profile and write the table to data/derived/."""
    metrics = load_profiles()[["file", "metric"]].drop_duplicates()
    return write_derived(benchmark(metrics, seasons, matches), "benchmarks")
