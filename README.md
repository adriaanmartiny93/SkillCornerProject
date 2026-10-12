# SkillCorner Replacement Finder (Pilot)

A Streamlit proof of concept built on SkillCorner CSV exports. Its purpose is to find transfer targets that can replace specific players within a team.

The pilot keeps the CSV structure as-is. Derived results (benchmarks, importance scores, similarity results) are recalculated on demand through buttons in the app and written back as versioned CSVs.

---

## Goal

1. **Benchmark teams** on playing style and quality.
2. **Measure player importance** within a team.
3. **Find similar players** to replace important players, adjusted for team context.

---

## Project plan

### Step 0 — Data foundation

1. **Inventory the CSVs.** Record the following for each file:
   - the grain (per match or per season)
   - the join keys (player ID, team ID, competition, season, position)
   - which metric families it covers (physical, off-ball runs, passing options, pressure)
2. **Set normalisation rules.**
   - Express metrics per 30 minutes in possession (TIP) or out of possession (OTIP), not only per 90. SkillCorner metrics are strongly context-dependent.
   - Standardise within each competition (z-scores or percentiles).
3. **Set reliability thresholds.** Choose a minimum number of minutes or matches. Flag low-sample players rather than dropping them silently.
4. **Map positions to roles.** Use role groups such as CB, FB/WB, DM, CM, AM, W and CF. Similarity is only computed within a role group.
5. **Store derived outputs separately.**
   - Raw CSVs are never modified.
   - Every recalculation writes timestamped derived CSVs to `data/derived/`.

### Step 0b — Visual layer (built before the analytics)

All visuals are **HTML templates rendered in iframes** and wired into the Streamlit app.

1. **Template library.** There is one Jinja2 HTML template per visual type in `templates/`. A shared base template holds the club styling.
2. **Data contract.** Each template receives a fixed JSON payload:
   - `data`
   - `labels`
   - `colours`
   - `title`
   - `options`

   Python builds the payload and the template only renders it.
3. **One charting library.** Pick a single library (see `tech_stack.md`) and keep it consistent across all templates.
4. **Embedding modes.**
   - **Display-only:** a one-way embed, from Python to the iframe.
   - **Interactive:** a custom bidirectional Streamlit component that sends the selection (team, player, candidate) back to the app. Keep this to one or two visuals in the pilot.
5. **Local assets.** JS libraries and fonts are bundled locally, so the app doesn't depend on a CDN.
6. **Sizing.** Each template has a fixed height, or the base template includes an auto-resize helper.
7. **Export.** Filled templates can be saved as standalone HTML reports for scouts and staff.

### Step 1 — Team benchmarks (style vs quality)

Style and quality are kept on **separate axes**.

- **Style features** describe how a team plays:
  - physical intensity in and out of possession
  - the mix of run types (in behind, overlap, support)
  - pressing intensity and engagement height
  - passing-option and risk tendencies
- **Quality features** describe how successful a team is at what it does, measured in the SkillCorner data itself. Each style dimension is paired with the outcome of the same actions:
  - pressing: regains, disruptions and forced backward play against times beaten (for example, regains per high-block press)
  - passing: completed line-breaking passes against attempts and against expected completion
  - runs: runs that are targeted and received, and the threat (xThreat) they create
- **Example:** "do they press high?" is style; "does the high press win the ball?" is quality.
- **Method:**
  1. Standardise within each competition, then apply a league adjustment.
  2. Reduce correlated metrics with PCA.
  3. Cluster (k-means) into a small set of named style archetypes, named together with staff.
- **Outputs:** a style radar per team, the nearest teams by style, and a style-vs-quality scatter plot.

### Step 2 — Player importance within a team

The importance index combines four components, with weights the user can adjust through sliders:

1. **Availability:** share of minutes, starts and consistency.
2. **Contribution share:** the player's share of the team's output on the key actions for his role.
3. **Style fit:** how strongly the player expresses the team's defining style dimensions from Step 1.
4. **Replaceability:** the distance to the most similar teammate in the same role group.

Validate the resulting ranking against the coaching staff's intuition.

**Outputs:**
- a squad importance chart, split into the four components
- a per-player breakdown card
- a "critical and irreplaceable" flag

### Step 3 — Replacement finder

1. **Features per role.** Use a fixed feature set for each role group.
2. **Weighting.** Boost the target player's signature traits (from Step 2) and the metrics tied to your own team's style (from Step 1).
3. **Context adjustment.** Scale candidates' metrics for their team's style and quality.
4. **Similarity.** Compute a weighted cosine or Euclidean distance on standardised features and scale it to a 0–100 score.
5. **Filters.** League, age and minutes, plus market value and contract status later if external data is added.
6. **Explainability.** For each candidate, show the drivers of similarity, the biggest differences, and an overlay radar against the target.
7. **Shortlist export.** Export the shortlist to CSV or Excel for scouting.

### Step 4 — App structure and validation

- **Pages:** Team Benchmarks → Squad Importance → Replacement Finder. Selections carry forward from one page to the next.
- **Computation:** heavy computations are cached and only rerun when a recalculate button is pressed.
- **Validation:**
  - Back-test against known transfers.
  - Run blind checks with scouts on a few targets.
- **Feedback loop:** users can mark candidates as relevant or not relevant. This feedback is later used to tune the weights.

---

## Visuals per step

| Step | Visual | Mode |
|---|---|---|
| 1 | Team style radar | Display |
| 1 | Style-vs-quality scatter, coloured by archetype | Interactive (select team) |
| 1 | Nearest teams list | Display |
| 2 | Squad importance bars (4 components) | Interactive (select player) |
| 2 | Player breakdown card | Display |
| 3 | Ranked candidate table + similarity score | Interactive (select candidate) |
| 3 | Target-vs-candidate overlay radar | Display |
| 3 | "Why similar / where different" bars | Display |

---

## Build order

1. Data foundation (Step 0)
2. Base template, data contract and the first display template (radar), to prove the iframe setup
3. The first interactive component (scatter), to prove the two-way flow works
4. Steps 1 → 2 → 3, with each step's visuals built alongside its analytics
5. Export and validation

---

## Open decisions

- **League adjustment:** the method for comparing across leagues. This is the largest source of misleading comparisons.
- **Weight ownership:** who sets the importance and similarity weights — the analysts by default, or the staff through sliders.
- **Minimum sample:** the threshold below which a player is hidden rather than flagged.

---

## Proposed folder structure

```
.
├── app.py                  # Streamlit entry point
├── .streamlit/config.toml  # dark base theme, green primary colour
├── pages/                  # 0_Metric_Catalogue, 1_Benchmarks, 2_Profile_Builder, 9_Design_Demo; later Team_Benchmarks, Squad_Importance, Replacement_Finder
├── src/
│   ├── data/               # loading, joining, normalisation, role mapping
│   ├── benchmarks/         # engine.py (percentile, z-score, profile score), profiles.py (profiles, correlations); later team style/quality, PCA, clustering
│   ├── importance/         # importance index components
│   ├── similarity/         # feature sets, weighting, distance, explainability
│   └── viz/                # theme.py (inject_theme, HTML helpers), payloads.py (payload builders), visuals.py (show, export), charts.py (older Plotly helpers)
├── templates/              # Jinja2 HTML templates (base + one per visual)
├── components/             # sc_chart/: the chart component (index.html, sc_charts.js, ECharts 5.5.1)
├── static/                 # styling.css (Streamlit theme), styles.css + tokens/ (design tokens), assets/ (logos), fonts/ (local webfonts)
├── data/
│   ├── raw/                # SkillCorner CSVs (never modified)
│   └── derived/            # versioned recalculation outputs
├── exports/                # HTML reports and shortlists
├── docs/                   # design_system.md (style guide), activity.md (log)
├── requirements.txt
├── README.md
└── tech_stack.md
```

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Put the SkillCorner CSVs in `data/raw/` before you start the app.

## Design system

The look of the app follows `docs/design_system.md`. Every page calls `inject_theme()` from `src/viz/theme.py` right after `st.set_page_config`; this loads `static/styling.css` and sets the logo. Visuals: build a payload with `src/viz/payloads.py` and draw it with `src/viz/visuals.show(kind, payload, key=..., interactive=...)`; with `interactive=True` the clicked item comes back as a dict. Exports: `visuals.export(kind, payload, name)` writes a standalone HTML report to `exports/`. The visuals use ECharts 5.5.1 from `components/sc_chart/` and the fonts in `static/fonts/`; nothing loads from a CDN. The page "Design Demo" shows the theme and the four visuals with made-up data. `src/viz/charts.py` (Plotly) is the older version and is not used by any page.
