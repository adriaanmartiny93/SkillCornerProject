"""Render the HTML visuals in Streamlit and export them as standalone reports.

    from src.viz import payloads, visuals
    visuals.show("radar", payloads.radar(...))                         # display-only
    pick = visuals.show("scatter", payloads.scatter(...), key="s", interactive=True)   # returns the clicked item
    path = visuals.export("radar", payload, "team_radar")             # exports/team_radar_<ts>.html

In the app every visual goes through one static custom component (components/sc_chart/):
ECharts is loaded once and cached by the browser, and clicks can come back to Python.
Exports use the Jinja2 templates in templates/ with ECharts, the chart code and the fonts inlined.
"""
import base64
import re
from datetime import datetime
from pathlib import Path

import streamlit.components.v1 as components
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parents[2]
COMPONENT = ROOT / "components" / "sc_chart"
TEMPLATES = ROOT / "templates"
FONTS = ROOT / "static" / "fonts"
EXPORTS = ROOT / "exports"
KINDS = ("radar", "distribution", "bar", "scatter")

_component = components.declare_component("sc_chart", path=str(COMPONENT))
_env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]))


def show(kind, payload, key=None, interactive=False):
    """Draw a visual. Returns the clicked item as a dict when interactive (None until a click), else None.
    The frame height follows the content; set the chart height in the payload options."""
    if kind not in KINDS:
        raise ValueError(f"Unknown visual '{kind}'. Use one of {KINDS}.")
    value = _component(kind=kind, payload=payload, interactive=interactive, key=key, default=None)
    return value if interactive else None


def _script(path):
    # Keep inlined JS from closing the <script> tag early.
    return path.read_text(encoding="utf-8").replace("</script", "<\\/script")


def _fonts_inline():
    css = (FONTS / "fonts.css").read_text(encoding="utf-8")

    def data_uri(m):
        data = base64.b64encode((FONTS / m.group(1)).read_bytes()).decode()
        return f'url("data:font/woff2;base64,{data}")'

    return re.sub(r'url\("([^"/]+\.woff2)"\)', data_uri, css)


def render_standalone(kind, payload, source=None, width=960):
    """Full HTML document with everything inlined (no network needed)."""
    return _env.get_template(f"{kind}.html").render(
        kind=kind, payload=payload, source=source, width=width,
        generated=datetime.now().strftime("Generated %d %b %Y, %H:%M"),
        fonts_css=_fonts_inline(),
        echarts_js=_script(COMPONENT / "echarts.min.js"),
        sc_charts_js=_script(COMPONENT / "sc_charts.js"),
    )


def export(kind, payload, name, source=None):
    """Write a standalone HTML report to exports/<name>_<timestamp>.html and return the path."""
    EXPORTS.mkdir(exist_ok=True)
    path = EXPORTS / f"{name}_{datetime.now().strftime('%Y-%m-%dT%H%M%S')}.html"
    path.write_text(render_standalone(kind, payload, source=source), encoding="utf-8")
    return path
