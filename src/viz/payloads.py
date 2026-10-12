"""Payload builders for the HTML visuals.

Every visual takes the same contract (see tech_stack.md):
    {"data": ..., "labels": ..., "colours": [...], "title": str, "options": {...}}
Python builds the payload, the template / component only renders it.
All values are converted to plain Python types so they serialise to JSON.
"""
import math

SERIES = ["#1fd655", "#33c3e8", "#f2b33d", "#f2665c", "#a191f2", "#aab0ab"]
HIGHLIGHT = ["#ffffff", "#33c3e8", "#f2b33d"]
REFERENCE = "#aab0ab"   # grey for league / role averages


def _num(v):
    """numpy / pandas scalar -> float, NaN -> None."""
    if v is None:
        return None
    v = float(v)
    return None if math.isnan(v) else v


def _payload(data, labels, colours, title, **options):
    return {"data": data, "labels": labels, "colours": colours, "title": title or "",
            "options": {k: v for k, v in options.items() if v is not None}}


def radar(axes, series, title="", eyebrow=None, show_values=True, dashed=None, colours=None, height=420, caption=None):
    """axes: list[str]. series: list of (name, values 0-100). First series is the subject.
    dashed: names drawn with a dashed line (e.g. a role average)."""
    data = [{"name": n, "values": [_num(v) for v in vals]} for n, vals in series]
    return _payload(data, list(axes), colours or SERIES[:len(data)], title,
                    eyebrow=eyebrow, show_values=show_values, dashed=dashed or [], height=height, caption=caption)


def distribution(rows, subjects, title="", eyebrow=None, peer_label="Other players", colours=None, caption=None):
    """Dot strip, one row per metric.
    rows: list of dict(label, values, highlights, unit=None, invert=False)
        values: list of numbers, or list of dict(value, name, id) for hover names and click-back
        highlights: one value per subject, same order as `subjects`
        invert: True for lower-is-better metrics (the catalogue's `inverse` column)
    subjects: legend names of the highlighted players."""
    data = []
    for r in rows:
        vals = [{"value": _num(v["value"]), "name": v.get("name", ""), "id": v.get("id")} if isinstance(v, dict) else _num(v)
                for v in r["values"]]
        vals = [v for v in vals if (v["value"] if isinstance(v, dict) else v) is not None]
        data.append({"label": r["label"], "unit": r.get("unit"), "invert": bool(r.get("invert", False)),
                     "values": vals, "highlights": [_num(h) for h in r.get("highlights", [])]})
    return _payload(data, list(subjects), colours or HIGHLIGHT[:len(subjects)], title,
                    eyebrow=eyebrow, peer_label=peer_label, caption=caption)


def bar(categories, series, title="", eyebrow=None, unit=None, highlight=None, reference=None, reference_label="Avg",
        stacked=False, horizontal=False, colours=None, height=320, caption=None):
    """categories: list[str]. series: list of (name, values)."""
    data = [{"name": n, "values": [_num(v) for v in vals]} for n, vals in series]
    return _payload(data, [str(c) for c in categories], colours or SERIES[:len(data)], title,
                    eyebrow=eyebrow, unit=unit, highlight=highlight, reference=_num(reference), reference_label=reference_label,
                    stacked=stacked, horizontal=horizontal, height=height, caption=caption)


def scatter(df, x, y, label, highlight=(), id_col=None, title="", eyebrow=None, x_title=None, y_title=None,
            quadrants=True, quadrant_labels=None, label_all=False, colours=None, height=420, caption=None):
    """df: DataFrame. highlight: values of `label` (or of `id_col`) to emphasise.
    quadrant_labels: [top-right, top-left, bottom-left, bottom-right]."""
    key = id_col or label
    hl = set(highlight)
    data = [{"x": _num(r[x]), "y": _num(r[y]), "label": str(r[label]), "highlight": r[key] in hl,
             "id": (r[id_col].item() if hasattr(r[id_col], "item") else r[id_col]) if id_col else None}
            for _, r in df[[c for c in dict.fromkeys([x, y, label, key])]].dropna(subset=[x, y]).iterrows()]
    return _payload(data, {"x": x_title or x, "y": y_title or y}, colours or [SERIES[0]], title,
                    eyebrow=eyebrow, quadrants=quadrants, quadrant_labels=quadrant_labels, label_all=label_all,
                    height=height, caption=caption)
