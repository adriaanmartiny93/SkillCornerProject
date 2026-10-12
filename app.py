"""SkillCorner Replacement Finder - Streamlit entry point (Step 0: data foundation)."""

import pandas as pd
import streamlit as st

from src.data import foundation, loaders
from src.data.catalogue import CALCULATIONS, metric_specs
from src.data.inventory import METRIC_FILES, inventory
from src.data.roles import role_positions, save_role_positions
from src.viz.theme import inject_theme

cached_inventory = st.cache_data(inventory)
cached_player_matches = st.cache_data(foundation.player_matches)
cached_load_derived = st.cache_data(loaders.load_derived)
cached_match_values = st.cache_data(foundation.match_values)

st.set_page_config(page_title="SkillCorner Replacement Finder", layout="wide")
inject_theme()
st.title("SkillCorner Replacement Finder")
st.caption("Step 0: data foundation.")

with st.sidebar:
    st.header("Player pipeline")
    min_match_minutes = st.number_input(
        "Minimum minutes per match",
        min_value=0,
        value=foundation.DEFAULT_MIN_MATCH_MINUTES,
        step=5,
        help="A match only counts for season aggregates if the player has at least this many "
        "minutes in it. Metrics without the match filter in the catalogue (max, min) use every match.",
    )
    min_matches = st.number_input(
        "Minimum matches",
        min_value=0,
        value=foundation.DEFAULT_MIN_MATCHES,
        step=1,
        help="Players with fewer included matches in a role are flagged as low sample. "
        "They are not hidden.",
    )
    if st.button("Recalculate", type="primary"):
        path = foundation.run_player_pipeline(min_match_minutes, min_matches)
        st.success(f"Written: data/derived/{path.name}")

tab_players, tab_check, tab_roles, tab_files = st.tabs(
    ["Players", "Metric check", "Role mapping", "File inventory"]
)

path = loaders.latest_derived("player_seasons")
seasons = cached_load_derived(path) if path else None
if seasons is not None and "min_match_minutes" not in seasons:
    # Written before the match filter existed.
    seasons = None

with tab_players:
    if seasons is None:
        st.info("No player table yet. Press Recalculate in the sidebar.")
    else:
        st.caption(
            f"Source: data/derived/{path.name}. "
            f"Settings used: at least {seasons['min_match_minutes'].iloc[0]:g} minutes per match, "
            f"at least {seasons['min_matches'].iloc[0]:g} matches. "
            "One row per player, team, competition and role."
        )
        c1, c2, c3, c4 = st.columns(4)
        competitions = c1.multiselect("Competition", sorted(seasons["competition_name"].unique()))
        teams = c2.multiselect("Team", sorted(seasons["team_name"].unique()))
        roles = c3.multiselect("Role", list(role_positions()))
        sample = c4.selectbox("Sample", ["All", "Enough matches", "Low sample"])

        view = seasons
        if competitions:
            view = view[view["competition_name"].isin(competitions)]
        if teams:
            view = view[view["team_name"].isin(teams)]
        if roles:
            view = view[view["role"].isin(roles)]
        if sample != "All":
            view = view[view["low_sample"] == (sample == "Low sample")]

        m1, m2, m3 = st.columns(3)
        m1.metric("Rows", len(view))
        m2.metric("Low sample", int(view["low_sample"].sum()))
        m3.metric("Players", view["player_id"].nunique())
        st.dataframe(
            view.drop(columns=["competition_edition_id", "team_id", "min_match_minutes", "min_matches"]),
            hide_index=True,
            width="stretch",
        )

with tab_check:
    if seasons is None:
        st.info("No player table yet. Press Recalculate in the sidebar.")
    else:
        st.caption(
            "Pick one metric to see how its season value is built. The calculation comes from "
            "the Metric Catalogue page. z-score and percentile are within competition and role; "
            "low-sample players are left out of the reference but still get a score."
        )
        c1, c2, c3 = st.columns([1, 2, 2])
        name = c1.selectbox("File", list(METRIC_FILES))
        specs = metric_specs(name)
        options = specs.index[specs["scope"] == "full"].tolist()
        metric = c2.selectbox("Metric", options)
        other = c3.selectbox(
            "Compare with",
            [m for m in options if m != metric],
            index=None,
            help="Optional: a second metric of the same file. Its season value is added as a column.",
        )
        metrics = [metric, other] if other else [metric]
        spec = specs.loc[metric]
        st.write(
            f"Calculation: {spec['calculation']} - {CALCULATIONS[spec['calculation']]}. "
            f"Match filter: {'yes' if spec['match_filter'] else 'no, every match counts'}. "
            f"Lower is better: {'yes' if spec['inverse'] else 'no'}."
        )
        used_minutes = seasons["min_match_minutes"].iloc[0]

        values = cached_match_values(name, metrics, cached_player_matches())
        rate = foundation.rate_column(name, metric)
        rates = foundation.season_rates(values, name, metrics, used_minutes)
        rates = rates.merge(
            seasons[[*foundation.SEASON_KEYS, "low_sample"]], on=foundation.SEASON_KEYS
        )
        rates = foundation.standardise(rates, [rate])

        st.dataframe(
            rates.drop(columns=["competition_edition_id", "team_id"]).sort_values(rate, ascending=False),
            hide_index=True,
            width="stretch",
        )
        st.caption(
            f"Minimum minutes per match: {used_minutes:g}, taken from the player table. Only "
            "matches covered by this file are counted, so the number of included matches can be "
            "lower than in the Players tab. z-scores are not flipped for lower-is-better metrics."
        )

        st.subheader("Match rows for one player")
        players = rates.sort_values("player_name")
        labels = players["player_name"] + " - " + players["team_name"] + " - " + players["role"]
        choice = st.selectbox("Player", labels.tolist())
        row = players[labels == choice].iloc[0]
        rows = values[
            (values["player_id"] == row["player_id"])
            & (values["team_id"] == row["team_id"])
            & (values["role"] == row["role"])
        ].sort_values("match_date")
        rows = rows.assign(included=rows[foundation.MINUTES["all"]] >= used_minutes)
        # Minutes for totals, the weight column for averages and ratios.
        if spec["per"]:
            support = [foundation.MINUTES[foundation.PER[spec["per"]][0]]]
        else:
            support = [spec["weight"]] if spec["weight"] else []
        match_columns = ["match_date", "position", foundation.MINUTES["all"], "included", *support, metric, rate]
        match_columns = [c for c in dict.fromkeys(match_columns) if c in rows]
        st.dataframe(rows[match_columns], hide_index=True, width="stretch")
        st.write(f"Season value ({rate}): {row[rate]:.3f}.")

with tab_roles:
    st.caption(
        "Benchmarks and similarity are calculated within a role group. Change the positions of a "
        "role, or add or remove a role (rows can be added at the bottom of the table). Players in "
        "a position that is in no role are left out of the player table."
    )
    positions = sorted(cached_player_matches()["position"].unique())
    edited_roles = st.data_editor(
        pd.DataFrame({"role": role, "positions": positions_} for role, positions_ in role_positions().items()),
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "role": st.column_config.TextColumn(required=True),
            "positions": st.column_config.MultiselectColumn(options=positions),
        },
    )
    mapping = {
        str(role).strip(): list(chosen) if hasattr(chosen, "__iter__") and not isinstance(chosen, str) else []
        for role, chosen in zip(edited_roles["role"], edited_roles["positions"])
        if str(role).strip() not in ("", "None", "nan")
    }
    used = [position for chosen in mapping.values() for position in chosen]
    unused = [position for position in positions if position not in used]
    double = sorted({position for position in used if used.count(position) > 1})
    if unused:
        st.warning("Positions not in a role: " + ", ".join(unused) + ".")
    else:
        st.write("Positions not in a role: none.")
    if double:
        st.error("In more than one role: " + ", ".join(double) + ". A position can only be in one role.")
    if len(mapping) < len(edited_roles):
        st.error("Two rows have the same role name, or a row has no name.")
    if st.button("Save role mapping", disabled=bool(double) or len(mapping) < len(edited_roles)):
        save_role_positions(mapping)
        cached_player_matches.clear()
        cached_match_values.clear()
        foundation.run_player_pipeline(min_match_minutes, min_matches)
        st.rerun()
    st.caption(
        "Saving writes data/role_mapping.csv and recalculates the player table with the settings in "
        "the sidebar. Benchmarks have to be recalculated on the Benchmarks page; profiles of a role "
        "that was renamed or removed have to be saved again under the new role."
    )

with tab_files:
    st.caption("The raw CSVs in data/raw/. These files are never modified.")
    st.dataframe(cached_inventory(), hide_index=True, width="stretch")
