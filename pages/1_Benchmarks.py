"""Benchmarks: percentile, z-score and season value of the metrics of a profile, with the profile score."""

import streamlit as st

from src.benchmarks import engine, strengths
from src.benchmarks.profiles import load_profiles
from src.data import foundation, loaders
from src.viz.theme import inject_theme

cached_player_matches = st.cache_data(foundation.player_matches)
cached_load_derived = st.cache_data(loaders.load_derived)
cached_ratings = st.cache_data(engine.competition_ratings)

SHOW = {"Percentile": "_pct", "z-score": "_z", "Season value": ""}

st.set_page_config(page_title="Benchmarks", layout="wide")
inject_theme()
st.title("Benchmarks")
st.caption(
    "Season value, percentile and z-score of every metric that is in at least one profile, within "
    "competition and role. For lower-is-better metrics the percentile and z-score are flipped: "
    "higher is always better."
)

profiles = load_profiles()
seasons_path = loaders.latest_derived("player_seasons")
if seasons_path is None:
    st.info("No player table yet. Press Recalculate on the main page.")
    st.stop()
if profiles.empty:
    st.info("No profiles yet. Create one on the Profile Builder page.")
    st.stop()

with st.sidebar:
    st.header("Benchmarks")
    if st.button("Recalculate benchmarks", type="primary"):
        written = engine.run_benchmarks(cached_load_derived(seasons_path), cached_player_matches())
        st.success(f"Written: data/derived/{written.name}")
    if st.button(
        "Recalculate metric reference",
        help="Mean and spread of every full-match metric per competition and role. Used for the strongest "
        "metrics on the Player Profile page. Takes about half a minute.",
    ):
        with st.spinner("Calculating every metric for every player"):
            written = strengths.run_metric_reference(cached_load_derived(seasons_path), cached_player_matches())
        st.success(f"Written: data/derived/{written.name}")
    points_per_z = st.session_state["points_per_z"] = st.number_input(
        "Rating points per z-score",
        min_value=1.0,
        value=float(st.session_state.get("points_per_z", engine.DEFAULT_POINTS_PER_Z)),
        help="League strength: this many Opta rating points count as one z-score in the weighted profile score.",
    )

path = loaders.latest_derived("benchmarks")
if path is None:
    st.info("No benchmarks yet. Press Recalculate benchmarks in the sidebar.")
    st.stop()
benchmarks = cached_load_derived(path)

c1, c2, c3, c4 = st.columns(4)
name = c1.selectbox("Profile", sorted(profiles["profile"].unique()))
profile = profiles[profiles["profile"] == name]
ids = [engine.metric_id(file, metric) for file, metric in zip(profile["file"], profile["metric"])]
if any(f"{i}_z" not in benchmarks for i in ids):
    st.info("This profile has metrics that are not in the stored benchmarks. Press Recalculate benchmarks in the sidebar.")
    st.stop()

scored = engine.weighted_score(engine.profile_score(benchmarks, profile), cached_ratings(), points_per_z)
# A z-score needs a spread: it is missing where every reference player has the same value.
no_spread = scored.groupby("competition_name")[[f"{i}_z" for i in ids]].count().eq(0)
competitions = c2.multiselect("Competition", sorted(scored["competition_name"].unique()))
sample = c3.selectbox("Sample", ["Enough matches", "All", "Low sample"])
show = c4.selectbox("Show per metric", list(SHOW))

view = scored
if competitions:
    view = view[view["competition_name"].isin(competitions)]
if sample != "All":
    view = view[view["low_sample"] == (sample == "Low sample")]

# Short column names: the metric name, with the file in front if the name is in two files.
short = {
    i: metric if (profile["metric"] == metric).sum() == 1 else i
    for i, metric in zip(ids, profile["metric"])
}
table = view[["player_name", "team_name", "competition_name", "matches_included", "low_sample", "score", "score_pct", "score_weighted", "score_weighted_pct"]]
table = table.join(view[[f"{i}{SHOW[show]}" for i in ids]].set_axis(list(short.values()), axis=1))

st.write(
    f"Profile {name}, role {profile['role'].iloc[0]}: "
    + ", ".join(f"{short[i]} ({weight:g})" for i, weight in zip(ids, profile["weight"]))
    + "."
)
if competitions:
    no_spread = no_spread.loc[no_spread.index.isin(competitions)]
missing = {short[i]: no_spread.index[no_spread[f"{i}_z"]].tolist() for i in ids if no_spread[f"{i}_z"].any()}
unrated =sorted(view.loc[view["opta_rating"].isna(), "competition_name"].unique())
if unrated:
    st.warning(f"No weighted score: not in data/raw/competition_power_rankings.csv: {', '.join(unrated)}.")
if missing:
    st.warning(
        "No profile score in these competitions: every reference player has the same value for the metric, "
        "so it has no z-score. Replace the metric in the Profile Builder.\n\n"
        + "\n".join(f"- {metric}: {', '.join(names)}" for metric, names in missing.items())
    )
st.dataframe(
    table.sort_values("score", ascending=False),
    hide_index=True,
    width="stretch",
    column_config={
        "score": st.column_config.NumberColumn("profile score", format="%.2f"),
        "score_pct": st.column_config.NumberColumn("score percentile", format="%.0f"),
        "score_weighted": st.column_config.NumberColumn("profile score (weighted)", format="%.2f"),
        "score_weighted_pct": st.column_config.NumberColumn("profile percentile (weighted)", format="%.0f"),
    },
)
st.caption(
    f"Source: data/derived/{path.name}. Profile score: the weighted mean of the z-scores of the "
    "profile's metrics, with the weights as they are stored now. Score percentile: within "
    "competition and role. Low-sample players are left out of the reference but still get a score. "
    "A player without a value for one of the metrics gets no score. Profile score (weighted): the profile "
    "score minus the gap in Opta power rating between the strongest league and the player's league, divided by "
    f"{points_per_z:g} rating points per z-score. Profile percentile (weighted): within the role over all "
    "competitions together."
)
