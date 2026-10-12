"""Plotly chart helpers matching the design system. Requires: plotly, numpy, pandas.
    from src.viz import charts  # sets the default Plotly template to "sc_dark"
    st.plotly_chart(charts.radar(...), width="stretch")
"""
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

INK = dict(i950="#101210", i900="#161917", i850="#1c1f1d", i800="#232624", i750="#2a2e2b", i700="#323733",
           i600="#424843", i500="#5d645e", i400="#858c86", i300="#aab0ab", i200="#cfd3d0", i50="#f5f6f5")
GREEN, GLOW = "#1fd655", "#4cf07a"
SERIES = ["#1fd655", "#33c3e8", "#f2b33d", "#f2665c", "#a191f2", "#aab0ab"]
BODY, MONO, DISPLAY = "IBM Plex Sans", "IBM Plex Mono", "Saira"


def pct_color(p):
    return "#1fd655" if p >= 80 else "#8fdc4a" if p >= 60 else "#f2c53d" if p >= 40 else "#f2913f" if p >= 20 else "#f2665c"


def _rgba(hex_, a):
    h = hex_.lstrip("#"); return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"


pio.templates["sc_dark"] = go.layout.Template(layout=dict(
    paper_bgcolor=INK["i850"], plot_bgcolor=INK["i850"], colorway=SERIES,
    font=dict(family=BODY, color=INK["i300"], size=12),
    title=dict(font=dict(family=DISPLAY, size=16, color=INK["i50"]), x=0, xanchor="left"),
    xaxis=dict(gridcolor=INK["i750"], linecolor=INK["i600"], zerolinecolor=INK["i600"], tickfont=dict(family=MONO, size=11, color=INK["i400"]),
               title=dict(font=dict(family=DISPLAY, size=11, color=INK["i300"]))),
    yaxis=dict(gridcolor=INK["i750"], linecolor=INK["i600"], zerolinecolor=INK["i600"], tickfont=dict(family=MONO, size=11, color=INK["i400"]),
               title=dict(font=dict(family=DISPLAY, size=11, color=INK["i300"]))),
    legend=dict(orientation="h", y=-0.15, x=0, font=dict(size=12, color=INK["i300"]), bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor=INK["i800"], bordercolor=INK["i600"], font=dict(family=MONO, size=12, color=INK["i50"])),
    margin=dict(l=48, r=16, t=40, b=40),
    polar=dict(bgcolor=INK["i850"]),
))
pio.templates.default = "sc_dark"


def _cap(s):  # uppercase tracked axis titles
    return s.upper() if s else s


# ---------------------------------------------------------------- Radar
def radar(axes, series, show_values=True, height=420):
    """axes: list[str]; series: list[dict(name, values[0-100], color?, dashed?)] — first = subject."""
    fig = go.Figure()
    for i, s in enumerate(series):
        c = s.get("color", SERIES[i % len(SERIES)])
        r = list(s["values"]) + [s["values"][0]]
        fig.add_trace(go.Scatterpolar(
            r=r, theta=list(axes) + [axes[0]], name=s["name"], mode="lines+markers",
            line=dict(color=c, width=2.2 if i == 0 else 1.5, dash="dash" if s.get("dashed") else "solid"),
            marker=dict(size=6, color=c, line=dict(color=INK["i950"], width=1)),
            fill="toself", fillcolor=_rgba(c, .2 if i == 0 else .08),
            hovertemplate="%{theta}: p%{r:.0f}<extra>" + s["name"] + "</extra>"))
    tick_text = [f"{a.upper()}<br><span style='font-family:{MONO};color:{GREEN}'>{round(v)}</span>" for a, v in zip(axes, series[0]["values"])] if show_values else [a.upper() for a in axes]
    fig.update_layout(height=height, showlegend=len(series) > 1, polar=dict(
        radialaxis=dict(range=[0, 100], tickvals=[25, 50, 75, 100], showticklabels=False, gridcolor=INK["i700"], linecolor=INK["i700"], griddash="dot"),
        angularaxis=dict(tickvals=list(axes), ticktext=tick_text, gridcolor=INK["i700"], linecolor=INK["i700"], rotation=90, direction="clockwise",
                         tickfont=dict(family=DISPLAY, size=11, color=INK["i300"]))))
    return fig


# ---------------------------------------------------------------- Distribution (dot strip, multiple metrics)
HL_COLORS = ["#ffffff", "#33c3e8", "#f2b33d"]


def distribution(metrics, peer_label="Other players", subject_labels=None, row_height=62, show_axis=True):
    """metrics: list[dict(label, values, highlight? | highlights?: [dict(value, label?, color?)], unit?, invert?)].
    One row per metric on a shared single line: peers = translucent green dots, values of interest = hexagons.
    Each row is centred on the peer mean and scaled by its max deviation, so left = worse, right = better."""
    fig = go.Figure()
    n = len(metrics)
    for i, m in enumerate(metrics):
        y = n - 1 - i
        v = np.asarray(m["values"], dtype=float)
        hs = m.get("highlights") or ([{"value": m["highlight"]}] if m.get("highlight") is not None else [])
        allv = np.concatenate([v, [h["value"] for h in hs]]) if hs else v
        mean = v.mean(); dev = np.abs(allv - mean).max() or 1
        sgn = -1 if m.get("invert") else 1
        X = lambda a: sgn * (np.asarray(a, dtype=float) - mean) / dev
        fig.add_shape(type="line", x0=-1.08, x1=1.08, y0=y, y1=y, line=dict(color=INK["i700"], width=1), layer="below")
        fig.add_trace(go.Scatter(x=X(v), y=np.full(len(v), y), mode="markers", showlegend=(i == 0), name=peer_label, legendgroup="peers",
                                 marker=dict(size=13, color=_rgba(GREEN, .28), line=dict(width=0)),
                                 customdata=v, hovertemplate=m["label"] + ": %{customdata:,.2f}<extra></extra>"))
        vals_txt = ""
        for j, h in enumerate(hs):
            c = h.get("color", HL_COLORS[j % 3])
            name = h.get("label") or (subject_labels[j] if subject_labels and j < len(subject_labels) else f"Selected {j + 1}")
            fig.add_trace(go.Scatter(x=X([h["value"]]), y=[y], mode="markers", name=name, legendgroup=f"h{j}", showlegend=(i == 0),
                                     marker=dict(symbol="hexagon", size=24, color=c, line=dict(color=INK["i950"], width=1.5)),
                                     hovertemplate=f"{name} · {m['label']}: {h['value']:,.2f}<extra></extra>"))
            vals_txt += f" <span style='color:{INK['i500']}'>·</span> <span style='font-family:{MONO};color:{c}'>{h['value']:,.2f}</span>"
        unit = f" ({m['unit']})" if m.get("unit") else ""
        fig.add_annotation(x=0, y=y + 0.42, text=f"{m['label']}{unit}{vals_txt}", showarrow=False, xanchor="center",
                           font=dict(family=BODY, size=13, color=INK["i300"]))
    if show_axis:
        for x, t, xa in [(-1.08, "← Worse", "left"), (0, "Average", "center"), (1.08, "Better →", "right")]:
            fig.add_annotation(x=x, y=-0.75, text=t, showarrow=False, xanchor=xa, font=dict(family=BODY, size=12, color=INK["i400"]))
    fig.update_xaxes(visible=False, range=[-1.12, 1.12])
    fig.update_yaxes(visible=False, range=[-1, n - 0.35])
    fig.update_layout(height=row_height * n + 110, margin=dict(l=16, r=16, t=16, b=16),
                      legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.02, yanchor="top", font=dict(size=13, color=INK["i300"])))
    return fig


# ---------------------------------------------------------------- Bar
def bar(categories, series, unit="", highlight=None, reference=None, reference_label="Avg", stacked=False, horizontal=False, height=340):
    """series: list[dict(name, values, color?)]"""
    fig = go.Figure()
    for i, s in enumerate(series):
        base = s.get("color", SERIES[i % len(SERIES)])
        colors = [base if (highlight is None or c == highlight) else _rgba(base, .35) for c in categories]
        kw = dict(y=categories, x=s["values"], orientation="h") if horizontal else dict(x=categories, y=s["values"])
        fig.add_trace(go.Bar(name=s["name"], marker=dict(color=colors, line=dict(width=0), cornerradius=2), **kw,
                             hovertemplate="%{" + ("y" if horizontal else "x") + "}: %{" + ("x" if horizontal else "y") + ":,.0f} " + unit + "<extra>" + s["name"] + "</extra>"))
    if reference is not None:
        line = dict(color=INK["i200"], width=1, dash="dash")
        (fig.add_vline if horizontal else fig.add_hline)(reference, line=line, annotation_text=f"{reference_label.upper()} {reference:,.0f}",
                                                         annotation_font=dict(family=DISPLAY, size=10, color=INK["i200"]))
    fig.update_layout(height=height, barmode="stack" if stacked else "group", bargap=.3, bargroupgap=.08, showlegend=len(series) > 1)
    if unit:
        (fig.update_xaxes if horizontal else fig.update_yaxes)(title_text=unit)
    if horizontal:
        fig.update_yaxes(autorange="reversed", tickfont=dict(family=BODY, size=12, color=INK["i300"]), showgrid=False)
    else:
        fig.update_xaxes(tickfont=dict(family=BODY, size=12, color=INK["i300"]), showgrid=False)
    return fig


# ---------------------------------------------------------------- Scatter
def scatter(df, x, y, label=None, highlight=None, x_title=None, y_title=None, quadrants=True, quadrant_labels=None, height=460):
    """df: DataFrame; highlight: list of labels (or boolean mask) to emphasise.
    quadrant_labels: [top-right, top-left, bottom-left, bottom-right]."""
    mask = df[label].isin(highlight) if (highlight is not None and label and not hasattr(highlight, "dtype")) else (highlight if highlight is not None else np.zeros(len(df), bool))
    rest, hl = df[~mask], df[mask]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rest[x], y=rest[y], mode="markers", name="Peers", text=rest[label] if label else None,
                             marker=dict(size=8, color=_rgba(INK["i400"], .55), line=dict(color=INK["i900"], width=1)),
                             hovertemplate="%{text}<br>%{x:,.1f} · %{y:,.1f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=hl[x], y=hl[y], mode="markers+text", name="Targets", text=hl[label] if label else None, textposition="middle right",
                             textfont=dict(family=BODY, size=12, color=INK["i50"]),
                             marker=dict(size=12, color=GREEN, line=dict(color=INK["i950"], width=2)),
                             hovertemplate="%{text}<br>%{x:,.1f} · %{y:,.1f}<extra></extra>"))
    if quadrants:
        mx, my = float(df[x].median()), float(df[y].median())
        fig.add_vline(mx, line=dict(color=INK["i500"], width=1, dash="dash"))
        fig.add_hline(my, line=dict(color=INK["i500"], width=1, dash="dash"))
        fig.add_shape(type="rect", x0=mx, x1=float(df[x].max()) * 1.1, y0=my, y1=float(df[y].max()) * 1.1,
                      fillcolor=_rgba(GREEN, .05), line_width=0, layer="below")
        if quadrant_labels and len(quadrant_labels) == 4:
            pos = [(1, 1, "right", "top"), (0, 1, "left", "top"), (0, 0, "left", "bottom"), (1, 0, "right", "bottom")]
            for i, (t, (px, py, xa, ya)) in enumerate(zip(quadrant_labels, pos)):
                fig.add_annotation(text=t.upper(), xref="x domain", yref="y domain", x=px, y=py, xanchor=xa, yanchor=ya, showarrow=False,
                                   font=dict(family=DISPLAY, size=10, color=GREEN if i == 0 else INK["i400"]))
    fig.update_layout(height=height, showlegend=False, xaxis_title=_cap(x_title or x) + " →", yaxis_title=_cap(y_title or y) + " →")
    return fig
