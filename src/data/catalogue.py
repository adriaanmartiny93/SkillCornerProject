"""Metric catalogue: one row per metric column of the raw files.

The catalogue is built once from the naming rules below and stored as
`data/metric_catalogue.csv`. From then on the stored file is the truth: the
calculation, per, weight, match filter and inverse fields can be edited in
the app.

Rows with origin "raw" are the columns of the raw files. Rows with origin
"custom" are calculated metrics added in the app: a new name that reads a raw
column (`source`) and has its own calculation.
"""

import html
import re

import pandas as pd

from src.data.inventory import METRIC_FILES
from src.data.loaders import load_catalogue_file, raw_columns, read_glossary, save_catalogue_file

BEST_X = "average of best x"

# How the season value of a metric is calculated from its match values.
CALCULATIONS = {
    "total": "Each match as a rate per 90 or per 30 minutes (TIP / OTIP), then the plain mean over matches",
    "ratio": "Sum over matches divided by the sum of the weight column",
    "average": "Mean over matches, weighted by the weight column",
    "max": "Highest match value of the season",
    "min": "Lowest match value of the season",
    BEST_X: "Mean of the x best match values of the season (the x lowest if lower is better)",
}

# per: (minutes phase, number of minutes)
PER = {"30 TIP": ("tip", 30), "30 OTIP": ("otip", 30), "90": ("all", 90)}

COLUMNS = [
    "category", "file", "metric", "type", "definition",
    "scope", "calculation", "per", "weight", "match_filter", "inverse",
    "source", "origin", "best_x",
]

_KEYS = {"competition_edition_id", "match_id", "player_id"}
_TYPE_BY_PREFIX = {"xthreat": "Threat", "xpass": "Probability", "avg": "Physical"}


def load_catalogue() -> pd.DataFrame:
    """The stored catalogue; it is built from the rules on first use."""
    catalogue = load_catalogue_file()
    if catalogue is None:
        catalogue = build_catalogue()
        save_catalogue_file(catalogue)
    elif "match_filter" not in catalogue:
        # Catalogue stored before the match filter existed: add the default.
        catalogue["match_filter"] = _match_filter(catalogue["calculation"])
        catalogue = catalogue[[c for c in COLUMNS if c in catalogue]]
        save_catalogue_file(catalogue)
    if "origin" not in catalogue:
        # Catalogue stored before calculated metrics existed.
        catalogue["calculation"] = catalogue["calculation"].replace("expected total", "ratio")
        catalogue = _as_raw(catalogue)
        save_catalogue_file(catalogue)
    return catalogue


def metric_specs(name: str) -> pd.DataFrame:
    """Catalogue rows of one raw file, indexed by metric."""
    catalogue = load_catalogue()
    return catalogue[catalogue["file"] == name].set_index("metric")


def build_catalogue() -> pd.DataFrame:
    """Build the catalogue from the raw column names and the glossary."""
    glossary = _glossary()
    rows = []
    for name, (family, phase) in METRIC_FILES.items():
        columns = raw_columns(name)
        for metric in columns:
            row = _physical_row(metric) if name == "physical" else _event_row(metric, phase, columns)
            if row is None:
                continue
            kind, definition = glossary.get(metric, ("", ""))
            row = {"category": family, "file": name, "metric": metric, "definition": definition, **row}
            row["type"] = kind or row["type"]
            rows.append(row)
    catalogue = pd.DataFrame(rows)
    catalogue["match_filter"] = _match_filter(catalogue["calculation"])
    return _as_raw(catalogue)


def rebuild_catalogue() -> pd.DataFrame:
    """The catalogue rebuilt from the rules; calculated metrics are kept."""
    stored = load_catalogue()
    custom = stored[stored["origin"] == "custom"]
    return pd.concat([build_catalogue(), custom], ignore_index=True)


def name_taken(catalogue: pd.DataFrame, file: str, name: str) -> bool:
    """True if `name` is already a metric or a column for this file."""
    metrics = catalogue.loc[catalogue["file"] == file, "metric"]
    return name in {*metrics, *raw_columns(file), *raw_columns("physical"), "role"}


def add_metric(
    catalogue: pd.DataFrame,
    file: str,
    name: str,
    source: str,
    calculation: str,
    weight: str = "",
    best_x: int = 0,
    match_filter: bool = True,
    inverse: bool = False,
) -> pd.DataFrame:
    """The catalogue with one calculated metric added: `source` under a new name."""
    raw = catalogue[(catalogue["file"] == file) & (catalogue["metric"] == source)].iloc[0]
    if calculation == BEST_X:
        definition = f"Mean of the best {best_x} match values of {source}"
    else:
        definition = f"{source} divided by {weight}, both summed over the season"
    row = {
        **raw,
        "metric": name,
        "type": "Calculated",
        "definition": definition,
        "calculation": calculation,
        "per": "",
        "weight": weight,
        "match_filter": match_filter,
        "inverse": inverse,
        "source": source,
        "origin": "custom",
        "best_x": best_x,
    }
    return pd.concat([catalogue, pd.DataFrame([row])], ignore_index=True)


def _as_raw(catalogue: pd.DataFrame) -> pd.DataFrame:
    """Mark every row as a raw column that is read under its own name."""
    return catalogue.assign(source=catalogue["metric"], origin="raw", best_x=0)[COLUMNS]


def _match_filter(calculation: pd.Series) -> pd.Series:
    """Aggregates only use matches with enough minutes; best values use every match."""
    return ~calculation.isin(["max", "min", BEST_X])


def _glossary() -> dict[str, tuple[str, str]]:
    """Metric name -> (type, definition) from the aggregates guide."""
    items = re.findall(
        r'metric-name-text">(.*?)</span>\s*<span class="metric-type">(.*?)</span>\s*</div>'
        r'\s*<div class="metric-description">(.*?)</div>',
        read_glossary(),
        re.S,
    )
    out = {}
    for metric, kind, definition in items:
        out.setdefault(metric.strip(), (kind.strip(), html.unescape(definition.strip())))
    return out


def _event_row(metric: str, phase: str, columns: list[str]) -> dict | None:
    if metric in _KEYS or metric.startswith("player_"):
        return None
    prefix = metric.split("_", 1)[0]
    row = {
        "type": _TYPE_BY_PREFIX.get(prefix, "Count"),
        "scope": "full",
        "calculation": "total",
        "per": f"30 {phase.upper()}",
        "weight": "",
        "inverse": "beaten_by" in metric,
    }
    # Sums of probabilities and match averages are tied to a count column.
    match = re.match(r"(?:xpass_completion|avg_speed_avg|avg_distance_covered|avg_speed_difference)_(.*)", metric)
    if match:
        count = f"count_{match.group(1)}"
        row["calculation"] = "ratio" if prefix == "xpass" else "average"
        row["per"] = ""
        row["weight"] = count if count in columns else ""
    return row


def _physical_row(metric: str) -> dict | None:
    row = {"type": "Physical", "scope": "full", "per": "", "weight": "", "inverse": False}
    if metric == "psv99":
        return {**row, "calculation": "max"}
    if metric in ("timetohsr", "timetosprint"):
        return {**row, "calculation": "min", "inverse": True}
    match = re.search(r"_(full|h1|h2)_(all|tip|otip)$", metric)
    if match is None or metric.startswith("minutes_"):
        return None
    scope, phase = match.groups()
    row["scope"] = scope
    if "metersperminute" in metric:
        # Minutes-weighted mean = season distance divided by season minutes.
        return {**row, "calculation": "average", "weight": f"minutes_{scope}_{phase}"}
    per = "90" if phase == "all" else f"30 {phase.upper()}"
    return {**row, "calculation": "total", "per": per}
