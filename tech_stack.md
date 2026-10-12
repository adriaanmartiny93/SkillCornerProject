# Tech Stack

## Overview

| Layer | Choice | Why |
|---|---|---|
| App framework | **Streamlit** (multipage) | Fast pilot UI, built-in caching, buttons for on-demand recalculation |
| Data handling | **pandas**, **numpy** | CSV-based pilot, so no database yet |
| Analytics | **scikit-learn**, **scipy** | Standardisation, PCA, k-means, distance metrics |
| Templating | **Jinja2** | HTML templates for iframe visuals, rendered from Python payloads |
| Charting (in templates) | **Apache ECharts** (recommended) | One JS file, radars, scatter and bars built in, good interactivity, easy theming |
| Interactivity | **Streamlit custom component** (bidirectional) | Sends click and selection events from the iframe back to Python |
| Export | **openpyxl** + plain HTML | Excel shortlists and standalone HTML reports |

## Data layer

- **Source:** SkillCorner CSV exports in `data/raw/`. These files are read-only.
- **Derived outputs:** versioned CSVs in `data/derived/`. Each filename contains a timestamp, for example `team_benchmarks_2026-10-10T1630.csv`.
- **Caching:**
  - `st.cache_data` caches loaded and derived DataFrames.
  - Recalculate buttons clear the relevant cache entry and write new derived files.
- **Later migration:** the loaders in `src/data/` are the only code that touches files. That makes a later move to DuckDB or SQLite a local change.

## Analytics layer

- **Normalisation:**
  - Metrics are expressed per 30 minutes TIP or OTIP.
  - They are then standardised within each competition (z-score or percentile) and adjusted for league strength.
- **Team style:** `StandardScaler` → `PCA` → `KMeans` produces the style archetypes.
- **Similarity:**
  - The core is a weighted cosine or Euclidean distance on standardised, role-specific features, computed with `scipy.spatial.distance` or numpy.
  - The weights come from the target player's signature traits and the team's style.
- **Importance index:** a weighted sum of availability, contribution share, style fit and replaceability. The weights are exposed as sliders.

## Visual layer: iframes with HTML templates

### Rendering flow

```
Python (pandas) → payload builder (dict/JSON) → Jinja2 template → HTML string → iframe in Streamlit
```

### Two embedding modes

1. **Display-only (one-way)**
   - Rendered HTML is passed to `streamlit.components.v1.html(html, height=...)`.
   - Used for radars, breakdown cards and comparison bars.
2. **Interactive (two-way)**
   - A custom component is registered with `streamlit.components.v1.declare_component(path=...)`. It points to a folder with a static `index.html`.
   - The template listens for Streamlit's render message to receive data. It returns selections with `setComponentValue` through the Streamlit component messaging protocol, either via `streamlit-component-lib` or a small hand-written `postMessage` wrapper.
   - No React or npm build is needed for a static-HTML component.
   - Used for the style-vs-quality scatter, the squad importance chart and the candidate table.

### Template conventions

- `templates/base.html` holds the club colours, fonts, logo and the iframe auto-resize helper. Every visual template extends it.
- There is one template per visual type, and each one takes a JSON payload with these keys:
  - `data`
  - `labels`
  - `colours`
  - `title`
  - `options`
- JS libraries are bundled in `static/` and inlined or served locally, so the app doesn't depend on a CDN on the club network.
- As built: ECharts is in `components/sc_chart/`, and in the app the display-only visuals also go through that component, not through `components.html`. Streamlit serves `.js` files from `static/` as plain text, so the browser will not run them from there. The Jinja2 templates are used for the standalone exports.
- Each template has a fixed height, or the base helper reports the content height.

### Charting library options

| Library | Pros | Cons |
|---|---|---|
| **ECharts** (recommended) | Radars, scatter and bars out of the box, strong interaction, a single file | Large file (~1 MB unminified) |
| Plotly.js | Familiar, good hover | Heavy, less flexible styling |
| D3 | Full control | Much more code per visual |

## Export

- **HTML reports:** a filled template is saved to `exports/` as a standalone file with inlined JS.
- **Shortlists:** pandas writes CSV, and openpyxl writes formatted Excel.

## Python version

- Python 3.11 or newer.

## Not needed for the pilot (candidates for later)

- DuckDB or SQLite instead of CSVs
- Authentication and multi-user deployment, for example Streamlit Community Cloud or an internal server behind SSO
- A merge with external data for market value and contracts
- A scheduled data refresh instead of manual CSV drops
