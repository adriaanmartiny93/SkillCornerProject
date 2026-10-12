# Todo

## Task 1 - Project set-up (2026-10-10)

Goal: read the project, then create the folders and the virtual environment so work on Step 0 (data foundation) can start. No analytics or app logic yet.

Status: done.

### Plan

- [x] Read all project files (README, tech_stack, requirements, .gitignore, CLAUDE.MD, 13 raw CSVs, glossary HTML, glossary PDF)
- [x] Write this plan and start docs/activity.md
- [x] Plan verified by user
- [x] Create the folder structure from the README: `pages/`, `src/{data,benchmarks,importance,similarity,viz}/`, `templates/`, `components/`, `static/`, `data/raw/`, `data/derived/`, `exports/` (with `.gitkeep` in empty folders and `__init__.py` in the `src` packages)
- [x] Move the 13 CSVs from `raw/` to `data/raw/` (matches README and tech_stack; files are moved, not changed)
- [x] Update `.gitignore`: ignore `data/derived/*` and `exports/*` outputs, and the raw CSVs
- [x] Create `.venv` with Python 3.13.5 and install `requirements.txt`
- [x] Add a minimal placeholder `app.py` (title + a table listing the CSVs found in `data/raw/` with row and column counts) so the set-up can be checked in the browser with `streamlit run app.py`
- [x] Verify: imports work, `streamlit run app.py` starts, the 13 CSVs are listed
- [x] Stage the changes in git (no commit)
- [x] Add the review section below and update docs/activity.md

### Decisions (answered by user)

1. Raw data location: moved from `raw/` to `data/raw/`.
2. Raw data in git: ignored. The CSVs are 390 MB in total and the largest, `off_ball_runs.csv`, is 88.5 MB, close to GitHub's 100 MB per-file limit.

### What was found while reading

Data (now in `data/raw/`, 13 CSVs, 390 MB), season 2024/2025, five competitions: Premier League (895), Championship (890), Pro League BEL (873), Eredivisie (925), Superliga DEN (888). 90 teams.

| File | Rows | Cols | Grain | Player key |
|---|---|---|---|---|
| competition_editions | 5 | 12 | competition edition | - |
| player_performance_metadata | 70,504 | 37 | player x match (includes GK and SUB rows) | `id` |
| physical | 48,708 | 164 | player x match | `player_id` |
| off_ball_runs | 46,432 | 823 | player x match | `player_id` |
| line_breaking_options | 49,433 | 480 | player x match | `player_id` |
| passes_to_off_ball_runs | 47,772 | 628 | player x match | `player_in_possession_id` |
| line_breaking_passes | 48,954 | 452 | player x match | `player_in_possession_id` |
| possessions | 49,154 | 52 | player x match | `player_id` |
| on_ball_engagements | 45,865 | 246 | player x match | `player_id` |
| pressing_engagements | 45,865 | 99 | player x match | `player_id` |
| pressure_engagements | 45,865 | 99 | player x match | `player_id` |
| counter_press_engagements | 45,866 | 99 | player x match | `player_id` |
| recovery_press_engagements | 45,865 | 137 | player x match | `player_id` |

Points to carry into Step 0:

- Everything is per player per match; season values have to be aggregated by us.
- The dynamic-event files only carry `competition_edition_id`, `match_id`, player id and name. Team, position and minutes must come from `physical.csv` (has `minutes_full_tip` / `minutes_full_otip`, needed for the per-30 TIP/OTIP normalisation) or `player_performance_metadata.csv`.
- The player key has three different names (`player_id`, `player_in_possession_id`, `id`).
- Match coverage differs: metadata 1,736 matches, physical 1,705, dynamic events 1,622.
- Positions: 18 in `physical` (no goalkeepers), 5 position groups. The README role groups (CB, FB/WB, DM, CM, AM, W, CF) need their own mapping; there is no "CM" position in the data.
- Quality (clarified by user on 2026-10-10): quality means how successful a team is at what it does, measured in the SkillCorner data itself, not league results. Style = how much / where (for example `count_pressing_in_high_block`); quality = the outcome of the same actions (for example regains, disruptions and `beaten_by` counts for those pressing actions). The export has such volume/outcome pairs for pressing, passing and runs, so no external source is needed for this. Results data (points, goals, xG) is not in the export.
- Some column names start with a digit (`8m_carry_...` in possessions).

Glossary:

- `dynamic_events_aggregates_guide.html`: the definition of every aggregated metric in the CSVs. This is the reference for the files we have.
- `20250216 - Dynamic Events CSV Specifications.pdf` (89 pages): the spec of the underlying event-level data (definitions of possessions, off-ball runs, passing options, on-ball engagements, phases of play, attribute tables). Pages 1-8 read in full, the rest by outline only; to be read in detail per topic when needed.

Environment: Python 3.13.5 (Homebrew), meets the 3.11+ requirement. `CLAUDE.MD`, `README.md`, `tech_stack.md`, `requirements.txt` and `glossary/` were not yet tracked in git before this task.

### Review

Changes made:

- Folder structure from the README created: `pages/`, `src/` (five packages with `__init__.py`), `templates/`, `components/`, `static/`, `data/raw/`, `data/derived/`, `exports/`. Empty folders hold a `.gitkeep`.
- The 13 CSVs were moved unchanged from `raw/` to `data/raw/`; the empty `raw/` folder was removed.
- `.gitignore`: `data/raw/*`, `data/derived/*` and `exports/*` are ignored (their `.gitkeep` files are kept). The CSVs therefore exist only on this machine.
- `.venv` created with Python 3.13.5; `requirements.txt` installed unchanged. Installed versions: streamlit 1.65.0, pandas 3.0.6, numpy 2.5.3, scikit-learn 1.9.1, scipy 1.18.1, Jinja2 3.1.6, openpyxl 3.1.5.
- `app.py` added as a placeholder: one page listing the CSVs in `data/raw/` with rows, columns and size.
- `tasks/todo.md` and `docs/activity.md` added.

Verified: all packages import; the app runs without errors and lists all 13 CSVs; the Streamlit server answers on HTTP 200.

Check it yourself:

```bash
source .venv/bin/activate
streamlit run app.py
```

Not done / to note:

- Nothing is committed; all changes are staged for review.
- `requirements.txt` has lower bounds only, so the newest versions were installed (pandas 3.x, numpy 2.x). Versions are not pinned.
- The PDF spec was read in full only for pages 1-8; pages 9-89 by outline.
- Next step according to the README build order: Step 0, the data foundation (CSV inventory, join keys, normalisation rules, role mapping).

---

## Task 2 - Step 0: data foundation (2026-10-10)

Goal: one small data layer in `src/data/` that every later step builds on: load the raw CSVs, join them on shared keys, apply the per-30 TIP/OTIP rule, map positions to roles, flag low samples and write timestamped derived CSVs. No team benchmarks, importance or similarity yet.

Status: done.

### Plan

- [x] Read CLAUDE.MD, README, tech_stack, todo and activity log; profile keys, positions and minutes in the raw data
- [x] Write this plan
- [x] Plan verified by user
- [x] `src/data/loaders.py`: the only code that touches files. Load a raw CSV by name (player key renamed to `player_id` in every file), write a derived CSV with a timestamp in the name, load the latest derived CSV
- [x] `src/data/roles.py`: the position-to-role mapping as one dictionary (see decision 1)
- [x] `src/data/inventory.py`: the file inventory as one table (grain, player key, metric family, TIP or OTIP, rows, columns, matches covered)
- [x] `src/data/foundation.py`:
  - player-match base table from `physical.csv` (player, team, competition, match, position, role, minutes all / TIP / OTIP)
  - player-season table (minutes all / TIP / OTIP, matches, role, `low_sample` flag; starts are added in Step 2 from the metadata file)
  - `per_30(...)`: season sum of a count metric divided by season TIP or OTIP minutes, times 30
  - `standardise(...)`: z-score and percentile within competition (and role)
- [x] `app.py`: replace the placeholder with a "Data foundation" page: sidebar with a "Set minutes threshold" field and a "Recalculate" button that runs the player pipeline and writes the derived CSV; tabs for the player-season table with filters (competition, team, role, sample), a metric check for one metric the user picks, the role mapping and the file inventory
- [x] Verify: row counts reconcile with the raw files, a hand-calculated per-30 value for one player matches, the app runs
- [x] Stage the changes in git (no commit)
- [x] Add the review section and update docs/activity.md

### Normalisation rules (proposed)

| File | Minutes used for per-30 |
|---|---|
| off_ball_runs, line_breaking_options, passes_to_off_ball_runs, line_breaking_passes, possessions | TIP (`minutes_full_tip`) |
| on_ball_engagements, pressing, pressure, counter_press, recovery_press engagements | OTIP (`minutes_full_otip`) |
| physical | already split in the file by `_tip` / `_otip` / `_all` suffix; each uses its own minutes |

- Only additive columns (counts, distances, xThreat sums) are summed over the season and then divided by minutes. Averages and ratios in the raw files (`avg_...`, `xpass_completion_...`, `psv99`, `timetohsr`) are not summed; they are handled per metric when a later step needs them.
- Ratios (for example regains per press) are computed from season sums, not as a mean of match ratios.
- Standardisation: z-score and percentile within competition and role group. Low-sample rows are left out of the mean and spread, but still get a score and keep their flag.
- Physical rows with `physical_check_passed = False` (1,097 of 48,708) are left out of physical metrics only; their minutes still count.
- Step 0 builds the rules and the base tables. It does not pre-compute all 2,700 metric columns; each later step picks its own metrics and calls the same functions.

### What was found for this task

- `minutes_full_tip` and `minutes_full_otip` are ball-in-play minutes: about 19 each per player-match against 69 total minutes. Per-30 values are therefore close to "per full match in that phase".
- `physical.csv` has one row per player and match with no duplicates, and carries team, competition, position and all minutes. It is the base table; the dynamic-event files are joined to it on `match_id` + `player_id`.
- Coverage gap: 1,705 matches in physical against 1,622 in the dynamic-event files. Minutes are counted per file, only over the matches that file covers, so a missing match does not lower a per-30 value.
- 126 players played for two teams in the season.
- Season minutes per player and competition (2,484 rows): median 1,201; 1,923 have 300+, 1,766 have 450+, 1,654 have 600+, 1,449 have 900+.
- Positions, checked on which positions appear together in the same team and match:
  - `LM` / `RM` appear with a single `DM` (49%) and almost never with `LDM` / `RDM` (5%), and with either wingers or wing-backs beside them. They are the two central midfielders of a midfield three, not wide midfielders. This is the missing "CM".
  - `LDM` / `RDM` are the double pivot (79% of `AM` line-ups have one).
  - `LF` / `RF` always play next to a `CF` and almost never with `LW` / `RW` (8%): the two narrow forwards behind or beside a striker.

### Decisions (answered by user)

1. Role mapping. Proposed:

   | Role | Positions |
   |---|---|
   | CB | CB, LCB, RCB |
   | FB/WB | LB, RB, LWB, RWB |
   | DM | DM, LDM, RDM |
   | CM | LM, RM |
   | AM | AM |
   | W | LW, RW, LF, RF |
   | CF | CF |

   Open point: `LF` / `RF` in W (SkillCorner's own group "Wide Attacker") or in AM.
2. Grain of the player-season table. Proposed: one row per player x team x competition x role group, so a player who played both CB and FB gets two rows, each with its own minutes and flag. Alternative: one row per player x team with the role he played most.
3. Low-sample threshold. Proposed: flag below 450 minutes (five full matches) in that role; nothing is hidden. The value is one constant and easy to change.

Answers: 1. role mapping approved as proposed (`LF` / `RF` in W). 2. Grain as proposed: player x team x competition x role group. 3. The threshold is not fixed: it is a "Set minutes threshold" field in the app sidebar (default 450), applied when "Recalculate" is pressed.

### Review

Changes made:

- `src/data/loaders.py`: the only module that reads or writes CSVs. Raw files are loaded by name with the player key always returned as `player_id`; derived tables are written to `data/derived/<name>_<timestamp>.csv`; the newest one can be found and loaded.
- `src/data/roles.py`: the role mapping as one dictionary.
- `src/data/inventory.py`: metric family and TIP / OTIP rule per file, plus a table with rows, columns and matches.
- `src/data/foundation.py`: `player_matches` (base table from `physical.csv`), `player_seasons` (with `low_sample` and the threshold used), `run_player_pipeline` (recalculate and write), `additive_metrics`, `match_values`, `season_rates` (per 30 TIP / OTIP, per 90 for whole-match physical metrics) and `standardise` (z-score and percentile within competition and role).
- `app.py`: the placeholder is replaced by the data foundation page described in the plan.
- `data/derived/` holds one `player_seasons` file built with the default threshold of 450 (ignored by git).

Verified:

- Base table: 48,708 player-match rows, every position has a role. Player-season table: 7,013 rows, no duplicate keys; minutes add up to the raw total (3,369,824.5).
- Hand check: `count_on_ball_engagements` per 30 OTIP for one player, recomputed directly from the two raw CSVs, equals the pipeline value (95.758).
- Standardisation: within competition and role the z-scores of the reference players have mean 0 and spread 1.
- App test: starts without errors, Recalculate writes a derived file with the threshold from the sidebar, the tables and the metric check render for a physical and an off-ball-run metric.

Check it yourself:

```bash
source .venv/bin/activate
streamlit run app.py
```

Set a threshold in the sidebar and press Recalculate. In the "Metric check" tab, pick a file, a metric and a player: the match rows, the two sums and the resulting rate are shown so the division can be checked by hand.

To note:

- Splitting by role creates many small rows. The 2,484 player-seasons become 7,013 rows (2.8 roles per player on average, up to 8), because every short spell in another position is its own row. At 450 minutes 4,991 rows are flagged and 2,022 are not; those 2,022 hold 85% of all minutes. 1,632 of the 2,484 players have at least one unflagged role. Rows with enough minutes at other thresholds: 2,479 at 300, 1,717 at 600, 1,297 at 900.
- Low-sample rows get extreme scores (z-scores above 100 occur for players with a few minutes). They are flagged, not capped.
- Event rows that cannot be joined to `physical.csv` are left out: goalkeepers and matches missing from the physical file. For `count_on_ball_engagements` this is 2% of the raw total.
- A player with no row in an event file for a match that file covers counts as 0 for that match.
- Whole-match physical metrics (`_all`) are expressed per 90 minutes, TIP and OTIP metrics per 30. This per-90 choice was not in the approved plan.
- Metric rates are calculated on demand; only the player-season table is written to `data/derived/`. Derived file names carry seconds (`T165036`) so two quick recalculations do not overwrite each other.
- The inventory tab takes some seconds the first time, because it counts matches in every raw file.
- Nothing is committed; all changes are staged for review.
- Next according to the README build order: base template, data contract and the first display template (radar).

---

## Task 3 - Metric catalogue page (2026-10-10)

Goal: one page in the app that lists every metric in the raw files by category, with stored details per metric: how the season value is calculated (total per 90 / per 30, average, peak, ...) and whether scoring is inverse (lower is better).

Status: done.

### Plan

- [x] Survey all metric columns and the glossary
- [x] Write this plan
- [x] Plan verified by user
- [x] `src/data/catalogue.py`: build the catalogue from naming rules plus the glossary HTML (type and definition), one row per metric column
- [x] Store it as `data/metric_catalogue.csv` (tracked in git, see decision 1); loading and saving go through `src/data/loaders.py`
- [x] `pages/0_Metric_Catalogue.py`: the catalogue per category (file) with search and filters on calculation and inverse; the calculation and inverse fields can be edited and saved
- [x] `src/data/foundation.py`: read the calculation from the catalogue instead of the name rules in `additive_metrics`, so the page and the pipeline cannot disagree
- [x] Verify: every raw metric column is in the catalogue exactly once, counts per calculation type, the page runs
- [x] Stage the changes in git (no commit)
- [x] Add the review section and update docs/activity.md

### What was found

- 3,233 non-key columns in the 11 metric files; about 3,075 in the event files and 149 metrics in physical.
- The glossary HTML has a type and a one-line definition for 3,008 metric names. 356 event columns are not in it (for example `count_force_backward_pressing`); these get an empty definition.
- There are no percentage columns in the raw files. Every column is one of the types below.
- Correction to Step 0: `xpass_completion_...` is a sum of pass-completion probabilities per match, not a ratio. It can be summed over the season, but a per-30 value means little; divided by its count it gives the average expected completion.

### Proposed fields per metric

`file`, `category`, `metric`, `type` and `definition` (both from the glossary), `calculation`, `per`, `weight` (the count column used for averages), `inverse`.

### Proposed calculation rules

| Calculation | Columns | Season value | Per |
|---|---|---|---|
| total | `count_...`, `xthreat_...`, possession counts, physical distances and counts | season sum divided by minutes | 30 TIP, 30 OTIP, or 90 for whole-match physical |
| expected total | `xpass_completion_...` (402) | season sum divided by the matching count = average expected completion (0 to 1) | none |
| average | `avg_...` (171), `timetohsr`, `timetosprint` | mean over matches, weighted by the matching count (or by minutes where no count exists) | none |
| peak | `psv99` | highest match value of the season | none |
| rate | `total_metersperminute_...` | recalculated as season distance divided by season minutes | none |

Inverse (lower is better), proposed: the 66 `count_beaten_by_...` columns, `timetohsr` and `timetosprint`. Everything else: no. `count_difficult_...` means a difficult pass target, not a failure, so it is not inverse.

### Decisions (answered by user)

1. Storage and editing. Proposed: the catalogue is generated once by the rules, stored as `data/metric_catalogue.csv` in git, and from then on that file is the truth; `calculation` and `inverse` are editable on the page with a Save button. A "Rebuild from rules" button resets it. Alternative: rules in code only, page is read-only.
2. Percentages. The raw files have none; they would be new metrics built from two columns (for example regains divided by presses, completed divided by attempted line-breaking passes). Proposed: not in this task. The catalogue lists raw columns only; derived percentages are added as their own rows when Step 1 defines them.
3. Peak speed. Proposed: season maximum of `psv99`. Alternative: mean of the three best matches, which is less sensitive to one tracking error.
4. Half splits. Physical has every metric for full match, first half and second half. Proposed: list them all, with the half splits marked so they can be filtered out.

Answers: 1. storage and editing agreed. 2. percentages left out of this task. 3. the user pointed out that `psv99` is not the only best-value metric: time to sprint, time to HSR and time to turnaround are of the same kind. 4. mainly full-match data.

How 3 and 4 were applied:

- `psv99` is `max` (highest match value of the season); `timetohsr` and `timetosprint` are `min` (lowest match value of the season) and lower is better. This replaces the "average" proposed for the two time metrics in the table above. Time to turnaround is not in this export: `physical.csv` has no such column.
- The "rate" type in the table above was dropped: metres per minute is an `average` weighted by minutes, which is the same as season distance divided by season minutes.
- The first-half and second-half physical metrics are in the catalogue with `scope` h1 / h2 and are hidden by default ("Full match only" is ticked). Season values are only calculated for full-match metrics.

### Review

Changes made:

- `src/data/catalogue.py`: builds the catalogue from the naming rules and the glossary, and loads the stored file. Fields: `category`, `file`, `metric`, `type`, `definition`, `scope`, `calculation`, `per`, `weight`, `inverse`.
- `data/metric_catalogue.csv`: the stored catalogue, 3,213 metrics, tracked in git. From now on this file is the truth.
- `pages/0_Metric_Catalogue.py`: the catalogue with filters in the sidebar (category, file, calculation, lower is better, search, full match only). `calculation`, `per`, `weight` and `lower is better` can be edited in the table and saved. "Rebuild from rules" asks for confirmation and discards all edits.
- `src/data/loaders.py`: reads the glossary and reads / writes the catalogue file.
- `src/data/foundation.py`: `match_values` and `season_rates` now take the calculation of each metric from the catalogue (total, expected total, average, max, min). The name-based `additive_metrics` and `metric_phase` are removed. Season columns are named `<metric>_p30`, `_p90` or `_season`.
- `app.py`, Metric check tab: lists all full-match metrics of a file, shows the calculation and the lower-is-better flag, and the minutes or weight column that the season value is built from.

Catalogue contents:

| Calculation | Metrics | Per |
|---|---|---|
| total | 2,681 | 1,977 per 30 TIP, 662 per 30 OTIP, 42 per 90 |
| expected total | 402 | none |
| average | 127 | none |
| max | 1 | none |
| min | 2 | none |

68 metrics are lower is better (66 `count_beaten_by_...`, `timetohsr`, `timetosprint`). 3,123 are full match, 90 are half splits.

Verified:

- Every metric column of the 11 files is in the catalogue exactly once (key: file + metric). Every average and expected total found its weight column.
- Hand checks for one player from the raw CSVs: expected total (0.8496) and weighted average (17.564) equal the pipeline values. Metres per minute as a minutes-weighted average equals season distance divided by season minutes to within 0.1% (rounding in the raw file).
- App test: the catalogue page runs with filters, Save writes the file unchanged when nothing was edited, and the Metric check renders one metric of each calculation type.

Check it yourself:

```bash
source .venv/bin/activate
streamlit run app.py
```

Open "Metric Catalogue" in the page list on the left.

To note:

- Editing a cell in the table and saving it was not covered by the automated test (the test tool cannot type into the table); only the Save round trip without edits was. Please try one edit.
- 494 metrics have no definition: the 138 physical metrics and 356 event columns that are not in the glossary. Their type is inferred from the name.
- The same metric name can appear in several files (for example `count_on_ball_engagements` is in all five pressure files), so a metric is identified by file plus name.
- Lower is better is stored but not yet applied: z-scores and percentiles are not flipped. That belongs to scoring in Step 1.
- `max` and `min` take one match value, so one tracking error can set a player's season value. The calculation can be changed per metric on the page.
- Low-sample players get extreme values for averages as well (few events behind the value).
- Nothing is committed; all changes are staged for review.

---

## Task 4 - Create new metrics in the app (2026-10-10)

Goal: let the user define extra metrics on the Metric Catalogue page, for example `psv99` as season maximum next to `psv99` as the average of the three best matches.

Status: done. Built on 2026-10-12 from the "Revised plan" below. Checked by the user in the browser on 2026-10-12: "looks ok". Staged, nothing committed.

### Idea

A new metric is one extra row in the catalogue: a new name that points to an existing raw column and has its own calculation. Nothing else changes; the season calculation already reads its settings per row.

| metric | source | calculation | weight | origin |
|---|---|---|---|---|
| `psv99` | `psv99` | max | | raw |
| `psv99_top3` | `psv99` | top 3 average | | custom |
| `pressing_regain_pct` | `count_direct_regain_pressing` | ratio | `count_pressing` | custom |

The same mechanism covers the percentages that were left out of Task 3: a ratio is a season sum divided by the season sum of a second column. That is the calculation now called "expected total"; it would be renamed to "ratio".

### Plan

- [x] Write this plan
- [x] Plan verified by user (decisions 1 and 2; decision 3 left open)
- [ ] Catalogue: add the columns `source` (the raw column that is read; for raw metrics it is the metric itself) and `origin` (raw or custom)
- [ ] Add the calculation "top 3 average": mean of the three best match values of the season (the three lowest for lower-is-better metrics)
- [ ] Rename "expected total" to "ratio"
- [ ] `src/data/foundation.py`: read the `source` column and return it under the metric's own name
- [ ] Catalogue page: an "Add metric" form (name, file, source metric, calculation, per, weight, lower is better) and a way to delete custom metrics; "Rebuild from rules" keeps custom metrics
- [ ] Metric check tab: pick two metrics of the same file to see them next to each other (for example `psv99` and `psv99_top3`)
- [ ] Verify by hand for `psv99_top3` and one ratio; app test
- [ ] Stage the changes, add the review section, update docs/activity.md

### Decisions

1. Answered: the number of best matches is set per metric, default 3. It is one extra catalogue column.
2. Answered: with fewer matches than that number, average the matches there are, and flag the player.
3. Open, to be decided next session: ratios across files (numerator in one file, denominator in another). Proposal on the table: same file only for now.

### Notes for building this after Task 5

- Task 5 changed the season calculation: totals are the mean of match rates over matches that pass the match filter, and every catalogue row has a `match_filter` column. A new custom metric needs a value for it too; a "top N average" would default to no match filter, like max and min.
- "Expected total" is the sum-over-sum calculation that a ratio needs; the plan above renames it to "ratio".
- How to flag (decision 2) is not settled in detail: the existing `low_sample` flag is based on included matches, while a top-N metric without match filter looks at all matches. To be worked out when building: reuse `low_sample`, or a separate flag for "fewer than N matches with a value".

### Check of this plan against the current code (2026-10-12)

Prompt: "check task 4". Read `src/data/catalogue.py`, `src/data/foundation.py`, `src/data/loaders.py`, `pages/0_Metric_Catalogue.py` and the Metric check tab in `app.py`. No code changed.

The plan still fits the code. The idea (a custom metric is one extra catalogue row) works, because `match_values` and `season_rates` already read every setting per row. Missing from the checklist above:

- A catalogue column for the number of best matches (decision 1), proposed name `top_n`. The checklist only names `source` and `origin`.
- The stored `data/metric_catalogue.csv` is the truth, so the new columns and the rename of "expected total" (402 rows) need a one-time update of the stored file in `load_catalogue`, the same way `match_filter` was added.
- `match_values` loads raw columns by metric name. For a custom metric it has to load the `source` column and copy it to the metric's name; today a custom name would fail there.
- The "Add metric" form must refuse a name that already exists in that file, as a metric or as a raw column.
- "Top N average" takes the N highest values, or the N lowest when the metric is lower is better, so it reads the `inverse` field.
- A ratio is stored as a fraction (0 to 1), like the 402 existing ones, not times 100.

Proposals for the open points:

- Decision 3 (ratios across files): same file only. `match_values` reads one file per call, and physical covers other matches (1,705) than the event files (1,622). Many useful denominators are already in the same file (`count_on_ball_engagements` is in all five pressure files).
- Flag for decision 2: `season_rates` adds one column per top-N metric with the number of matches used; fewer than N means flagged. The existing `low_sample` flag stays as it is.
- Side-by-side in the Metric check tab: the tab is built around one metric. Proposed: a second, optional "Compare with" metric of the same file that adds its season value as one extra column in the player table; the match rows stay for the first metric.

### Revised plan (2026-10-12)

Prompt: "Seperate calculated metrics in new tab: tab 1 --> general catalogue, tab 2 --> calculated season metrics --> here we add details around 'Take avg of best x'".

This replaces the unchecked items of the plan above. Verified by the user: "if we still include existing metrics in seasonal calculations (so not only the custom ones) then \"go\"". That condition holds: the raw metrics stay in the same catalogue and are calculated as before. The three proposals of the check were taken as accepted with this "go".

Layout of the Metric Catalogue page:

- Tab 1 "General catalogue": the page as it is today, raw metrics only. The sidebar filters apply to this tab.
- Tab 2 "Calculated season metrics": the metrics we define ourselves. A table of them with the fields that matter here (name, file, source metric, calculation, best x matches, weight, match filter, lower is better), an "Add metric" form and a way to delete one. The "best x matches" field only exists in this tab.

Storage: both tabs read the same file, `data/metric_catalogue.csv`. A column `origin` (raw or custom) decides in which tab a row is shown. The season calculation keeps reading one catalogue.

- [x] Catalogue: new columns `source`, `origin` and `top_n` (best x matches); one-time update of the stored file; "expected total" renamed to "ratio"
- [x] New calculation "top N average": mean of the x best match values (the x lowest for lower-is-better metrics), no match filter by default
- [x] `src/data/foundation.py`: `match_values` reads the `source` column under the metric's own name; `season_rates` calculates the top N average and returns the number of matches used
- [x] Catalogue page: the two tabs described above; the form refuses a name that already exists in that file; "Rebuild from rules" keeps the calculated metrics
- [x] Metric check tab in `app.py`: calculated metrics can be picked like any other; an optional "Compare with" metric of the same file
- [x] Verify by hand for `psv99_top3` and one ratio; headless app test (no browser)
- [x] Stage the changes, add the review section, update `docs/activity.md`

### Review (Task 4)

Changes made:

- `src/data/catalogue.py`: three new catalogue columns, `source` (the raw column that is read), `origin` (raw or custom) and `best_x`. New calculation "average of best x". "expected total" is renamed to "ratio". New functions to add a calculated metric, to check whether a name is taken, and to rebuild the catalogue while keeping the calculated metrics.
- `data/metric_catalogue.csv`: updated once with the three columns and the new name "ratio" (402 rows). Still 3,213 rows, all raw; no calculated metric is stored yet.
- `src/data/foundation.py`: `match_values` reads the source column of a calculated metric under the metric's own name. `season_rates` calculates the average of best x and adds `<metric>_matches`, the number of matches it is built from.
- `pages/0_Metric_Catalogue.py`: two tabs. "General catalogue" is the page as it was, raw metrics only. "Calculated season metrics" has the table of calculated metrics (best x matches, match filter and lower is better can be edited), "Delete metrics", and an "Add metric" form for the two calculations: average of best x, and ratio.
- `app.py`, Metric check tab: calculated metrics are in the metric list; an optional "Compare with" metric of the same file adds its season value as a column.

Existing metrics: nothing changed in how raw metrics are calculated. The stored catalogue is equal to a fresh rebuild from the rules.

Verified by Claude (no browser; the test metrics were removed again afterwards):

- Hand check from the raw CSV for one player: `psv99` best 3 = mean of 33.0, 31.0 and 30.4 = 31.467, equal to the pipeline; the season maximum stays 33.0. For a lower-is-better metric (`timetosprint`) the three lowest values are taken (1.503, equal to the pipeline).
- Fewer than x matches: a player with 2 matches gets the mean of those 2, and `psv99_best3_matches` shows 2.
- Hand check of a ratio (`count_direct_regain_pressing` divided by `count_pressing`) over the included matches of one player: equal to the pipeline.
- Headless app test: the catalogue page runs with and without calculated metrics; Add metric stores the row; adding the same name again is refused; Save works on both tabs; Delete removes the row and leaves the file identical to before. The main page runs with a calculated metric and "Compare with".

Verified by the user: looked at the result in the browser and reported "looks ok".

Check it yourself:

```bash
source .venv/bin/activate
streamlit run app.py
```

Open "Metric Catalogue", tab "Calculated season metrics". Add `psv99` with "average of best x" and x = 3. Then on the main page, tab "Metric check": file physical, metric `psv99_best3`, compare with `psv99`.

To note:

- Names differ from the plan: the calculation is called "average of best x" and the column `best_x` (the plan said "top N average" and `top_n`), to match the wording of the request.
- The form offers two calculations only: average of best x, and ratio. Other calculations of a raw metric (for example a plain mean of `psv99`) cannot be added there.
- "Best x" is per row of the player table, so per player, team, competition and role. With x = 3, 3,351 of the 6,880 rows have fewer than 3 matches for `psv99`; they are not hidden, the `_matches` column shows it.
- The average of best x has no match filter by default (like max and min); it can be ticked per metric.
- A ratio is a fraction from 0 to 1, and both columns come from the same file.
- A calculated metric on a first-half or second-half physical metric is stored, but does not show in the Metric check tab, which lists full-match metrics only.
- Editing a cell in a table and saving it is still not covered by an automated test (only Save without edits).
- Nothing is committed; the changes are staged for review.

---

## Task 5 - Match-by-match rates, then season aggregates with a match filter (2026-10-10)

Requested by the user; replaces the season calculation built in Step 0 and Task 3. To be done before Task 4 (new metrics), which builds on it.

Goal:

1. Every match is first transformed to a rate on its own (per 90, or per 30 TIP / OTIP as set in the catalogue).
2. The season value is then an aggregate over the player's matches, where a filter decides whether a match is included: minimum minutes in the match, set by hand in the app, default 60.

Status: done.

### What changes compared to now

| | Now | Requested |
|---|---|---|
| Step 1 | sum the raw values over all matches | each match becomes its own per-90 / per-30 value |
| Step 2 | divide the season sum by season minutes | aggregate the match values of the included matches |
| Short appearances | count, with little weight | left out by the match filter |

### Plan

- [x] Write this plan
- [x] Plan verified by user
- [x] `src/data/foundation.py`: `match_rates` adds the per-match rate of each "total" metric (match value divided by match minutes, times 90 or 30)
- [x] `src/data/foundation.py`: `season_rates` takes `min_match_minutes` (default 60), keeps only the matches that pass, and aggregates per calculation type (see decision 1)
- [x] Player pipeline: the player-season table gets the number of included matches and the minutes in them, next to the totals; the filter value used is stored in the file
- [x] `app.py` sidebar: a "Minimum minutes per match" field (default 60) next to the existing threshold; Recalculate applies both
- [x] Metric check tab: the match rows show the match rate and whether the match is included, so a season value can be checked by hand
- [x] Catalogue page: update the explanation of the calculation types
- [x] Verify by hand for one total, one ratio and one max metric; app test
- [x] Stage the changes, add the review section, update docs/activity.md

### What was found

- 32,249 of the 48,708 player-match rows (66%) have 60 minutes or more.
- Of the 7,013 player x team x competition x role rows, 3,876 have at least one included match, 2,524 at least three, 1,935 at least five, 1,214 at least ten.

### Decisions (answered by user)

1. Season aggregate of the match rates. Proposed: the plain mean of the included matches (each match counts equally; this is how SkillCorner itself reports per-90 season values). Alternative: weighted by minutes. For the other calculation types the filter is applied in the same way: ratio = sum divided by sum over the included matches, average = weighted mean over the included matches, max / min = best included match.
2. Per 90 for everything, or keep per 30 TIP / OTIP. Proposed: keep what the catalogue says per metric (90 for whole-match physical, 30 TIP for in-possession, 30 OTIP for out-of-possession metrics); the match filter always looks at total minutes in the match (`minutes_full_all`).
3. Low-sample flag. With a match filter, season minutes mean less. Proposed: flag on the number of included matches (field "Minimum matches", default 5) instead of 450 season minutes.

Answers: 1. plain mean over the matches that meet the threshold. 2. keep per 90 / per 30 TIP / per 30 OTIP as set in the catalogue. 3. low-sample flag on the number of included matches. Extra: the match filter only applies to aggregate metrics, not to max / min, and becomes a column in the catalogue.

### Review

Changes made:

- Catalogue: new column `match_filter` (yes / no per metric), editable on the Metric catalogue page. Default: yes for total, expected total and average (3,210 metrics), no for max and min (`psv99`, `timetohsr`, `timetosprint`). The stored `data/metric_catalogue.csv` was extended with this column; nothing else in it changed.
- `src/data/foundation.py`:
  - `match_values` adds the rate of each match for "total" metrics (`<metric>_p90` or `_p30` = match value divided by match minutes).
  - `season_rates` takes `min_match_minutes` (default 60). A total is the plain mean of the match rates of the included matches. Expected totals and averages are calculated over the included matches. Metrics without the match filter use every match.
  - `player_seasons` has `matches_included` and `minutes_included`; `low_sample` is now "fewer than `min_matches` included matches" (default 5). The 450 season-minutes threshold is gone. Both settings are stored in the derived file.
- `app.py`: the sidebar has "Minimum minutes per match" (60) and "Minimum matches" (5); Recalculate applies both. The Metric check tab uses the minutes setting of the stored player table and shows per match: minutes, included yes / no, the raw value and the match rate.
- `data/derived/` holds one `player_seasons` file with the defaults (60 minutes, 5 matches).

Verified:

- Hand check from the raw CSVs for a player with 17 matches of which 7 have 60 minutes or more: distance per 90 is the mean of the 7 match rates (9,675.96; over all 17 matches it would be 9,591.50), and `psv99` takes the best of all 17 matches (34.6; the best included match is 33.6).
- Hand checks for an expected total and a minutes-weighted average over included matches match the pipeline.
- App test: starts without errors, Recalculate with 45 minutes / 4 matches writes a file with those settings, the Metric check renders for a max, an expected total and a total metric, the catalogue page runs.

Effect of the defaults (60 minutes, 5 matches): 32,249 of 48,708 player-match rows are included. Of the 7,013 player-role rows, 1,935 are not low sample (2,022 under the old 450-minutes rule); they cover 1,563 of the 2,484 players.

To note:

- Example for the flag: 4 matches of 60 minutes is 240 minutes. Under the old rule (450 season minutes) that row was low sample. Under the new rule it depends only on "Minimum matches": low sample at the default 5, not low sample if it is set to 4.
- A total is now a mean of match rates, so each included match counts equally whether it was 60 or 100 minutes.
- For per-30 TIP / OTIP metrics the filter still looks at total minutes in the match; a 60-minute match has roughly 15 to 20 minutes in each phase, so single-match rates are noisy and it is the mean over matches that carries the information.
- Editing a cell on the catalogue page is still not covered by an automated test.
- Nothing is committed; all changes are staged for review.
- Task 4 (new metrics, top 3 average) is next and still has three open decisions.

---

## Task 6 - Re-organise the project for the design system (2026-10-12)

Goal: put the design kit described in the design readme in the right places of the project and switch the two existing pages to it. No new analytics, no new visuals.

Status: done, except decision 1 (charting library), which is open.

### What was found

- The design system came in as a Streamlit kit in a root folder `streamlit/` (`theme.py`, `charts.py`, `styling.css`, a demo `app.py`, `config.toml`, two logos), a root `styles.css`, and, added by the user during the task, `tokens/` (five CSS files) and `assets/` (three logos). `guidelines/`, `ui_kits/` and the React `components/` from the design readme are not in the project; a Streamlit app does not need them.
- A project folder named `streamlit/` has the same name as the Streamlit package, so it could not stay in the root.
- The kit's charts are Plotly figures; Plotly was not installed. `README.md` and `tech_stack.md` plan the visuals as Jinja2 + ECharts templates in iframes.
- `styling.css` and `tokens/fonts.css` load the fonts and the Phosphor icons from the internet (Google Fonts, unpkg). `README.md` Step 0b says assets are bundled locally.

### Plan

- [x] Read the design readme, the kit and the current app
- [x] Write this plan
- [x] Plan check: the user answered by adding `tokens/` and `assets/`; this was taken as the go-ahead with the proposals below. Decision 1 was not answered and is left open
- [x] Move the files (content unchanged apart from paths and imports):

  | From | To |
  |---|---|
  | `streamlit/theme.py` | `src/viz/theme.py` |
  | `streamlit/charts.py` | `src/viz/charts.py` |
  | `streamlit/styling.css` | `static/styling.css` |
  | `streamlit/.streamlit/config.toml` | `.streamlit/config.toml` |
  | `streamlit/app.py` (demo) | `pages/9_Design_Demo.py` |
  | `assets/*.png` | `static/assets/` |
  | `tokens/` | `static/tokens/` |
  | `styles.css` | `static/styles.css` |
  | `readme_design.md` | `docs/design_system.md` |

- [x] Remove the emptied `streamlit/` and `assets/` folders
- [x] `src/viz/theme.py`: CSS and logo paths point to `static/`
- [x] `requirements.txt`: `plotly>=5.22` added; 7.1.0 installed in `.venv`
- [x] `app.py` and `pages/0_Metric_Catalogue.py`: `inject_theme()` after `st.set_page_config`
- [x] Demo page: imports fixed, `use_container_width` replaced by `width="stretch"`
- [x] `README.md`: folder structure updated and a short "Design system" section added
- [x] `.gitignore`: `.DS_Store` added
- [x] Verify with a headless app test
- [x] Stage the changes in git (no commit), add the review section, update docs/activity.md

### Decisions

1. Open - charting. The design kit uses Plotly figures shown with `st.plotly_chart`; the README plans Jinja2 + ECharts templates in iframes. Proposed: Plotly for display visuals, the iframe component only for the one or two interactive visuals. Until this is answered, Step 0b in `README.md` and the visual layer in `tech_stack.md` are unchanged and still describe ECharts in iframes.
2. Applied as proposed: fonts and icons keep loading from the internet for now. Bundling them in `static/` is a later task.
3. Changed: `styles.css` is kept (in `static/`), because the `tokens/` files it imports now exist.
4. Applied as proposed: the demo is kept as `pages/9_Design_Demo.py`.
5. Applied as proposed: the catalogue page title is now "Metric Catalogue". No other text changed.

### Review

Changes made:

- The design kit is part of the project structure: Python in `src/viz/`, CSS, tokens and logos in `static/`, the Streamlit theme config in `.streamlit/config.toml`, the style guide in `docs/design_system.md`. The root holds no design files any more.
- Both existing pages load the theme and show the logo. Their content and logic are unchanged.
- New page "Design Demo" with made-up data: metric tiles, badges, percentile bars, radar, bar chart, distribution and scatter.
- Plotly is a new dependency.

Verified (headless app test): `app.py`, the Metric Catalogue page and the Design Demo page run without errors and each injects the theme CSS; the main page still shows its four tabs and tables.

Not verified: how the pages look in a browser. The headless test cannot see colours, fonts or the logo. Please check this yourself.

Check it yourself:

```bash
source .venv/bin/activate
streamlit run app.py
```

Look at the main page, "Metric Catalogue" and "Design Demo" in the page list on the left. Expected: dark background, green accents, the SkillCorner logo top left, uppercase tabs and buttons.

To note:

- `static/styles.css` and `static/tokens/` are not used by the app yet. `static/styling.css` carries its own copy of the tokens. The token files are for HTML that runs in an iframe, which is only needed if decision 1 goes to iframes.
- The two logos that were in `streamlit/assets/` were byte-identical to the ones in `assets/`; one copy was kept.
- `docs/design_system.md` is the design readme unchanged. Its index still lists the folders of the original design system (`guidelines/`, `ui_kits/`, `streamlit/`), not the paths in this project; the README has those.
- `static/styling.css` targets Streamlit's internal `data-testid` hooks (written for 1.36 and up, installed is 1.65). If something looks unstyled, this is the first place to look.
- The design readme says to make sure you have the rights to use the SkillCorner logo in the app.
- Page labels (sidebar headers, tabs, buttons) are made uppercase by the CSS; the text in the code is unchanged.
- Nothing is committed; all changes are staged for review.

---

## Task 7 - Implement the design-system visuals export (2026-10-12)

Prompt: "open sports analytics design system.zip and implements"

Status: done and staged, nothing committed. The user approved the plan with "go" (all four proposals as written).

### What was found

- The zip holds `export/SkillCornerProject/` with a `readme_implement.md` and 29 files. It replaces the Plotly charts by ECharts visuals and removes every CDN import.
- New: `components/sc_chart/` (component page, chart code, ECharts 5.5.1), `templates/` (base + one per visual), `src/viz/payloads.py`, `src/viz/visuals.py`, `static/fonts/` (12 woff2 files + `fonts.css`).
- Replaced: `.streamlit/config.toml` (adds static serving), `static/styling.css`, `static/tokens/fonts.css`, `pages/9_Design_Demo.py`, `requirements.txt` (comments only).
- Checked before use: `echarts.min.js` is byte-identical to the official 5.5.1 release (same SHA-256 as the jsdelivr copy). `sc_charts.js` (216 lines) makes no network calls and escapes the text it puts into HTML. All 12 font files are valid woff2.
- `static/styling.css` in the zip differs from ours only in the header comment and the font import lines. Its comment has the old import path (`from theme import`), ours has the correct one (`from src.viz.theme import`).
- `components/sc_chart/_preview.html` is in the zip but not in the readme's file list, and it links to a stylesheet outside this project.
- Only `pages/9_Design_Demo.py` uses `src/viz/charts.py` (Plotly). `app.py` and the catalogue page do not.
- Installed: streamlit 1.65.0, jinja2 3.1.6. No new packages are needed.

### Plan

- [x] Copy the new files: `components/sc_chart/{index.html, sc_charts.js, echarts.min.js}`, `templates/{base,radar,distribution,bar,scatter}.html`, `src/viz/payloads.py`, `src/viz/visuals.py`, `static/fonts/*`
- [x] Replace `.streamlit/config.toml`, `static/tokens/fonts.css`, `pages/9_Design_Demo.py`, `requirements.txt` with the zip versions
- [x] `static/styling.css`: change only the font import lines to the local `@font-face` block (keeps our header comment with the correct import path)
- [x] `docs/design_system.md`: "Using it in Streamlit" step 3 now describes payloads + `visuals.show()` / `visuals.export()`; the Iconography and Fonts sections say fonts are local and Phosphor is no longer loaded
- [x] `README.md`: "Design system" paragraph and the folder structure lines updated the same way
- [x] `tech_stack.md`: one line about the component deviation (decision 2)
- [x] Verify: headless app test of all three pages; render one standalone export and check it holds no external URL; start the app once and check that the fonts and the component files are served
- [x] Stage the changes (no commit), add the review section, update `docs/activity.md`

### Decisions

1. `src/viz/charts.py` and `plotly`. After this task no page uses them. Proposed: keep both for now and remove them in a separate step once you have seen the new visuals in the browser.
2. Charting direction. This closes the open decision 1 of Task 6 in favour of ECharts. The export has one deviation from `tech_stack.md`: display-only visuals also go through the component, not through `components.html`, because Streamlit serves `.js` from `static/` as plain text. Proposed: accept it and add one line about it to `tech_stack.md`.
3. `_preview.html`. Proposed: do not copy it.
4. The zip file in the project root. Proposed: leave it where it is and do not stage it. Say so if you want it in `.gitignore` or deleted.

### Review

Changes made:

- The four visuals (radar, distribution, bar, scatter) are now ECharts visuals drawn through one component, `components/sc_chart/`. Python builds a payload with `src/viz/payloads.py` and draws it with `visuals.show()`; `visuals.export()` writes a standalone HTML report to `exports/`.
- Fonts are local (`static/fonts/`). The Google Fonts and Phosphor imports are gone from `static/styling.css` and `static/tokens/fonts.css`. Static serving is switched on in `.streamlit/config.toml`.
- `pages/9_Design_Demo.py` is the zip version: four visuals, click-back on distribution and scatter, an export button.
- `static/styling.css`: only the font lines and two comment lines changed; the rest is as it was.
- `README.md`, `tech_stack.md` and `docs/design_system.md` describe the new way of working.
- `requirements.txt`: comments only, no new packages.

Verified by Claude:

- Headless app test: `app.py`, Metric Catalogue and Design Demo run without errors and inject the theme.
- Standalone exports of radar, bar, distribution and scatter render in headless Chrome with the right fonts; the HTML holds no external URL and has the 12 fonts inlined (about 1.3 MB per file).
- Live Design Demo page in headless Chrome: no request left localhost, Saira / IBM Plex Sans / IBM Plex Mono loaded from `static/fonts/`, the component files are served as JavaScript, the radar and bar frames on the first tab have a size.

Verified by the user: tested the app in the browser and reported it is OK.

Not verified by Claude (stopped at the user's request): the Benchmarks tab in the live app (distribution and scatter), the click-back to Python, and the export button.

To note:

- Cosmetic, in the scatter: the y-axis shows the unrounded lowest and highest value as extra tick labels (for example 30.92 right above 30). Not fixed; it is in `sc_charts.js`.
- A component's files are served under `/component/src.viz.visuals.sc_chart/`. They only exist after a page that imports `src/viz/visuals.py` has run.
- `src/viz/charts.py` and `plotly` are kept but no page uses them. Removing them is a separate step (decision 1).
- `_preview.html` was not copied. The zip stays in the project root, untracked and not staged.
- If the app ever runs under a `server.baseUrlPath`, the `/app/static/fonts/` URLs in `components/sc_chart/index.html` and `static/styling.css` need that prefix.
- Nothing is committed; all changes are staged for review.

---

## Task 8 - Visual bug: icon names shown as text (2026-10-12)

Prompt: screenshot of the sidebar top, with "read project files and make this visual bug the next to-do."

Status: fix applied and staged, nothing committed. Not sufficient: the user found the same bug on an expander. Followed up in Task 9.

### The bug

In the sidebar header the text `keyboard_double_arrow_left` is drawn in large grey letters across the SkillCorner logo. It is the "collapse sidebar" button: the icon is not drawn, its name is shown instead.

### Cause (found by reading the code, not yet confirmed in a browser)

- Streamlit draws its icons with an icon font (Material Symbols Rounded). The element holds the icon name as text, and the font turns that name into the symbol.
- `static/styling.css` line 36 sets the body font on every element in the app: `.stApp *:not([class*="material"]):not(i):not(code):not(pre){font-family:var(--font-body)}`. The exception `[class*="material"]` is meant to skip the icons.
- In the installed Streamlit (1.65.0) an icon is a `<span data-testid="stIconMaterial">` with a generated class name that does not contain "material". The exception therefore does not match, the icon gets IBM Plex Sans, and the name is shown as plain text.
- This is not limited to the collapse button. Every Streamlit icon is affected by the same rule: expander arrows, the sidebar "expand" button, icons in buttons and alerts.
- Line 73 (`.stButton>button *` with `font-family ... !important`) can do the same to an icon inside a button, and wins over the fix below. To be checked.

### Plan

- [x] Read the project files and find the cause
- [x] Write this plan
- [x] Plan verified by user ("go")
- [x] `static/styling.css` line 36: `:not([data-testid="stIconMaterial"])` added to the list of exceptions
- [x] `static/styling.css` line 73: the same exception added to the two button rules (`.stButton>button *`, `.stDownloadButton>button *`). Applied without testing whether it was needed, see the review
- [ ] Check in the browser: by the user (CLAUDE.MD rule 11, no headless browsers)
- [x] Stage the changes (no commit), add the review section, update `docs/activity.md`

### Review

Changes made:

- `static/styling.css`, two lines. Line 36 (body font on every element) and line 73 (display font on everything inside a button) now skip Streamlit's icon element, so the icon font is no longer replaced. Nothing else changed.

Checked by Claude before the user stopped the browser test:

- On the main page and the Design Demo page the collapse-sidebar icon now has the font "Material Symbols Rounded" and is 24 px wide (an icon, not a line of text).

Not checked:

- How it looks: no screenshot was looked at. Please check that the arrow is drawn and the logo is clear.
- Any other icon. Only the collapse button was on the two pages at the time of the check; expander arrows, icons in buttons and alerts were not seen.
- Whether line 73 needed the change. It is the same kind of rule with `!important`, so the exception was added without a test.

To note:

- Other rules in `static/styling.css` set a font on "everything inside" an element with `!important`: headings (line 53), metric label, value and delta (lines 66, 67, 69). An icon placed inside one of those would show its name as text again. No page does this today, so they were left alone.
- The test server (port 8766) and the headless browser that Claude started were closed. Nothing else was touched.
- `CLAUDE.MD` rule 11 was extended by the user during this task: avoid headless browsers when not strictly needed. Browser checks are left to the user from now on.
- Nothing is committed; the changes are staged for review.

### Check it yourself

```bash
source .venv/bin/activate
streamlit run app.py
```

Move the mouse over the top of the sidebar: a small double-arrow icon appears next to the logo, with no text over the logo.

---

## Task 9 - Refactor the font styling so icons cannot break (2026-10-12)

Prompt: screenshot of an expander on the Metric Catalogue page ("_arrow_right" drawn through the title "What the calculation types mean"), with "same bug, other location. New to-do --> full refactor to fix similar issues in whole app."

Status: done and staged, nothing committed. The browser check is for the user.

### Why Task 8 did not fix this

- Task 8 added an exception for the icon element `stIconMaterial`. The statement in Task 8 that every Streamlit icon has that name was wrong.
- Streamlit gives many icons their own name. The expander arrow is `stExpanderIcon`. Others in the installed version (1.65.0): `stAlertDynamicIcon`, `stToastDynamicIcon`, `stHeadingIcon`, `stMetricIcon`, `stElementToolbarButtonIcon`, `stDialogIcon`, `stExpanderIconCheck`, `stExpanderIconError`, the file-chip icons.
- A list of exceptions therefore never ends, and changes with every Streamlit version. The approach itself is the problem, not one missing name.

### Root cause

`static/styling.css` forces fonts on "every element inside X" in six places:

| Line | Rule | Font forced |
|---|---|---|
| 36 | everything in the app | body |
| 53 | everything in a heading | display, `!important` |
| 66 | everything in a metric label | display, `!important` |
| 67 | everything in a metric value | mono, `!important` |
| 69 | everything in a metric delta | mono, `!important` |
| 73 | everything in a button | display, `!important` |

Each of these also hits an icon that sits inside, and replaces the icon font.

### Proposed approach

Fonts are inherited: a font set on a container is used by everything inside it, except by elements that have their own font. Streamlit's icons have their own font. So the rule is: set a font on the container, never on "everything inside".

1. Give the fonts to Streamlit itself in `.streamlit/config.toml`: body font IBM Plex Sans, heading font Saira, code font IBM Plex Mono, with the 12 local font files declared under `[[theme.fontFaces]]`. Streamlit then applies them everywhere and keeps its icon font for icons. This is the supported way since Streamlit 1.46.
2. `static/styling.css`: remove line 36, and change the five other rules so they target the element (or its text paragraph), not everything inside. The Task 8 exceptions go out again, they are no longer needed.
3. Read every other rule in `static/styling.css` for the same pattern (a font, size or text style forced on all children) and fix those the same way.

### Plan

- [x] Read the project files and find why Task 8 was not enough
- [x] Write this plan
- [x] Plan verified by user ("go", decisions 1 and 2 as proposed)
- [x] `.streamlit/config.toml`: `font`, `headingFont`, `codeFont` and the `[[theme.fontFaces]]` entries for the 12 files in `static/fonts/`
- [x] `static/styling.css`: line 36 removed; the rules for headings, metric label / value / delta and buttons rewritten without "everything inside"; the Task 8 exceptions removed
- [x] `static/styling.css`: remaining rules read once for the same pattern; one more found and fixed (widget labels)
- [x] `docs/design_system.md`: the rule added to the Fonts section
- [x] Stage the changes (no commit), add the review section, update `docs/activity.md`
- [ ] Check in the browser: by the user (CLAUDE.MD rule 11), with the checklist below

### Checklist for the browser check (by the user)

Stop and restart `streamlit run app.py` first: the config change is not picked up by a page reload.


- Sidebar: collapse arrow next to the logo, and the expand arrow when the sidebar is closed
- Metric Catalogue: the arrow of the expander "What the calculation types mean", closed and open
- Tables: the toolbar icons that appear top right when the mouse is over a table (download, search, full screen)
- Select boxes, number fields (plus / minus) and the help "?" icons in the sidebar
- Buttons, tabs, headings, metric tiles on the Design Demo page: still Saira / IBM Plex as before
- The charts on the Design Demo page: unchanged (they have their own fonts and are not touched by this task)

### Decisions

1. Approach. Proposed: as above (fonts in `config.toml`, no "everything inside" rules). Alternative: keep the CSS as it is and add one rule that gives the icon font back to every element whose name contains "Icon". That is one line, but it is the same guessing as Task 8 and some of those elements are images, not font icons.
2. Scope. "Similar issues in whole app" is read as: every place where the theme CSS overrides something Streamlit needs for itself, in `static/styling.css`. The chart component (`components/sc_chart/`) and the HTML templates are not part of it; they run in their own frame and do not use Streamlit icons. Say so if you want those reviewed too.
3. Config changes need a restart of `streamlit run`; a page reload is not enough. Only relevant for the check.

---

### Review (Task 9)

Changes made:

- `.streamlit/config.toml`: body font IBM Plex Sans, heading font Saira, code font IBM Plex Mono, and the 12 local font files as `[[theme.fontFaces]]`. Streamlit now sets the fonts itself and keeps its icon font for icons.
- `static/styling.css`, seven rules:
  - removed: the body font on every element in the app (old line 36)
  - headings: `h1` to `h4` only, no longer everything inside a heading
  - metric label, value and delta: the text elements, no longer everything inside
  - buttons: the text paragraph, no longer everything inside (the Task 8 exceptions are gone)
  - widget labels: the text paragraph, no longer everything inside (found in the read-through; it forced a size and colour, not a font)
  - a note in the header comment with the rule
- `docs/design_system.md`: the rule in the Fonts section.
- No rule of the form "everything inside X" is left in `static/styling.css`.

Verified by Claude (no browser):

- Streamlit reads the config: the three fonts and 12 font entries; every font file named in it exists in `static/fonts/`.
- Headless app test: `app.py`, Metric Catalogue and Design Demo run without errors.

Not verified: anything visual. Whether the icons are drawn and whether the text still has the right fonts can only be seen in the browser. Please use the checklist above.

To note:

- Where the look may differ slightly from before: text inside a metric value or delta, and labels, now get the font through fewer rules. If a text shows in the wrong font or size, tell me which element.
- The `@font-face` block at the top of `static/styling.css` is kept. The same fonts are now also declared in the config; the block is still needed for the project's own classes (`.sc-...`) and does no harm.
- Not changed, but the same kind of risk: the button rule gives every Streamlit button the same padding and uppercase text with `!important`, including the small icon-only buttons (sidebar collapse, table toolbar). The icons themselves are safe from the uppercase, but the spacing of those buttons may be off. Look at this in the check.
- The chart component and the HTML templates were left out (decision 2).
- Nothing is committed; the changes are staged for review.

---

## Task 10 - Icon names still shown as text on buttons (2026-10-12)

Prompt: two screenshots (sidebar top with "keyboard_double_a..." over the logo; the "Rebuild from rules" button on the Metric Catalogue page with "expand_more" drawn through it), with "expander buttons are broken".

Status: done and staged, nothing committed. The user restarted the app and reported the icons fixed.

### What was found

- Both icons in the screenshots are Streamlit icons inside a button: the "collapse sidebar" arrow and the arrow of the popover button "Rebuild from rules".
- Reading the installed Streamlit (1.65.0): the icon element sets its own icon font, weight, letter spacing and text case. Nothing in the current `static/styling.css` targets that element any more. By the code, the Task 9 version should draw these icons.
- The app that is running has never loaded the Task 9 version:
  - `src/viz/theme.py` reads `static/styling.css` once and keeps it in memory (`@st.cache_data` on `_css()`). A page reload does not read the file again.
  - The running server (`streamlit run app.py`, port 8501) was started at 21:31:18. `static/styling.css` and `.streamlit/config.toml` were last changed at 21:40:28.
  - So the browser still gets the CSS from 21:31 or earlier. The same may be true for the Task 8 fix: Claude checked that one on its own test server, not on the user's.
- In the second screenshot the "Rebuild from rules" button has mixed-case text and a filled background. That button is `stPopoverButton`, which the button rules in the CSS do not match. This is a separate, small styling gap, not the icon bug.

Not confirmed: that the icons are drawn once the new CSS is loaded. This follows from reading the code only. Tasks 8 and 9 were also diagnosed by reading, and both were incomplete, so the check in step 1 comes before any change.

### Plan

- [x] Read `CLAUDE.MD`, `tasks/todo.md`, the last entries of `docs/activity.md`, the CSS, the theme code and the icon code of the installed Streamlit
- [x] Write this plan
- [x] Step 1, by the user: stop the running app (Ctrl+C) and start it again with `streamlit run app.py`, then look at the two places in the screenshots and at the Task 9 checklist. Result: "after point 1 --> fixed"
- [x] Plan verified by user: the answer above was taken as the go-ahead for decision 1 as proposed (not said in so many words, see the review)
- [x] `src/viz/theme.py`: remove `@st.cache_data` from `_css()`, so a change in `static/styling.css` shows after a page reload (one line; the file is 165 lines, reading it on every run costs nothing noticeable)
- [x] Only if icons are still wrong after step 1: not needed
- [x] Stage the changes (no commit), add the review section, update `docs/activity.md`

### Decisions

1. Remove the cache on the CSS. Proposed: yes. Alternative: keep it and restart the app after every CSS change.
2. If the icons are still broken after the restart: reading the code has now missed three times. Proposed: you open the browser inspector on one broken icon and send the "font-family" line it shows under "Computed", or you allow one headless browser check for this single question.
3. The popover button ("Rebuild from rules") does not get the button style (uppercase Saira, outline). Proposed: leave it out of this task; say so if you want it styled like the other secondary buttons.

### Review

Outcome: the icons were never broken by the Task 9 code. The running app kept the old CSS in memory; after a restart the user reported the icons fixed. This also confirms the Task 9 refactor in the browser for these two icons.

Changes made:

- `src/viz/theme.py`: `@st.cache_data` removed from `_css()`. The CSS file is now read on every run, so a change in `static/styling.css` shows after a page reload, without a restart.

Verified by Claude: the module still compiles. Nothing else was run and no browser was started.

To note:

- The user's answer was about step 1 only. The one-line change of decision 1 was applied on that basis; to undo it, put `@st.cache_data` back above `_css()` in `src/viz/theme.py`.
- A change in `.streamlit/config.toml` may still need a restart of the app.
- The rest of the Task 9 checklist (table toolbar icons, select boxes, number fields, help icons, fonts of buttons, tabs, headings and metric tiles) was not reported on.
- Decision 3 is open: the popover button "Rebuild from rules" does not have the style of the other buttons. Not changed.
- Nothing is committed; the changes are staged for review.

---

## Task 11 - Benchmarking engine and profile builder (2026-10-12)

Prompt: "New to-do: benchmarking engine and profile builder. 1. benchmarking --> each metric (existing or created) --> season p score and z-score. 2. profile builder --> select a position, create name and add metrics and weights per metric. here: check correlations for metrics in a profile. show a correlation matrix and flag strong correlations (>= 0.6) before saving the profile."

Status: done. Checked by the user in the browser on 2026-10-12: "looks ok". Staged, nothing committed.

### What is there already

- `foundation.season_rates` gives the season value of any catalogue metric, raw or calculated, per player x team x competition x role.
- `foundation.standardise` gives a z-score and a percentile within competition and role; low-sample rows are left out of the reference but still get a score. It is only used for one metric at a time in the Metric check tab, and it does not flip lower-is-better metrics.
- `src/benchmarks/` is empty. There is no stored table of season values.
- Timing, measured: all 819 metrics of `off_ball_runs` take about 19 seconds and give a 35 MB CSV of season values; 5 metrics of that file take 0.5 seconds. All 3,123 full-match metrics would take about a minute and about 135 MB for season values, about three times that with z-score and percentile.

### Proposed approach

Part 1, benchmarking engine (`src/benchmarks/engine.py`):

- One function: give it a list of metrics (file + name), get back one table with a row per player x team x competition x role and, per metric, the season value, the percentile (0 to 100) and the z-score. It reuses `season_rates` and `standardise`; metrics of several files are joined on the player-role keys.
- Lower is better is applied here: z-score and percentile are flipped, so that higher always means better. The season value itself is not changed.
- Reference group as today: within competition and role, low-sample players left out of the reference.
- New page `pages/1_Benchmarks.py`: pick a role, a competition and one or more metrics; see the table with value, percentile and z-score per player. The Metric check tab on the main page stays as the place to check one metric by hand.

Part 2, profile builder (`src/benchmarks/profiles.py`, `pages/2_Profile_Builder.py`):

- A profile = a name, a role, and a list of metrics each with a weight. Stored in `data/profiles.csv` (one row per profile and metric), tracked in git like the metric catalogue. Reading and writing go through `src/data/loaders.py`.
- The page: pick a role, type a name, pick metrics (from all files, raw and calculated), set a weight per metric in a small table. Existing profiles can be opened, changed and deleted.
- Correlation check, shown before the Save button: the correlation matrix of the chosen metrics over the players of that role, as a coloured table, and below it a list of the pairs at or above 0.6. Saving stays possible; when pairs are flagged, the page says so and asks for a tick "Save anyway".

### Plan

- [x] Read `CLAUDE.md`, `tasks/todo.md`, the last entries of `docs/activity.md`, the README and tech stack on benchmarks, and the current season calculation
- [x] Write this plan
- [x] Plan verified by user (answers to the seven decisions, see below)
- [x] `src/data/roles.py`, `app.py`: the role mapping is stored in `data/role_mapping.csv` and can be edited in the Role mapping tab; positions that are in no role are listed below the table
- [x] `src/benchmarks/engine.py`: the benchmark function (season value, percentile, z-score for any list of metrics; lower is better flipped), the profile score, and the stored table for all metrics that are in a profile
- [x] `pages/1_Benchmarks.py`: "Recalculate benchmarks", profile and competition pickers, the table with profile score and the metrics
- [x] `src/data/loaders.py`: read and write `data/role_mapping.csv` and `data/profiles.csv`
- [x] `src/benchmarks/profiles.py`: load, save and delete a profile; the list of strong pairs
- [x] `pages/2_Profile_Builder.py`: role, name, metrics, weights (sum has to be 1), correlation matrix with flags, Save
- [x] Verify: hand checks and headless app test of the pages (no browser)
- [x] Stage the changes, add the review section, update `docs/activity.md`

### Decisions

1. Calculate on demand or store everything. Proposed: on demand. The engine works for every metric, but only calculates the ones a page asks for (half a second for a handful). Alternative: a "Recalculate benchmarks" button that calculates all 3,123 metrics once (about a minute) and writes them to `data/derived/` (135 MB for values, about 400 MB with scores); every later page is then instant, but the file is large and has to be rebuilt after each change in the catalogue.
2. "Position" in the profile builder. Proposed: the seven role groups (CB, FB/WB, DM, CM, AM, W, CF), which is the grain of the player table. Alternative: the 18 raw positions (LCB, RWB, ...), which needs a new player table.
3. Reference group for percentile and z-score. Proposed: as today, within competition and role. Alternative: all five competitions together within the role.
4. Correlation. Proposed: Pearson correlation of the z-scores, over the players of that role in all five competitions who are not low sample. Using z-scores within competition takes out level differences between leagues. Flagged when the absolute value is 0.6 or more, so a strong negative correlation (-0.7) is flagged too.
5. Weights. Proposed: any positive number per metric; the page shows each weight as a share of the total. Stored as entered.
6. Not in this task, proposed for later: a profile score per player (the weighted mean of the z-scores of a profile). Say so if you want it now; it is a small addition to the Benchmarks page.
7. Page names. The README planned `1_Team_Benchmarks`, `2_Squad_Importance`, `3_Replacement_Finder`. The two new pages take numbers 1 and 2; the later pages move up. The README folder list is updated for this.

Answers (taken as the go-ahead):

1. "Yes --> calculate scores for all metrics that are in at least one profile." Applied: the "Recalculate benchmarks" button calculates those metrics and writes one table to `data/derived/`. The correlation check in the Profile Builder calculates its own metrics on the spot, because they are not in a profile yet.
2. "Make this table 'app --> role mapping' editable. --> show positions below table that are not in a role." Applied: the profile keeps using role groups, and the groups themselves can now be edited.
3. Within competition and role.
4. Correlation as proposed.
5. Weights as proposed, "also force that sum needs to be one": Save is switched off until the weights add up to 1.
6. Profile score: yes, built now.
7. Page numbers as proposed.

### Review

Changes made:

- Role mapping (`src/data/roles.py`, `app.py`, `src/data/foundation.py`): the mapping is read from `data/role_mapping.csv` if it exists, otherwise the default from the code. In the Role mapping tab the positions of a role can be changed and roles can be added or removed. Below the table: the positions that are in no role, and an error if a position is in two roles. "Save role mapping" writes the file and recalculates the player table with the sidebar settings.
- `src/benchmarks/engine.py`: `benchmark` (season value, percentile and z-score of any list of metrics, raw or calculated, within competition and role; flipped for lower-is-better metrics), `profile_score` (weighted mean of the z-scores, and its percentile) and `run_benchmarks` (all metrics that are in at least one profile, written to `data/derived/benchmarks_<timestamp>.csv`).
- `src/benchmarks/profiles.py`: profiles in `data/profiles.csv` (one row per profile and metric), save, delete, and the list of metric pairs with a correlation of 0.6 or more.
- `pages/1_Benchmarks.py`: "Recalculate benchmarks" in the sidebar; pick a profile, competitions, sample, and what to show per metric (percentile, z-score or season value). The table has the profile score and its percentile.
- `pages/2_Profile_Builder.py`: open an existing profile or start a new one; role, name, metrics from the whole catalogue, a weight per metric with an "Equal weights" button, the correlation matrix with strong cells marked and the strong pairs listed. Save is off until there is a name, the weights add up to 1, and, if pairs are flagged, "Save anyway" is ticked.
- `src/data/loaders.py`: reads and writes the two new files. `README.md`: folder list.

Verified by Claude (no browser; all test files were removed afterwards):

- Hand checks from the benchmark table for one centre-back: z-score and percentile of `psv99` (-0.779, 24.0) and of the lower-is-better `timetosprint` (flipped: -0.292, 38.7) equal the pipeline. The profile score equals the hand-calculated weighted mean of the z-scores. One correlation recalculated with numpy equals the matrix.
- Flag: total distance and high-speed-running distance for centre-backs come out at 0.60 and are flagged.
- Headless app test, Profile Builder: an existing profile loads into the form; Save is off with flagged pairs, and stays off with a sum of 1.3 even with the tick; after "Equal weights", the tick and a name it saves; delete works.
- Headless app test, Benchmarks: recalculation writes the table and the page shows 370 centre-backs with enough matches for the test profile; the three views run.
- Headless app test, role mapping: with LF and RF taken out of W the tab lists "Positions not in a role: LF, RF"; saving recalculates the player table (6,842 rows instead of 7,013).

Not verified: how the pages look in the browser, and editing the role table by hand (the test tool cannot type into the table; the mapping was changed through the file for the test).

Check it yourself:

```bash
source .venv/bin/activate
streamlit run app.py
```

1. "Profile Builder": pick a role, type a name, pick a few metrics, press "Equal weights", look at the correlations, save.
2. "Benchmarks": press "Recalculate benchmarks" and pick the profile.
3. Main page, tab "Role mapping": take a position out of a role and see it listed below the table. Only press "Save role mapping" if you want to keep the change.

To note:

- No profile and no role mapping file is stored yet; the app starts with the default roles and an empty profile list.
- After a profile is saved with new metrics, or the role mapping or the catalogue changes, "Recalculate benchmarks" has to be pressed again. The page says so when a metric is missing. The profile score always uses the weights as stored at that moment.
- A profile stores its role by name. If a role is renamed or removed in the role mapping, its profiles have to be saved again under the new role.
- Players in a position without a role are left out of the player table and of all benchmarks.
- Weights are checked to three decimals: 0.333 three times (0.999) is refused, 0.333 + 0.333 + 0.334 is accepted. "Equal weights" always works.
- The correlation uses the flipped z-scores, so for a lower-is-better metric the sign is that of "better", not of the raw value.
- A player without a value for one of the profile's metrics gets no profile score.
- The metric picker lists all 3,123 full-match metrics; type to search.
- Nothing is committed; the changes are staged for review.

---

## Task 12 - Player profile page (2026-10-12)

Prompt: "To-do: 'player profile' page. 1. conditional selecting of season --> competition --> role --> player. 2. show index scores for different profiles for that role (if there are any). 3. show per metric category what the strengths and weaknesses are for this player --> eg for ALL metrics: calculate z-scores for that player with the given filters (season and competition and role) for all metrics so we can sort through them and explore."

Status: plan written, waiting for the user to verify. No code changed.

### What is there already

- `engine.benchmark` gives season value, percentile and z-score for any list of metrics, within competition and role, flipped for lower-is-better metrics. `engine.profile_score` gives the profile score and its percentile. Both can be reused as they are.
- The stored benchmark table (`data/derived/benchmarks_...csv`) only holds the metrics that are in a profile (16 today), not all metrics.
- Three profiles are stored: two for DM, one for CM. The other five roles have none.
- The catalogue has six categories over 11 files: Off-ball runs (819 full-match metrics), Passing (1,072), Passing options (476), Physical (51), Possessions (48), Pressure (660). 3,126 in total.
- The data holds one season (2024/2025). The player table has no season column; the season name is in `competition_editions.csv`.
- A player has one row per team, competition and role. 126 players played for two teams.

### What was measured

For Eredivisie, role DM (180 rows, 57 with enough matches):

| File | Metrics | Time | Metrics without a z-score |
|---|---|---|---|
| off_ball_runs | 819 | 24 s | 53 |
| pressing_engagements | 95 | 3 s | 8 |
| physical | 51 | 2 s | 0 |

- Calculating for one competition and role is not faster than for all of them: the time goes into reading the raw file and the season calculation. All categories together take one to two minutes.
- A metric has no z-score when every reference player has the same value (an event that never happens for that role).
- The largest z-score among players with enough matches is 7.5: rare events give a few players extreme scores.

### Proposed approach

New page `pages/3_Player_Profile.py`. No change to the engine or the data layer, apart from one small function for the long table (below).

1. Selection, four boxes in a row, each one limited by the one before: season, competition, role, player. The season comes from `competition_editions.csv`, joined on the competition id. The player box lists the players of that competition and role as "Name (Team)", sorted by matches, with low-sample players marked.
2. Header: team, role, matches, included matches, minutes, and a low-sample notice when it applies.
3. Profile scores: one row per profile of that role, with the profile score and its percentile within competition and role, sorted by score. If the role has no profile, one line says so. If a profile has a metric that is not in the stored benchmarks, the page asks for "Recalculate benchmarks", as the Benchmarks page does.
4. Strengths and weaknesses:
   - A category box (the six categories). The z-scores of that category are calculated when it is picked and kept in memory, so the next player in the same category is instant.
   - Per category: the 10 highest and the 10 lowest z-scores of this player side by side ("Strengths", "Weaknesses").
   - Below: the full table to explore, one row per metric: file, metric, definition, season value, percentile, z-score. Sortable by clicking a column, with a search field on the metric name.
   - `src/benchmarks/engine.py`: one function `player_metrics` that turns the benchmark row of one player into this long table.

### Plan

- [x] Read `CLAUDE.md`, `tasks/todo.md`, the last entries of `docs/activity.md`, the Benchmarks and Profile Builder pages, the engine and the data layer
- [x] Time the calculation for all metrics of a file
- [x] Write this plan
- [ ] Plan verified by user
- [ ] `src/benchmarks/engine.py`: `player_metrics` (one player's row to a table with one row per metric)
- [ ] `pages/3_Player_Profile.py`: the four selection boxes and the header
- [ ] `pages/3_Player_Profile.py`: profile scores for the role
- [ ] `pages/3_Player_Profile.py`: category box, strengths and weaknesses, the full table
- [ ] `README.md`: folder list
- [ ] Verify: hand check of one z-score and one profile score against the Benchmarks page; headless app test of the page (no browser)
- [ ] Stage the changes, add the review section, update `docs/activity.md`

### Decisions

1. Calculating all metrics. Proposed: per category, when it is picked, kept in memory until the app restarts or the player table changes. First time per category: 2 to 60 seconds (Passing is the slowest), after that instant. Alternative: "Recalculate benchmarks" calculates all 3,126 metrics once (one to two minutes) and writes them to `data/derived/` (about 400 MB); every page is then instant, but the file is large and has to be rebuilt after every change in the catalogue or the role mapping.
2. Season. The data has one season, so the season box has one choice. Proposed: build it anyway, read from `competition_editions.csv`, so a second season works without a change to this page.
3. A player with two teams in the same competition and role. Proposed: two entries in the player box, "Name (Team)", each with its own scores. This is the grain of the player table. Alternative: one entry per player with the teams added up, which needs a new player table.
4. Low-sample players. Proposed: they can be picked, are marked in the box and get a notice on the page. Their z-scores can be extreme.
5. What counts as a strength. Proposed: the 10 highest and 10 lowest z-scores per category, no cut-off value. Because of the rare events measured above, the lists can be led by metrics that hardly ever happen. Option to add now: leave out metrics where fewer than a set share of the reference players has a value above zero. Proposed: not now; first look at the lists.
6. Profile scores. Proposed: from the stored benchmark table, so the numbers are the same as on the Benchmarks page. Alternative: calculated on the spot, which never needs "Recalculate benchmarks" but takes a few seconds per role.
7. Charts. Proposed: tables only in this task, as on the Benchmarks and Profile Builder pages. A radar of the profile scores or a dot strip per metric from the design system can follow as its own task.

---

## Where we are (end of session 2026-10-12)

Everything below is staged in git; nothing is committed. The commit is for the user.

Done:

- Task 1: project set-up.
- Task 2: Step 0 data foundation (loaders, role mapping, inventory, player tables, app page).
- Task 3: Metric catalogue page and `data/metric_catalogue.csv`.
- Task 5: match-by-match rates, match filter (default 60 minutes), low-sample flag on included matches (default 5).
- Tasks 6 and 7: design system and ECharts visuals.
- Tasks 8 to 10: icon and font fixes; the theme CSS is no longer cached.
- Task 4: calculated season metrics in their own tab (average of best x, ratio). Checked by the user.
- Task 11: benchmarking engine, profile builder with correlation check, profile score, editable role mapping. Checked by the user.

Stored by the user in the app on 2026-10-12, and staged:

- `data/metric_catalogue.csv`: two calculated metrics, `timetohsr_best3` and `timetosprint_best3`.
- `data/profiles.csv`: two profiles for role DM, "Ball Winning Midfielder" (5 metrics) and "Deep Lying Playmaker" (4 metrics).
- `data/role_mapping.csv`: the role mapping, equal to the default.

Next, according to the README build order: the base template, the data contract and the first display template (radar), then team benchmarks (style and quality).

Open points to pick up:

- `.agents/` and `.claude/` (the Streamlit skill, a link into `.venv`) are untracked: add to git or to `.gitignore`.
- `README.md` and `tech_stack.md` still describe the older rules (per-30 from season sums, a minutes threshold). They were not updated for Task 5.
- `src/viz/charts.py` and `plotly` are no longer used by any page (Task 7, decision 1).
- The popover button "Rebuild from rules" does not have the style of the other buttons (Task 10, decision 3).
- Most of the Task 9 browser checklist was never reported on (table toolbar icons, select boxes, number fields, help icons).
- Editing a cell in a table and saving it is not covered by an automated test (catalogue page, role mapping).
- The Benchmarks and Profile Builder pages show tables only; no chart from the design system is used on them yet.
