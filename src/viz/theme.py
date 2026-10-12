"""Inject styling.css + small HTML helpers. Call inject_theme() once at the top of each page."""
from pathlib import Path
import streamlit as st

STATIC = Path(__file__).parents[2] / "static"
CSS_PATH = STATIC / "styling.css"
LOGO = STATIC / "assets" / "logo.png"          # white + green wordmark, transparent
LOGO_WHITE = STATIC / "assets" / "logo-white.png"


def _css() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def inject_theme(logo: bool = True):
    st.markdown(f"<style>{_css()}</style>", unsafe_allow_html=True)
    if logo and LOGO.exists():
        st.logo(str(LOGO), size="large")


def header(title: str, eyebrow: str = "", description: str = ""):
    eb = f'<div class="sc-eyebrow">{eyebrow}</div>' if eyebrow else ""
    ds = f'<p class="sc-desc">{description}</p>' if description else ""
    st.markdown(f'{eb}<h2 class="sc-title">{title}</h2>{ds}', unsafe_allow_html=True)


def badge(text: str, tone: str = "accent") -> str:
    return f'<span class="sc-badge {tone}">{text}</span>'


def pct_color(p: float) -> str:
    return "#1fd655" if p >= 80 else "#8fdc4a" if p >= 60 else "#f2c53d" if p >= 40 else "#f2913f" if p >= 20 else "#f2665c"


def percentile_bars(rows):
    """rows: iterable of (label, percentile, value_text)."""
    html = "".join(
        f'<div class="sc-pct"><div><div style="font-size:13px">{l}</div>'
        f'<div class="sc-num" style="font-size:11px;color:var(--ink-400)">{v}</div></div>'
        f'<div class="track"><span class="fill" style="width:{p}%;background:{pct_color(p)}"></span></div>'
        f'<div class="rank" style="color:{pct_color(p)}">{round(p)}</div></div>'
        for l, p, v in rows
    )
    st.markdown(html, unsafe_allow_html=True)
