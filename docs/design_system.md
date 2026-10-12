# Sports Analytics Design System

A style guide for HTML visuals rendered inside a **Streamlit** web app that presents sports tracking data (physical metrics, XY positions, player/team comparisons). The visual direction is **inspired by https://skillcorner.com/** — dark charcoal surfaces, glowing green pitch-line markings, squared uppercase display type — The SkillCorner wordmark is included because the user supplied it. No other SkillCorner imagery is reproduced.

**Sources:** https://skillcorner.com/ (homepage copy, OG image, accent SVG colours `#00A82F` / `#252525`, Phosphor-style arrow icons). No codebase, Figma or brand files were provided.

**Logo:** supplied by the user — `assets/logo.png` (white "SKILL" + `#33FF6A` "corner", transparent), `logo-on-black.png`, `logo-white.png`. Place on black/ink-950 only; mono white on mid surfaces; mono black on green. Min. width 120px, clear space = cap height. Ensure you have rights to use the SkillCorner mark in your app.

## Index
- `styles.css` — entry point (imports only) → `tokens/fonts.css`, `colors.css`, `typography.css`, `spacing.css`, `base.css`
- `guidelines/` — 16 foundation specimen cards (Colors, Type, Spacing, Brand)
- `components/` — React primitives (see list below), one card per folder
- `ui_kits/streamlit-app/` — click-through analytics app: Player search → Player profile → Match report
- `streamlit/` — drop-in kit for a vanilla Streamlit app: `styling.css` (full widget overrides + `.sc-*` HTML utility classes), `theme.py` (`inject_theme()`, `header()`, `badge()`, `percentile_bars()`), `charts.py` (Plotly template `sc_dark` + `radar()`, `distribution()`, `bar()`, `scatter()`), `app.py` demo, `.streamlit/config.toml`, `assets/` logos
- `assets/` — logo files
- `thumbnail.html`, `SKILL.md`

## Components
- **core/** — `Button`, `Badge`, `Card`, `SectionHeader`, `Icon`
- **forms/** — `TextInput`, `Select`, `Switch`, `Tabs` (underline + segmented)
- **data/** — `MetricCard`, `PercentileBar`, `BarList`, `DataTable`, `PlayerCard`, `PitchPlot`
- **feedback/** — `Callout`
- **charts/** — `RadarChart`, `DistributionPlot`, `BarChart`, `ScatterPlot` (each mirrors a Plotly helper in `streamlit/charts.py`)

No source inventory existed, so this set is authored for the Streamlit context: each maps to a Streamlit primitive it replaces (`st.metric`→MetricCard, `st.dataframe`→DataTable, `st.tabs`→Tabs, `st.info`…→Callout). Intentional additions: `Icon` (wrapper for the Phosphor web font), `PitchPlot` (core visual for XY tracking data).

## Using it in Streamlit
1. Copy the `streamlit/` folder into your app; move `.streamlit/config.toml` to your app root (dark base, green primary for native widgets).
2. At the top of every page: `from theme import inject_theme; inject_theme()` — injects `styling.css` and sets `st.logo`.
3. Visuals: build a payload with `src/viz/payloads.py` and draw it with `src/viz/visuals.show(kind, payload, key=..., interactive=...)`. Exports: `visuals.export(kind, payload, name)`.
4. Custom HTML: `st.markdown(html, unsafe_allow_html=True)` with the `.sc-card`, `.sc-eyebrow`, `.sc-metric`, `.sc-badge`, `.sc-pct`, `.sc-table` classes. For iframe blocks (`components.html`) inline `styling.css` — iframes don't inherit page CSS.
5. `styling.css` targets Streamlit ≥ 1.36 `data-testid` hooks; these can change between Streamlit releases — re-check after upgrades.

## Charts
- Radar: percentiles 0–100, rings at 25/50/75/100 with dashed 50; subject series glows green, comparisons cyan/amber, league average dashed grey. Max 3 series.
- Distribution (dot strip): one row per metric, label centred above with the value(s) of interest after a `·` in their highlight colour. Every peer is a translucent green dot (28%) on a single line — no jitter, no density. Values of interest are glowing hexagons: white (subject), cyan, amber. Rows are centred on the peer mean so the footer reads ← Worse · Average · Better →; use `invert` for lower-is-better metrics. Legend below: dot = peers, hexagon = subject(s).
- Bar: vertical, grouped or stacked; dashed reference line labelled in Saira caps; non-highlighted categories dim to 35–40%. Ranked lists → `BarList` / `bar(horizontal=True)`.
- Scatter: peers grey 55%, targets green with dark outline + label; dashed median quadrants, top-right tinted 5% green and labelled in green.
- Always: ink-850 plot background, ink-750 gridlines, mono tick labels, uppercase Saira axis titles ending in →, no chart titles inside the plot (use the Card title).

## Content fundamentals
- **Voice:** confident, expert, data-literate. Third person about the data, "you"/"your" to the user only in calls to action ("Unlock the real value of tracking data"). No "we" inside the app UI.
- **Casing:** eyebrows, buttons, tab labels and table headers are UPPERCASE (Saira, tracked). Headlines in Title Case ("Player Search", "Smarter Analysis Across the World's Biggest Sports"); body and descriptions in sentence case.
- **Domain vocabulary, used precisely:** P90 (per 90 minutes), HSR (high-speed running), PSV-99 (top speed), sprints, TIP (time in possession), off-ball runs, extrapolated positions. Always show units: `km`, `m`, `km/h`, `'` for minutes.
- **Numbers:** tabular mono, thousands separators (`2,140`), 1 decimal for speeds/km, integers for metres. Deltas as `▲ 3.1%` / `▼ 0.8`.
- **Brevity:** labels ≤ 3 words; descriptions one sentence stating scope ("Physical output per 90 minutes, min. 600'."). Caveats are stated plainly ("Off-camera positions are extrapolated.").
- **Emoji:** never. Unicode only for ▲ ▼ ↑ ↓ · and the minute mark '.

## Visual foundations
- **Colour:** dark-first. App bg `ink-900 #161917`, sidebar `ink-950`, cards `ink-850`, raised `ink-800`. Neutrals carry a faint green tint. One accent: `green-400 #1fd655` (UI) / `green-500 #00a82f` (reference brand green, use on light backgrounds). `green-300 #4cf07a` is the glow tone for pitch lines only. Data series ordered green → cyan → amber → coral → violet → grey. Home = green, away = cyan. Percentiles use a 5-step coral→green ramp.
- **Type:** Saira (display: headlines, eyebrows, buttons, labels — uppercase with 0.06–0.14em tracking), IBM Plex Sans (body/table text), IBM Plex Mono (every number). Display sizes 48/32/24/18; body 14; small 12–13; eyebrow 11.
- **Spacing:** 4px base (4, 8, 12, 16, 20, 24, 32, 40, 48, 64). Cards pad 20px; grids gap 12–16px; page padding 48px; content max 1280px.
- **Backgrounds:** flat dark surfaces. The only "imagery" is the pitch-line motif — 1–1.5px green lines with a 6px glow on a radial-darkened pitch (`#1f2621 → #141a16`). No gradients elsewhere, no textures, no photos inside the app. Marketing-style heroes may use full-bleed sport photography (desaturated, dark, green-graded) — supply your own.
- **Corners:** small and squared — 2px badges, 4px buttons/inputs, 6px cards, 10px max. Pills only for switches.
- **Borders:** 1px `ink-750` on cards; `ink-700` on inputs; `ink-600` strong. Accent borders only on focus or the one highlighted card.
- **Shadows:** cards get a soft dark drop (`--shadow-card`) plus a 3% inner top highlight; popovers `--shadow-pop`. Glow (`--glow-accent`, `--glow-line`) is reserved for the accent: highlighted card, highlighted bar, pitch lines.
- **Cards:** ink-850 fill, 1px subtle border, 6px radius, optional green eyebrow + Saira title header with right-aligned actions.
- **Hover:** surfaces lighten one step (`surface-hover`); primary button lightens to green-300; secondary gains accent border + 12% green fill; trailing arrow icons nudge 2px right.
- **Press:** primary darkens to green-600 and shifts down 1px. No scaling.
- **Focus:** green border + 3px 12%-green ring on inputs; `--focus-ring` elsewhere.
- **Selection:** 12% green fill + 2px inset green left bar (table rows, sidebar nav).
- **Motion:** ease-out `cubic-bezier(.2,.7,.2,1)`; 120ms hover, 200ms toggles/tabs, 400ms bar fills. No bounce, no parallax.
- **Transparency/blur:** only 12% tinted status backgrounds and the glow. No glassmorphism.
- **Layout:** Streamlit shell — fixed 264px left sidebar (nav + filters), centred content column. KPI row of 4 MetricCards on top, then a 2:1 or 1.6:1 grid of cards.

## Iconography
- In this project the Phosphor web font is not loaded (no CDN on the club network, and the app uses no icons). To use icons, bundle `Phosphor.woff2` in `static/fonts/` and add only the classes you need.
- **Phosphor Icons** (regular weight; fill for emphasis). The reference site's arrow glyphs are Phosphor `arrow-right`. Use `<Icon name="…" />` or `<i class="ph ph-funnel">`.
- 16px in controls, 18–20px standalone; colour inherits text, accent green for directional CTAs.
- Common: `magnifying-glass`, `funnel`, `sliders-horizontal`, `download-simple`, `arrow-right`, `arrow-left`, `soccer-ball`, `user`, `chart-bar`, `lightning`, `map-trifold`, `warning`, `info`, `check-circle`.
- No emoji. No PNG icons. No custom SVG icons — the PitchPlot is a chart, not an icon.

## Fonts
Open substitutes (SIL OFL), bundled as woff2 in `static/fonts/` and loaded locally — the reference wordmark/headlines use a proprietary squared face. **Saira** is the nearest open match; swap in licensed files via `@font-face` in `static/fonts/fonts.css` and `static/styling.css` if you have them.

In the Streamlit app the fonts are set in `.streamlit/config.toml` (`font`, `headingFont`, `codeFont`, `[[theme.fontFaces]]`). In `static/styling.css`, never force a font, size or weight on all children of an element (`X *`): Streamlit's icons are text in an icon font and would show their name instead. Style the element itself or its text (`X p`).
