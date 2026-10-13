"""Profile builder: a role, a name, and metrics with weights; with a correlation check before saving."""

import numpy as np
import pandas as pd
import streamlit as st

from src.benchmarks import engine
from src.benchmarks.profiles import STRONG_CORRELATION, delete_profile, load_profiles, save_profile, strong_pairs
from src.benchmarks.usefulness import DEFAULT_MIN_EVENTS, events_per_match
from src.data import foundation, loaders
from src.data.catalogue import load_catalogue, metric_parts
from src.data.roles import role_positions
from src.viz.theme import inject_theme

cached_player_matches = st.cache_data(foundation.player_matches)
cached_load_derived = st.cache_data(loaders.load_derived)
cached_benchmark = st.cache_data(engine.benchmark)
cached_events = st.cache_data(events_per_match)

NEW = "New profile"
ALL = "All"
# The order of the boxes: each one is limited by the ones before it.
FILTERS = {"Category": "category", "Action": "action", "Measure": "measure", "Phase / block": "phase"}

st.set_page_config(page_title="Profile Builder", layout="wide")
inject_theme()
st.title("Profile Builder")
st.caption(
    "A profile is a set of metrics with weights for one role. Stored in data/profiles.csv. "
    "The Benchmarks page calculates scores for every metric that is in at least one profile."
)

seasons_path = loaders.latest_derived("player_seasons")
if seasons_path is None:
    st.info("No player table yet. Press Recalculate on the main page.")
    st.stop()
seasons = cached_load_derived(seasons_path)

catalogue = metric_parts(load_catalogue())
catalogue = catalogue[catalogue["scope"] == "full"]
catalogue = catalogue.assign(label=catalogue["file"] + " / " + catalogue["metric"])
labels = catalogue["label"].tolist()
metric_of = dict(zip(labels, zip(catalogue["file"], catalogue["metric"])))
roles = list(role_positions())
st.session_state.setdefault("metrics", [])


def weight_key(label: str) -> str:
    return f"weight::{label}"


def load_picked():
    """Fill the form with the picked profile (or empty it for a new one)."""
    rows = load_profiles()
    rows = rows[rows["profile"] == st.session_state["picked"]]
    rows = rows[(rows["file"] + " / " + rows["metric"]).isin(metric_of)]
    st.session_state["name"] = "" if rows.empty else st.session_state["picked"]
    st.session_state["metrics"] = (rows["file"] + " / " + rows["metric"]).tolist()
    if not rows.empty and rows["role"].iloc[0] in roles:
        st.session_state["role"] = rows["role"].iloc[0]
    for label, weight in zip(st.session_state["metrics"], rows["weight"]):
        st.session_state[weight_key(label)] = float(weight)


def equal_weights():
    for label in st.session_state["metrics"]:
        st.session_state[weight_key(label)] = 1 / len(st.session_state["metrics"])


def add_metric():
    label = st.session_state.get("candidate")
    if label and label not in st.session_state["metrics"]:
        st.session_state["metrics"] = [*st.session_state["metrics"], label]


def delete_picked():
    delete_profile(st.session_state["picked"])
    st.session_state["picked"] = NEW
    load_picked()


profiles = load_profiles()
c1, c2, c3 = st.columns(3)
picked = c1.selectbox("Profile", [NEW, *sorted(profiles["profile"].unique())], key="picked", on_change=load_picked)
role = c2.selectbox("Role", roles, key="role")
name = c3.text_input("Profile name", key="name").strip()
if picked != NEW:
    st.button("Delete this profile", on_click=delete_picked)

# Events per match behind each metric, for the median player of this role. Physical metrics have none.
events = cached_events(seasons, cached_player_matches())
events = events[events["role"] == role]
events_of = dict(zip(events["file"] + " / " + events["metric"], events["events_per_match"]))

st.subheader("Add metrics")
c1, c2 = st.columns([1, 3])
min_events = c1.number_input(
    "Minimum events per match",
    min_value=0.0,
    value=DEFAULT_MIN_EVENTS,
    step=0.1,
    help="A metric is useful for a role if the median player of that role, with enough matches, has at "
    "least this many of the events behind it per match. Physical metrics are always useful.",
)
useful_only = c2.checkbox("Useful metrics only", value=True)

# A pressure metric that is in several files is listed once, from on_ball_engagements if it is there.
first = (catalogue["file"] != "on_ball_engagements").to_numpy().argsort(kind="stable")
options = catalogue.iloc[first].drop_duplicates(["category", "metric"]).sort_index()
if useful_only:
    options = options[options["label"].map(events_of).fillna(min_events) >= min_events]
for box, (title, column) in zip(st.columns(len(FILTERS)), FILTERS.items()):
    choices = options[column].drop_duplicates().tolist()
    choice = box.selectbox(title, choices if column == "category" else [ALL, *choices], key=f"filter::{column}")
    if choice != ALL:
        options = options[options[column] == choice]


def metric_label(label: str) -> str:
    name = metric_of[label][1]
    return f"{name} ({events_of[label]:.2f} per match)" if label in events_of else name


c1, c2 = st.columns([4, 1], vertical_alignment="bottom")
c1.selectbox(
    f"Metric ({len(options)} to choose from)",
    options["label"].tolist(),
    key="candidate",
    format_func=metric_label,
    help="Type to search. In brackets: events per match of the median player of this role.",
)
c2.button("Add to profile", on_click=add_metric, disabled=options.empty)

chosen = st.multiselect(
    "Metrics in this profile",
    st.session_state["metrics"],
    key="metrics",
    help="Remove a metric here. Add one with the boxes above.",
)
if not chosen:
    st.info("Add one or more metrics.")
    st.stop()

rare = [label for label in chosen if events_of.get(label, min_events) < min_events]
if rare:
    st.warning(
        f"Fewer than {min_events:g} events per match for the median player in role {role}. "
        "Scores on these metrics are built on few events.\n\n"
        + "\n".join(f"- {label}: {events_of[label]:.2f} per match" for label in rare)
    )

st.subheader("Weights")
st.button("Equal weights", on_click=equal_weights)
weights = []
columns = st.columns(3)
for i, label in enumerate(chosen):
    st.session_state.setdefault(weight_key(label), 0.0)
    weights.append(
        columns[i % 3].number_input(
            label, min_value=0.0, max_value=1.0, step=0.05, format="%.3f", key=weight_key(label)
        )
    )
total = sum(weights)
sum_ok = round(total, 3) == 1
st.write(f"Sum of the weights: {total:.3f}. The sum has to be 1.")

st.subheader("Correlations")
pairs = []
if len(chosen) < 2:
    st.write("A correlation needs at least two metrics.")
else:
    metrics = pd.DataFrame([metric_of[label] for label in chosen], columns=["file", "metric"])
    benchmarks = cached_benchmark(metrics, seasons, cached_player_matches())
    reference = benchmarks[(benchmarks["role"] == role) & ~benchmarks["low_sample"]]
    z = reference[[f"{engine.metric_id(*metric_of[label])}_z" for label in chosen]].set_axis(chosen, axis=1)
    correlations = z.corr()
    pairs = strong_pairs(correlations)

    def highlight(frame: pd.DataFrame) -> pd.DataFrame:
        strong = (frame.abs() >= STRONG_CORRELATION) & ~np.eye(len(frame), dtype=bool)
        return pd.DataFrame(
            np.where(strong, "background-color: #f2913f; color: #000000", ""), index=frame.index, columns=frame.columns
        )

    st.dataframe(correlations.style.format("{:.2f}").apply(highlight, axis=None), width="stretch")
    st.caption(
        f"Correlation of the z-scores over the {len(reference)} players with enough matches in role "
        f"{role}, all competitions together. z-scores are within competition, and flipped for "
        f"lower-is-better metrics. Marked: {STRONG_CORRELATION} or more, positive or negative."
    )
    if pairs:
        st.warning(
            f"Strong correlations ({STRONG_CORRELATION} or more): these metrics partly measure the same thing.\n\n"
            + "\n".join(f"- {a} and {b}: {value:.2f}" for a, b, value in pairs)
        )
    else:
        st.write(f"No pair of metrics has a correlation of {STRONG_CORRELATION} or more.")

st.subheader("Save")
accepted = st.checkbox("Save anyway, with the strong correlations listed above") if pairs else True
if not name:
    st.write("Type a profile name.")
elif name in set(profiles["profile"]) and name != picked:
    st.warning(f"A profile named {name} exists. Saving replaces it.")
if st.button("Save profile", type="primary", disabled=not (name and sum_ok and accepted)):
    rows = pd.DataFrame([metric_of[label] for label in chosen], columns=["file", "metric"]).assign(weight=weights)
    save_profile(name, role, rows)
    st.success(
        f"Saved profile {name} to data/profiles.csv. Press Recalculate benchmarks on the Benchmarks "
        "page to calculate its scores."
    )
