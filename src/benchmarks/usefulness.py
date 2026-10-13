"""Is a metric useful for a role: how often the events behind it happen."""

import pandas as pd

from src.data.catalogue import load_catalogue
from src.data.foundation import MINUTES, SEASON_KEYS
from src.data.loaders import load_raw, raw_columns

# A metric is useful for a role if the median player has at least this many events per match.
DEFAULT_MIN_EVENTS = 0.3


def events_per_match(seasons: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Events per match behind each event metric, for the median reference player of each role.

    One row per file, metric and role, with `events_per_match`. The events are
    the count behind the metric: the metric itself for a count, the matching
    `count_...` column for an xthreat metric, the weight column for a ratio or
    an average. A calculated ratio is judged on its outcome (the column above
    the line), which is rarer than the column it is divided by. Reference players are the rows of `seasons` that are not low
    sample, all competitions together; only their included matches are used.
    Physical metrics are not in the result: they are measured in every match.
    """
    min_match_minutes = seasons["min_match_minutes"].iloc[0]
    reference = seasons.loc[~seasons["low_sample"], SEASON_KEYS]
    catalogue = load_catalogue()
    catalogue = catalogue[catalogue["file"] != "physical"]
    out = []
    for file, rows in catalogue.groupby("file"):
        available = set(raw_columns(file))
        events = {}
        for metric, source, calculation, weight, origin in zip(
            rows["metric"], rows["source"], rows["calculation"], rows["weight"].fillna(""), rows["origin"]
        ):
            count = f"count_{source.removeprefix('xthreat_')}"
            if calculation == "ratio" and origin == "custom":
                events[metric] = source
            elif calculation in ("ratio", "average") and weight in available:
                events[metric] = weight
            elif source.startswith("xthreat_") and count in available:
                events[metric] = count
            else:
                events[metric] = source
        columns = sorted(set(events.values()))
        values = load_raw(file, columns=["match_id", "player_id", *columns])
        df = matches[matches["match_id"].isin(values["match_id"].unique())]
        df = df[df[MINUTES["all"]] >= min_match_minutes].merge(reference, on=SEASON_KEYS)
        df = df.merge(values, on=["match_id", "player_id"], how="left")
        df[columns] = df[columns].fillna(0)
        per_player = df.groupby(SEASON_KEYS)[columns].mean()
        per_role = per_player.groupby("role").median()
        for metric, column in events.items():
            out.append(
                pd.DataFrame(
                    {"file": file, "metric": metric, "role": per_role.index, "events_per_match": per_role[column].to_numpy()}
                )
            )
    return pd.concat(out, ignore_index=True)
