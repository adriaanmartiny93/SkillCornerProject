"""Design demo: the theme and the four HTML visuals with made-up data. Remove once real visuals exist."""
import numpy as np
import pandas as pd
import streamlit as st

from src.viz import payloads, visuals
from src.viz.theme import badge, header, inject_theme, percentile_bars

st.set_page_config(page_title="Design Demo", layout="wide")
inject_theme()

with st.sidebar:
    st.header("Filters")
    st.selectbox("Season", ["2026/27", "2025/26"])
    st.selectbox("Role", ["CM", "CB", "W", "CF"])
    st.slider("Min. minutes", 0, 3000, 600, step=100)
    st.toggle("U23 only")

header("Lucas Moreau", eyebrow="Design demo · made-up data", description="Every visual below is an HTML template in an iframe. Click the scatter or the dots to send a selection back to Python.")
st.markdown(badge("CM") + " " + badge("FRA", "info") + " " + badge("Low sample", "warning"), unsafe_allow_html=True)
st.write("")

c = st.columns(4)
c[0].metric("Distance P90", "11.42 km", "+3.1%")
c[1].metric("HSR P90", "742 m", "+5.0%")
c[2].metric("Sprints P90", "21.4", "-0.8")
c[3].metric("PSV-99", "33.9 km/h")

rng = np.random.default_rng(7)
axes = ["Distance", "HSR", "Sprints", "PSV-99", "Accels", "Pressing"]
radar = payloads.radar(axes, [("L. Moreau", [92, 88, 63, 34, 71, 81]), ("Role average", [50] * 6)],
                       title="Physical profile", eyebrow="Radar", dashed=["Role average"],
                       colours=[payloads.SERIES[0], payloads.REFERENCE])

names = [f"Player {i}" for i in range(18)]
def peers(mean, sd):
    return [{"value": v, "name": n, "id": i} for i, (n, v) in enumerate(zip(names, rng.normal(mean, sd, len(names))))]
dist = payloads.distribution([
    {"label": "Total distance P90", "unit": "km", "values": peers(10.6, .9), "highlights": [11.42, 10.61]},
    {"label": "HSR distance P90", "unit": "m", "values": peers(640, 160), "highlights": [742, 918]},
    {"label": "Sprint count P90", "values": peers(17, 6), "highlights": [21.4, 31.2]},
    {"label": "Time to recover", "unit": "s", "values": peers(9.5, 1.6), "highlights": [8.2, 10.9], "invert": True},
], subjects=["L. Moreau", "T. Ibarra"], title="Where they sit", eyebrow="Distribution", peer_label="Other CMs")

bars = payloads.bar(["MD4", "MD5", "MD6", "MD7", "MD8"], [("HSR", [690, 742, 812, 701, 766])], title="HSR by match",
                    eyebrow="Bar", unit="m", highlight="MD8", reference=705, reference_label="Season avg", height=280)

df = pd.DataFrame({"player_id": range(60), "player": [f"P{i}" for i in range(60)],
                   "hsr": rng.normal(640, 160, 60), "spr": rng.normal(17, 6, 60)})
df.loc[0, ["player", "hsr", "spr"]] = ["L. Moreau", 742, 21.4]
df.loc[1, ["player", "hsr", "spr"]] = ["T. Ibarra", 918, 31.2]
scat = payloads.scatter(df, "hsr", "spr", label="player", id_col="player_id", highlight=[0, 1], title="HSR vs. sprints",
                        eyebrow="Scatter · interactive", x_title="HSR P90 (m)", y_title="Sprints P90",
                        quadrant_labels=["Elite output", "Sprinters", "Low output", "Volume runners"])

t1, t2, t3 = st.tabs(["Profile", "Benchmarks", "Theme widgets"])
with t1:
    l, r = st.columns(2)
    with l:
        visuals.show("radar", radar, key="radar")
    with r:
        visuals.show("bar", bars, key="bar")
with t2:
    l, r = st.columns([1, 1.2])
    with l:
        clicked = visuals.show("distribution", dist, key="dist", interactive=True)
        st.caption(f"Clicked: {clicked['name'] or '-'} · {clicked['metric']} · {clicked['value']:.2f}" if clicked else "Click a dot.")
    with r:
        picked = visuals.show("scatter", scat, key="scatter", interactive=True)
        st.caption(f"Selected: {picked['label']} (id {picked['id']})" if picked else "Click a point to select a player.")
    if st.button("Export radar as HTML report"):
        path = visuals.export("radar", radar, "demo_radar", source="Design demo, made-up data")
        st.success(f"Written: exports/{path.name}")
with t3:
    with st.container(border=True):
        percentile_bars([("Total distance", 92, "11.42 km"), ("HSR distance", 88, "742 m"), ("Sprint count", 63, "21.4"), ("PSV-99", 34, "33.9 km/h")])
    st.info("Off-camera positions are extrapolated from broadcast video.")
