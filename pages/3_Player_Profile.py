"""Player profile: minutes and positions, profile scores and strongest metrics for the two most played roles, best players in a profile."""

import streamlit as st

from src.benchmarks import engine, strengths
from src.benchmarks.profiles import load_profiles
from src.benchmarks.usefulness import DEFAULT_MIN_EVENTS
from src.data import foundation, loaders
from src.viz import payloads, visuals
from src.viz.theme import badge, header, inject_theme, percentile_bars

cached_player_matches = st.cache_data(foundation.player_matches)
cached_load_derived = st.cache_data(loaders.load_derived)
cached_load_raw = st.cache_data(loaders.load_raw)
cached_profile_score = st.cache_data(engine.profile_score)
cached_ratings = st.cache_data(engine.competition_ratings)

PLAYER_KEYS = ["competition_edition_id", "team_id", "player_id"]

st.set_page_config(page_title="Player Profile", layout="wide")
inject_theme()

seasons_path = loaders.latest_derived("player_seasons")
if seasons_path is None:
    st.info("No player table yet. Press Recalculate on the main page.")
    st.stop()
seasons = cached_load_derived(seasons_path)
matches = cached_player_matches()
editions = cached_load_raw("competition_editions")
profiles = load_profiles()
min_match_minutes = seasons["min_match_minutes"].iloc[0]
# Set on the Benchmarks page.
points_per_z = st.session_state.get("points_per_z", engine.DEFAULT_POINTS_PER_Z)

# 1. Player selector: each box is limited by the one before.
c1, c2, c3, c4 = st.columns(4)
season = c1.selectbox("Season", sorted(editions["season_name"].unique(), reverse=True))
in_season = seasons[seasons["competition_edition_id"].isin(editions.loc[editions["season_name"] == season, "id"])]
competition = c2.selectbox("Competition", sorted(in_season["competition_name"].unique()))
in_competition = in_season[in_season["competition_name"] == competition]
team = c3.selectbox("Team (optional)", ["All teams", *sorted(in_competition["team_name"].unique())],placeholder="ENG - Premier League")
if team != "All teams":
    in_competition = in_competition[in_competition["team_name"] == team]
players = (
    in_competition.groupby([*PLAYER_KEYS, "player_name", "team_name"], as_index=False)["minutes"]
    .sum()
    .sort_values(["player_name", "team_name"])
    .reset_index(drop=True)
)
pick = c4.selectbox(
    "Player", players.index, format_func=lambda i: f"{players.at[i, 'player_name']} ({players.at[i, 'team_name']})"
)
player = players.loc[pick]


def of_player(df):
    """The rows of `df` of the chosen player at the chosen team and competition."""
    return df[(df[PLAYER_KEYS] == player[PLAYER_KEYS].to_numpy()).all(axis=1)]


# 2. Minutes, games, position breakdown.
played = of_player(matches)
roles = of_player(seasons).sort_values("minutes", ascending=False)
top_roles = roles.head(2)
main = roles.iloc[0]

header(player["player_name"], eyebrow=f"Player profile · {competition} · {season}")
st.markdown(
    badge(player["team_name"], "info")
    + " "
    + badge(main["role"])
    + (" " + badge("Low sample", "warning") if main["low_sample"] else ""),
    unsafe_allow_html=True,
)
st.write("")

c = st.columns(4)
c[0].metric("Matches", played["match_id"].nunique())
c[1].metric(f"Matches of {min_match_minutes:g}+ minutes", int((played[foundation.MINUTES["all"]] >= min_match_minutes).sum()))
c[2].metric("Minutes", f"{played[foundation.MINUTES['all']].sum():,.0f}")
c[3].metric("Positions played", played["position"].nunique())

positions = (
    played.groupby("position", as_index=False)
    .agg(role=("role", "first"), matches=("match_id", "nunique"), minutes=(foundation.MINUTES["all"], "sum"))
    .sort_values("minutes", ascending=False)
)
positions["share"] = positions["minutes"] / positions["minutes"].sum() * 100
left, right = st.columns([1.2, 1])
with left:
    visuals.show(
        "bar",
        payloads.bar(positions["position"], [("Minutes", positions["minutes"].round())], title="Minutes per position",
                     eyebrow="Position breakdown", unit="min", height=280),
        key="positions",
    )
with right:
    st.dataframe(
        positions,
        hide_index=True,
        width="stretch",
        column_config={
            "minutes": st.column_config.NumberColumn(format="%.0f"),
            "share": st.column_config.NumberColumn("share of minutes", format="%.0f%%"),
        },
    )

# 3. Profile scores within the two most played roles.
st.subheader("Profile scores")
benchmarks_path = loaders.latest_derived("benchmarks")
if benchmarks_path is None:
    st.info("No benchmarks yet. Press Recalculate benchmarks on the Benchmarks page.")
    st.stop()
benchmarks = cached_load_derived(benchmarks_path)


def metric_ids(profile):
    return [engine.metric_id(file, metric) for file, metric in zip(profile["file"], profile["metric"])]


SCORES = ["score", "score_pct"]
# Per profile of the two roles: the scored rows of the role and the row of this player.
scored, own, stale = {}, {}, []
for role in top_roles["role"]:
    for name, profile in profiles[profiles["role"] == role].groupby("profile"):
        if any(f"{i}_z" not in benchmarks for i in metric_ids(profile)):
            stale.append(name)
            continue
        scored[name] = engine.weighted_score(cached_profile_score(benchmarks, profile), cached_ratings(), points_per_z)
        own[name] = of_player(scored[name]).iloc[0]
if stale:
    st.info(
        f"Not shown: {', '.join(stale)}. These profiles have metrics that are not in the stored benchmarks. "
        "Press Recalculate benchmarks on the Benchmarks page."
    )

left, right = st.columns(2)
with left:
    for _, row in top_roles.iterrows():
        role = row["role"]
        st.markdown(
            f"**{role}** · {row['minutes']:,.0f} minutes · {row['matches_included']} of {row['matches']} matches included"
            + (" " + badge("Low sample", "warning") if row["low_sample"] else ""),
            unsafe_allow_html=True,
        )
        names = [name for name in scored if scored[name]["role"].iloc[0] == role]
        if not names:
            if role not in profiles["role"].values:
                st.caption("No profile for this role yet.")
            continue
        with st.container(border=True):
            percentile_bars(
                (name, own[name]["score_pct"], f"score {own[name]['score']:+.2f}")
                for name in names
                if own[name][SCORES].notna().all()
            )
        empty = [name for name in names if own[name][SCORES].isna().any()]
        if empty:
            st.caption(f"No score for {', '.join(empty)}: the player has no z-score for one of its metrics.")
    st.caption(
        "Bar: percentile of the profile score within competition and role. Score: weighted mean of the z-scores."
    )
with right:
    if not scored:
        st.caption("No profile to draw for these roles.")
    else:
        r1, r2 = st.columns(2)
        with_profile = [role for role in top_roles["role"] if any(scored[n]["role"].iloc[0] == role for n in scored)]
        radar_role = r1.selectbox("Role", with_profile)
        radar_name = r2.selectbox("Profile", [n for n in scored if scored[n]["role"].iloc[0] == radar_role])
        profile = profiles[profiles["profile"] == radar_name]
        ids = metric_ids(profile)
        visuals.show(
            "radar",
            payloads.radar(
                [metric.replace("_", " ") for metric in profile["metric"]],
                [(player["player_name"], [own[radar_name][f"{i}_pct"] for i in ids]), ("Role median", [50] * len(ids))],
                title=radar_name, eyebrow=f"Radar · percentile within {competition}, {radar_role}",
                dashed=["Role median"], colours=[payloads.SERIES[0], payloads.REFERENCE],
            ),
            key="radar",
        )

# 4. Strongest metrics per category, within competition and role.
st.subheader("Strongest metrics")
reference_path = loaders.latest_derived("metric_reference")
if reference_path is None:
    st.info("No metric reference yet. Press Recalculate metric reference on the Benchmarks page.")
else:
    # The result is kept for this player, so the boxes below do not calculate again.
    strengths_key = (*player[PLAYER_KEYS], reference_path.name)
    if st.button("Run calculations", type="primary"):
        with st.spinner("Calculating every metric for this player"):
            result = strengths.player_strengths(top_roles, matches, cached_load_derived(reference_path))
        st.session_state["strengths"] = (strengths_key, result)
    stored_key, result = st.session_state.get("strengths", (None, None))
    if stored_key != strengths_key:
        st.caption(
            "Press Run calculations for the ten metrics with the highest z-score per category, for the two most "
            "played roles. Takes about ten seconds."
        )
    else:
        s1, s2 = st.columns([2, 1])
        strengths_role = s1.radio("Role", top_roles["role"], horizontal=True, key="strengths_role")
        useful_only = s2.toggle("Useful metrics only", value=True)
        row = top_roles[top_roles["role"] == strengths_role].iloc[0]
        in_role = in_season[(in_season["competition_name"] == competition) & (in_season["role"] == strengths_role)]
        st.markdown(
            f"**{strengths_role}** · {row['minutes']:,.0f} minutes · z-scores against "
            f"{(~in_role['low_sample']).sum()} players"
            + (" " + badge("Low sample", "warning") if row["low_sample"] else ""),
            unsafe_allow_html=True,
        )
        top = strengths.strongest(result[result["role"] == strengths_role], DEFAULT_MIN_EVENTS if useful_only else None)
        boxes = st.columns(2)
        for i, category in enumerate(result["category"].unique()):
            with boxes[i % 2]:
                st.markdown(f"**{category}**")
                st.dataframe(
                    top.loc[top["category"] == category, ["metric", "file", "value", "per", "z"]],
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "value": st.column_config.NumberColumn("season value", format="%.2f"),
                        "z": st.column_config.NumberColumn("z-score", format="%+.2f"),
                    },
                )
        st.caption(
            f"Source: data/derived/{reference_path.name}. z-score: the season value against the mean and spread "
            f"of the players with enough matches in the same role in {competition}; flipped for lower-is-better "
            f"metrics, so higher is always better. Useful metrics only: the median player of the role has at "
            f"least {DEFAULT_MIN_EVENTS:g} of the events behind the metric per match. A metric that is in several "
            "files of a category is listed once. First-half and second-half metrics are left out."
        )

# 5. Best players in one profile, next to the chosen player.
st.subheader("Best players in the profile")
if not scored:
    st.caption("The two most played roles have no profile, so there is nothing to compare on.")
    st.stop()
s1, s2 = st.columns([2, 1])
best_name = s1.selectbox(
    "Profile (role)", list(scored), format_func=lambda n: f"{n} ({scored[n]['role'].iloc[0]})", key="best_profile"
)
include_low_sample = s2.toggle("Include low sample players")
target = own[best_name]
candidates = scored[best_name][scored[best_name]["player_id"] != target["player_id"]]
if not include_low_sample:
    candidates = candidates[~candidates["low_sample"]]
best = candidates.nlargest(5, "score_weighted")
table = scored[best_name].loc[[target.name, *best.index]]
table.insert(0, "rank", ["Target", *range(1, len(best) + 1)])
table["difference"] = table["score_weighted"] - target["score_weighted"]
st.dataframe(
    table[["rank", "player_name", "team_name", "competition_name", "matches_included", "low_sample", "score", "score_pct", "score_weighted", "score_weighted_pct", "difference"]].astype({"rank": str}),
    hide_index=True,
    width="stretch",
    column_config={
        "score": st.column_config.NumberColumn("profile score", format="%.2f"),
        "difference": st.column_config.NumberColumn("difference to target (weighted)", format="%+.2f"),
        "score_pct": st.column_config.NumberColumn("score percentile", format="%.0f"),
        "score_weighted": st.column_config.NumberColumn("profile score (weighted)", format="%.2f"),
        "score_weighted_pct": st.column_config.NumberColumn("profile percentile (weighted)", format="%.0f"),
    },
)
st.caption(
    f"Source: data/derived/{benchmarks_path.name}. The five highest weighted profile scores of the role in all "
    "competitions, with the chosen player in the first row. Profile score: built on z-scores within competition, "
    "so it says how far a player is above his own league. Weighted: corrected for league strength with the Opta "
    f"power rating ({points_per_z:g} rating points per z-score); its percentile is over all competitions together."
)
