"""Metric catalogue: every metric of the raw files, by category, with its stored details."""

import streamlit as st

from src.data.catalogue import (
    BEST_X,
    CALCULATIONS,
    PER,
    add_metric,
    load_catalogue,
    name_taken,
    rebuild_catalogue,
)
from src.data.inventory import METRIC_FILES
from src.data.loaders import save_catalogue_file
from src.viz.theme import inject_theme

EDITABLE = ["calculation", "per", "weight", "match_filter", "inverse"]
# Calculations of raw metrics; the average of best x is only for calculated metrics.
RAW_CALCULATIONS = [c for c in CALCULATIONS if c != BEST_X]
CALCULATED_COLUMNS = ["file", "metric", "source", "calculation", "best_x", "weight", "match_filter", "inverse"]
CALCULATED_EDITABLE = ["best_x", "match_filter", "inverse"]

st.set_page_config(page_title="Metric Catalogue", layout="wide")
inject_theme()
st.title("Metric Catalogue")
st.caption(
    "Every metric in the raw files, and the metrics calculated from them. Stored in "
    "data/metric_catalogue.csv; the season calculations read their settings from this file."
)

catalogue = load_catalogue()
raw = catalogue[catalogue["origin"] == "raw"]
calculated = catalogue[catalogue["origin"] == "custom"]

with st.sidebar:
    st.header("Filters")
    st.caption("For the general catalogue.")
    categories = st.multiselect("Category", sorted(raw["category"].unique()))
    in_category = raw[raw["category"].isin(categories)] if categories else raw
    files = st.multiselect("File", sorted(in_category["file"].unique()))
    calculations = st.multiselect("Calculation", RAW_CALCULATIONS)
    inverse = st.selectbox("Lower is better", ["All", "Yes", "No"])
    full_only = st.checkbox("Full match only", value=True, help="Hide the first-half and second-half physical metrics.")

view = in_category
if files:
    view = view[view["file"].isin(files)]
if calculations:
    view = view[view["calculation"].isin(calculations)]
if inverse != "All":
    view = view[view["inverse"] == (inverse == "Yes")]
if full_only:
    view = view[view["scope"] == "full"]

tab_general, tab_calculated = st.tabs(["General catalogue", "Calculated season metrics"])

with tab_general:
    search = st.text_input(
        "Search the table",
        placeholder="For example: regain pressing high block",
        help="Searches category, file, metric name, type and definition. With several words, all of them "
        "have to be found; an underscore in a name counts as a space.",
    )
    if search:
        text = view[["category", "file", "metric", "type", "definition"]].fillna("").agg(" ".join, axis=1)
        text = text.str.replace("_", " ").str.lower()
        for word in search.lower().replace("_", " ").split():
            view = view[text.loc[view.index].str.contains(word, regex=False)]

    m1, m2, m3 = st.columns(3)
    m1.metric("Metrics shown", len(view))
    m2.metric("Lower is better", int(view["inverse"].sum()))
    m3.metric("Metrics in catalogue", len(raw))

    with st.expander("What the calculation types mean"):
        for name in RAW_CALCULATIONS:
            st.write(f"{name}: {CALCULATIONS[name]}.")
        st.write(
            "per: the minutes a match total is divided by (30 minutes in possession, 30 minutes out "
            "of possession, or 90 match minutes). weight: the column an average or ratio "
            "is weighted by or divided by. match filter: if ticked, only matches in which the "
            "player has the minimum minutes (set on the main page, default 60) count for the season "
            "value; best values (max, min) use every match by default."
        )

    edited = st.data_editor(
        view,
        hide_index=True,
        width="stretch",
        disabled=[c for c in view.columns if c not in EDITABLE],
        column_config={
            "calculation": st.column_config.SelectboxColumn(options=RAW_CALCULATIONS, required=True),
            "per": st.column_config.SelectboxColumn(options=["", *PER]),
            "match_filter": st.column_config.CheckboxColumn(
                "match filter",
                help="Ticked: only matches with enough minutes count. Unticked: every match counts.",
            ),
            "inverse": st.column_config.CheckboxColumn("lower is better"),
            "source": None,
            "origin": None,
            "best_x": None,
        },
    )
    st.caption(
        "calculation, per, weight, match filter and lower is better can be edited. Save before changing a filter; "
        "unsaved edits are lost when the filter changes."
    )

    c1, c2 = st.columns([1, 5])
    if c1.button("Save", type="primary"):
        catalogue.loc[edited.index, EDITABLE] = edited[EDITABLE].fillna("")
        save_catalogue_file(catalogue)
        st.success("Saved to data/metric_catalogue.csv.")
    with c2.popover("Rebuild from rules"):
        st.write(
            "This discards all saved edits and rebuilds the catalogue from the naming rules. "
            "Calculated season metrics are kept."
        )
        if st.button("Discard edits and rebuild"):
            save_catalogue_file(rebuild_catalogue())
            st.rerun()

with tab_calculated:
    st.caption(
        "Metrics we define ourselves: a new name that reads a metric of the general catalogue "
        "and has its own season calculation. They can be picked in the Metric check tab of the "
        "main page like any other metric."
    )
    st.write(
        f"{BEST_X}: {CALCULATIONS[BEST_X]}. A player with fewer than x matches gets the mean "
        f"of the matches there are. ratio: {CALCULATIONS['ratio']}, as a fraction from 0 to 1."
    )

    if calculated.empty:
        st.info("No calculated metrics yet. Add one below.")
    else:
        edited_calculated = st.data_editor(
            calculated[CALCULATED_COLUMNS],
            hide_index=True,
            width="stretch",
            disabled=[c for c in CALCULATED_COLUMNS if c not in CALCULATED_EDITABLE],
            column_config={
                "source": "source metric",
                "best_x": st.column_config.NumberColumn("best x matches", min_value=0, step=1, required=True),
                "match_filter": st.column_config.CheckboxColumn("match filter"),
                "inverse": st.column_config.CheckboxColumn("lower is better"),
            },
        )
        st.caption("best x matches, match filter and lower is better can be edited. best x is only used by the average of best x.")
        c1, c2 = st.columns([1, 5])
        if c1.button("Save", type="primary", key="save_calculated"):
            catalogue.loc[edited_calculated.index, CALCULATED_EDITABLE] = edited_calculated[CALCULATED_EDITABLE]
            save_catalogue_file(catalogue)
            st.success("Saved to data/metric_catalogue.csv.")
        with c2.popover("Delete metrics"):
            labels = calculated["file"] + " / " + calculated["metric"]
            chosen = st.multiselect("Calculated metrics to delete", labels.tolist())
            if st.button("Delete", disabled=not chosen):
                save_catalogue_file(catalogue.drop(index=labels.index[labels.isin(chosen)]))
                st.rerun()

    st.subheader("Add metric")
    c1, c2, c3 = st.columns(3)
    file = c1.selectbox("File", list(METRIC_FILES), key="new_file")
    in_file = raw.loc[raw["file"] == file].set_index("metric")
    source = c2.selectbox("Source metric", in_file.index.tolist())
    calculation = c3.selectbox("Calculation", [BEST_X, "ratio"], key="new_calculation")

    c1, c2, c3 = st.columns(3)
    if calculation == BEST_X:
        best_x = c1.number_input("Best x matches", min_value=1, value=3, step=1)
        weight = ""
        default_name = f"{source}_best{best_x}"
    else:
        weight = c1.selectbox("Divided by", in_file.index.tolist(), help="A metric of the same file.")
        best_x = 0
        default_name = f"{source}_ratio"
    name = c2.text_input("Name of the new metric", value=default_name).strip()
    match_filter = c3.checkbox(
        "Match filter",
        value=calculation != BEST_X,
        help="Ticked: only matches with enough minutes count. Unticked: every match counts.",
    )
    inverse = c3.checkbox("Lower is better", value=bool(in_file.at[source, "inverse"]))

    if st.button("Add metric", type="primary"):
        if not name.replace("_", "").isalnum():
            st.error("Use only letters, digits and underscores in the name.")
        elif name_taken(catalogue, file, name):
            st.error(f"{name} already exists for this file. Choose another name.")
        else:
            save_catalogue_file(
                add_metric(catalogue, file, name, source, calculation, weight, int(best_x), match_filter, inverse)
            )
            st.rerun()
