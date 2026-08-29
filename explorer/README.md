# Mito Explorer

This repository has two applications, both runnable from the repository root:

- `feature_explorer.py`
- `patch_explorer.py`

Both applications select their result files as one complete set. If the
sibling pipeline has produced `results/features/features.csv`,
`results/scenarios_features.yaml`, and `results/feature_explanations.yaml`, the
applications use those recomputed files. Otherwise they use the paper-result
copies in this directory. An incomplete
pipeline result set is never mixed with paper-result files; the applications
warn and use the complete paper-result set instead.

## Notes on `uv`

Both applications are Python-based and use `uv` to install their dependencies
in isolated environments, avoiding a separate manual setup step.

If your system does not have `uv` installed, please install it following the [official instructions](https://docs.astral.sh/uv/getting-started/installation/).
Since `uv` is a relatively new package manager, you may also want to
[read about it](https://docs.astral.sh/uv/) first.

## Feature Explorer

Opens an interactive [`marimo`](https://marimo.io)-based application for
exploring pairs of mitochondrial image features. The app combines a joint
scatter plot, marginal KDEs, feature explanations, and an annotation editor.

On macOS, Linux, or Git Bash:

```console
./feature_explorer.py
```

On Windows PowerShell or Command Prompt:

```console
.\feature_explorer.cmd
```

The executable script uses `uv` and `feature_explorer.py.lock` to create the
locked environment, then starts the Marimo application. The Windows launcher
invokes the same script without relying on Unix shebang support.

### Controls

- **View / Annotate** switches between rendered explanations and editable
  annotation forms. Whenever a scenario is selected, the application starts in
  Annotate mode if any editable explanation field for either of its features is
  blank or contains `TODO`; otherwise it starts in View mode.
- **Scenario** selects a feature pair. Its labels come from the descriptions in
  `scenarios_features.yaml`. Selecting **Day 3** checks only Day 3; selecting
  **Day 1 merged, Day 2 absent** checks Days 1 and 3. Other scenarios check all
  days. Scenario changes do not alter the experiment filters.
- **Day 1–3** and **Experiment 1–2** independently filter the plotted samples.
- **Show covariance ellipses** controls the experiment-specific covariance
  ellipses and is enabled by default.

At least one day and one experiment must remain selected.

### Plot encoding

Growth medium is represented by color. Experiment is represented independently:

| Experiment | Scatter marker | KDE and ellipse line |
| --- | --- | --- |
| 1 | Circle | Solid |
| 2 | `x` | Dashed |

The legend combines medium and experiment. Marginal KDEs and covariance
ellipses are calculated separately for every visible medium–experiment group.
Axis labels use the human-readable feature titles, while limits are shared
across filter selections and use the 0.003–0.997 quantiles of the complete
feature table.

Each rendered plot is saved automatically as PNG and PDF in `figures/`. The
filename records the scenario ID, selected days, selected experiments, and
whether covariance ellipses were enabled.

### Editing feature explanations

Switch from **View** to **Annotate** to edit both currently displayed feature
explanations. The feature IDs are read-only. **Update file** validates all
fields and writes both entries to the active `feature_explanations.yaml` while
preserving YAML scalar formatting. In Annotate mode, the relative path of the
file being edited is displayed below the button. Each file replacement is
atomic.

Switching back to View mode renders the saved Markdown explanations.

### Data files

The bundled paper-result files are stored together under `paper_results/`. The
Feature Explorer reads:

- `paper_results/features.csv` for extracted feature values;
- the shared `yeast-mitochondria-patches/metadata.csv` for image IDs,
  experiment IDs, days, and growth media;
- `paper_results/scenarios_features.yaml` for scenario descriptions and feature
  pairs;
- `paper_results/feature_explanations.yaml` for displayed and editable
  explanations.

The paper feature table is intentionally narrower than a fresh pipeline output:
it contains only the features retained for the paper's selected scenarios,
whereas `pipeline/results/features/features.csv` contains the wider extracted
feature table. The paper explanations file contains completed manual
annotations. Its YAML keys may appear in a different order than those in the
pipeline-generated template; entries should be matched by feature key, not by
position.

The interface labels the selected set as **paper results** or **recomputed
results**. When recomputed results are selected, annotation updates are written
to the pipeline's `results/feature_explanations.yaml`. The pipeline initially
generates this file as a template with `TODO` placeholders; completing its
explanatory text is an intentional manual step.

If the metadata file is missing, the application downloads it through
`zenodo_fetcher.py`.

## Patch Explorer

Opens a resizable interactive window of image thumbnails positioned by their
selected features. The window title shows the selected scenario.

On macOS, Linux, or Git Bash:

```console
./patch_explorer.py
```

On Windows PowerShell or Command Prompt:

```console
.\patch_explorer.cmd
```

The executable script invokes `uv` through its shebang and uses the checked-in
lockfile. The Windows launcher invokes the same command without relying on Unix
shebang support.

The viewer uses the same selected features and scenarios result set as Feature
Explorer, together with the shared metadata file. It builds
thumbnails from corresponding images and masks under
`yeast-mitochondria-patches/images/` and
`yeast-mitochondria-patches/masks/`; missing archives are downloaded through
`zenodo_fetcher.py`.

By default, Explorer and the sibling feature pipeline share
`yeast-mitochondria-patches/` beside their repository directories. Set
`YEAST_MITOCHONDRIA_PATCHES_DIR` to an absolute path to use another location.
Both applications must receive the same value when the variable is overridden.

Patch Explorer uses the `Day_3` scenario by default. Select another scenario by
its ID:

```console
./patch_explorer.py --scenario YPGal
```

List the valid IDs together with their human-readable descriptions:

```console
./patch_explorer.py --list-scenarios
```

On Windows, the same arguments are forwarded by the launcher:

```console
.\patch_explorer.cmd --scenario YPGal
```

The selected scenario ID and description are included in the viewer window
title.

### Mouse

| Input | Action |
| --- | --- |
| Left-drag | Pan |
| Right-drag up | Zoom in |
| Right-drag down | Zoom out |

### Keyboard

| Key | Action |
| --- | --- |
| <kbd>C</kbd> | Toggle between monochrome green and color-coded patches |
| <kbd>1</kbd>, <kbd>2</kbd>, <kbd>3</kbd> | Toggle patches from day 1, 2, or 3 |
| <kbd>[</kbd> | Toggle Experiment 1 |
| <kbd>]</kbd> | Toggle Experiment 2 |
| ![D](https://img.shields.io/badge/-D-CC0000) | Toggle YPD |
| ![L](https://img.shields.io/badge/-L-CC6E00) | Toggle YPGal |
| ![Y](https://img.shields.io/badge/-Y-00CC33) | Toggle YPGly |
| ![A](https://img.shields.io/badge/-A-007ACC) | Toggle AS |
| ![S](https://img.shields.io/badge/-S-8800CC) | Toggle SD |
| <kbd>0</kbd> | Reset all day, medium, and experiment filters |
| <kbd>Q</kbd> or <kbd>Esc</kbd> | Quit |

Day, medium, and experiment shortcuts act as independent toggles and can be
combined. Both experiments are visible initially; the window title reports the
currently active days and experiments.

### Color coding

The viewer starts in monochrome green. Press <kbd>C</kbd> to tint each patch by
growth medium and day according to `colors.py`. Each medium has a distinct hue,
and later days use progressively darker shades:

| Medium | Day 1 | Day 2 | Day 3 |
| --- | --- | --- | --- |
| YPD | ![Day 1](https://img.shields.io/badge/-Day%201-F29191) | ![Day 2](https://img.shields.io/badge/-Day%202-E64343) | ![Day 3](https://img.shields.io/badge/-Day%203-CC0000) |
| YPGal | ![Day 1](https://img.shields.io/badge/-Day%201-F2C491) | ![Day 2](https://img.shields.io/badge/-Day%202-E69543) | ![Day 3](https://img.shields.io/badge/-Day%203-CC6E00) |
| YPGly | ![Day 1](https://img.shields.io/badge/-Day%201-91F2A5) | ![Day 2](https://img.shields.io/badge/-Day%202-43E669) | ![Day 3](https://img.shields.io/badge/-Day%203-00CC33) |
| AS | ![Day 1](https://img.shields.io/badge/-Day%201-91C8F2) | ![Day 2](https://img.shields.io/badge/-Day%202-43A0E6) | ![Day 3](https://img.shields.io/badge/-Day%203-007ACC) |
| SD | ![Day 1](https://img.shields.io/badge/-Day%201-D491F2) | ![Day 2](https://img.shields.io/badge/-Day%202-B443E6) | ![Day 3](https://img.shields.io/badge/-Day%203-8800CC) |

---
