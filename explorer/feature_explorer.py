#!/usr/bin/env -S uv run --locked --script

# /// script
# dependencies = [
#     "marimo",
#     "matplotlib==3.11.0",
#     "numpy==2.5.0",
#     "pandas==3.0.3",
#     "pyyaml==6.0.3",
#     "scienceplots==2.2.2",
#     "seaborn==0.13.2",
#     "requests",
#     "ruamel.yaml==0.18.15",
#     "tqdm"
# ]
# requires-python = ">=3.12"
# ///

import marimo

__generated_with = "0.23.15"
app = marimo.App(width="columns", layout_file="layouts/feature_explorer.grid.json")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import seaborn as sns
    import pandas as pd
    import numpy as np

    from matplotlib.patches import Ellipse
    from matplotlib.lines import Line2D
    import matplotlib.pyplot as plt
    import scienceplots


    from explorer_support.colors import ENV_TO_COLOR
    from explorer_support.feature_fetcher import (
        EXPERIMENTS,
        RESULT_FILES,
        fetch_feature_table,
    )
    from explorer_support.feature_explanations import (
        EDITABLE_FIELDS,
        Path,
        load_feature_explanations,
        update_feature_explanation,
    )

    return (
        fetch_feature_table,
        ENV_TO_COLOR,
        EXPERIMENTS,
        RESULT_FILES,
        Ellipse,
        Line2D,
        EDITABLE_FIELDS,
        load_feature_explanations,
        mo,
        np,
        pd,
        plt,
        sns,
        update_feature_explanation,
    )


@app.cell
def _(plt):

    plt.style.use(["science", "no-latex"])

    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
        'font.size': 8,
        'axes.labelsize': 8,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'lines.linewidth': 0.8,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
    })
    return


@app.cell
def _(fetch_feature_table):
    # from zenodo_fetcher import fetch_labels
    # CSV_LABELS   = fetch_labels()
    # CSV_FEATURES = 'features.csv'

    # df_labels   = pd.read_csv(CSV_LABELS)
    # df_features = pd.read_csv(CSV_FEATURES)
    # yeast = pd.merge(df_labels, df_features, on='id')
    yeast = fetch_feature_table()
    return (yeast,)


@app.cell
def _(RESULT_FILES, load_feature_explanations):
    explanations_path = RESULT_FILES.explanations
    features = load_feature_explanations(explanations_path)
    return explanations_path, features


@app.cell
def _(ui_d1, ui_d2, ui_d3, ui_e1, ui_e2, yeast):
    selected_days = [
        day
        for day, selected in (
            (1, ui_d1.value),
            (2, ui_d2.value),
            (3, ui_d3.value),
        )
        if selected
    ]
    selected_experiments = [
        experiment
        for experiment, selected in (
            (1, ui_e1.value),
            (2, ui_e2.value),
        )
        if selected
    ]
    df = yeast[
        yeast.day.isin(selected_days)
        & yeast.experiment.isin(selected_experiments)
    ]
    return df, selected_days, selected_experiments


@app.cell
def _(mo):
    ui_e1 = mo.ui.checkbox(value=True, label='Experiment 1')
    ui_e2 = mo.ui.checkbox(value=True, label='Experiment 2')
    save_revision, set_save_revision = mo.state(0)
    ui_range = range_slider = mo.ui.range_slider(start=0, stop=1, step=.01, value=[.01, .99],label='Quantiles')


    return save_revision, set_save_revision, ui_e1, ui_e2


@app.cell
def _(mo, scenario_options):
    default_scenario = next(
        label for label, scenario_id in scenario_options.items()
        if scenario_id == "Day_3"
    )
    ui_ex = mo.ui.dropdown(
        scenario_options,
        value=default_scenario,
        full_width=True,
    )
    ui_covariance = mo.ui.checkbox(
        value=True,
        label="Show covariance ellipses",
    )
    return ui_ex, ui_covariance


@app.cell
def _(
    Path,
    RESULT_FILES,
    explanations_path,
    fx,
    fx_info,
    fy,
    fy_info,
    mo,
    ui_d1,
    ui_d2,
    ui_d3,
    ui_e1,
    ui_e2,
    ui_edit,
    ui_ex,
    ui_covariance,
    save_revision,
    set_save_revision,
    update_feature_explanation,
    x_editor,
    y_editor,
):
    has_changes = ui_edit.value and any(
        str(values.get(field) or "").strip()
        != str(entry.get(field) or "").strip()
        for entry, values in (
            (fx_info, x_editor.value),
            (fy_info, y_editor.value),
        )
        for field in values
    )
    displayed_entries = (
        (x_editor.value, y_editor.value)
        if ui_edit.value
        else (fx_info, fy_info)
    )
    remaining_todos = sum(
        1
        for values in displayed_entries
        for value in values.values()
        if not str(value or "").strip() or "TODO" in str(value or "").upper()
    )

    def save_both(_):
        for feature_id, entry, values in (
            (fx, fx_info, x_editor.value),
            (fy, fy_info, y_editor.value),
        ):
            if any(not str(value).strip() for value in values.values()):
                raise ValueError(f"All fields are required for {feature_id}")
            saved = update_feature_explanation(explanations_path, feature_id, values)
            entry.update(saved)
        set_save_revision(save_revision() + 1)

    save_button = mo.ui.button(
        label="Update file",
        kind="success",
        on_click=save_both,
        disabled=not has_changes,
    )
    result_label = (
        "recomputed results"
        if RESULT_FILES.source == "pipeline"
        else "paper results"
    )
    explanations_relative_path = explanations_path.relative_to(
        Path(__file__).resolve().parent,
        walk_up=True,
    )
    annotation_update_control = (
        mo.vstack((
            save_button,
            mo.md(f"<small>Editing: `{explanations_relative_path}`</small>"),
        ), gap=0.1)
        if ui_edit.value
        else mo.md(
            "<div aria-hidden='true' "
            "style='width: 5.5rem; height: 2.25rem;'></div>"
        )
    )
    mode_control = mo.vstack((
        mo.md(f"Feature explanations — **{result_label}**"),
        mo.hstack((
            mo.md("View"),
            ui_edit,
            mo.md("Annotate"),
            annotation_update_control,
        ), justify="start"),
    ), gap=0.25)
    todo_status = (
        f" <span style='color: #c62828;'>"
        f"({remaining_todos} TODO{'s' if remaining_todos != 1 else ''} "
        "left in descriptions)"
        "</span>"
        if remaining_todos
        else ""
    )
    scenario_control = mo.vstack((
        mo.md(f"<strong>Scenario</strong>{todo_status}"),
        ui_ex,
    ), gap=0.25)
    mo.vstack((
        # ui_range,
        mode_control,
        mo.md("<div style='height: 1rem'></div>"),
        scenario_control,
        mo.hstack((ui_d1, ui_d2, ui_d3), justify='start'),
        mo.hstack((ui_e1, ui_e2), justify='start'),
        ui_covariance,
    ))
    return


@app.cell
def _(EXPERIMENTS, ui_ex):
    exp_selected = EXPERIMENTS[ui_ex.value]
    fx,fy = exp_selected['features']
    return exp_selected, fx, fy


@app.cell
def _(EXPERIMENTS):
    scenario_options = {
        details["description"]: scenario_id
        for scenario_id, details in EXPERIMENTS.items()
    }
    if len(scenario_options) != len(EXPERIMENTS):
        raise ValueError("Scenario descriptions must be unique")
    return (scenario_options,)


@app.cell
def _(
    EDITABLE_FIELDS,
    explanations_path,
    mo,
    ui_edit,
    update_feature_explanation,
):
    def feature_editor(axis, feature_id, entry):
        labels = {
            "title": "",
            "image": "",
            "biology": "",
            "technical": "",
            "filter": "",
            "stats": "",
        }
        fields = {
            field: (
                mo.ui.text_area(
                    value=str(entry[field]).strip(),
                    label=labels[field],
                    rows=3,
                    full_width=True,
                )
                if field in {"image", "biology", "technical"}
                else mo.ui.text(
                    value=str(entry[field]).strip(),
                    label=labels[field],
                    full_width=True,
                )
            )
            for field in EDITABLE_FIELDS
        }

        vertical_fields = mo.ui.batch(
            mo.md(f"""
            <div style="display: grid; grid-template-columns: auto 1fr; align-items: center; gap: 1rem;">
              <strong>{axis}-axis</strong>
              {{title}}
            </div>

            **Observed visual pattern:**

            {{image}}

            **Possible biological interpretation:**

            {{biology}}

            **Technical definition:**

            {{technical}}

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
              <div><strong>Filter:</strong><br>{{filter}}</div>
              <div><strong>Statistic:</strong><br>{{stats}}</div>
            </div>
            <div style="color: #888; margin-top: 0.2rem;"><code style="color: inherit;">{feature_id}</code></div>
            """),
            fields,
        )
        return vertical_fields

    def feature_card(axis, feature_id, entry):
        image_text = entry["image"].strip()
        first_sentence, separator, _ = image_text.partition(". ")
        summary = f"{first_sentence}." if separator else ""
        summary_md = f"*{summary}*" if summary else ""
        card = mo.md(f"""
    ### ${axis}$-axis $\\rightarrow$ {entry['title']}

    {entry['image']}


    **Possible biological interpretation:**

    {entry['biology']}

    **Technical definition:**

    {entry['technical']}

        """)

        if not ui_edit.value:
            return card
        return feature_editor(axis, feature_id, entry)

    return (feature_card,)


@app.cell
def _(feature_card, fx, fx_info):
    x_editor = feature_card("x", fx, fx_info)
    x_editor
    return (x_editor,)


@app.cell
def _(feature_card, fy, fy_info):
    y_editor = feature_card("y", fy, fy_info)
    y_editor
    return (y_editor,)


@app.cell
def _(features, fx, fy):
    fx_info = features[fx]
    fy_info = features[fy]
    return fx_info, fy_info


@app.cell
def _(fx, fy, yeast):
    xlim = tuple(yeast[fx].quantile([0.003, 0.997]))
    ylim = tuple(yeast[fy].quantile([0.003, 0.997]))
    # xlim = yeast[fx].quantile(ui_range.value)
    # ylim = yeast[fy].quantile(ui_range.value)

    # ylim = (0.3,0.95) # for pub
    return xlim, ylim


@app.cell
def _(
    ENV_TO_COLOR,
    Line2D,
    Path,
    add_ellipse,
    df,
    fx,
    fx_info,
    fy,
    fy_info,
    mo,
    selected_days,
    selected_experiments,
    sns,
    ui_ex,
    ui_covariance,
    xlim,
    ylim,
):
    mo.stop(not selected_days, mo.md("Select at least one day."))
    mo.stop(not selected_experiments, mo.md("Select at least one experiment."))
    g = sns.JointGrid(
        data=df,
        x=fx,
        y=fy,
        height=7,
        ratio=4,
        space=0.04,
        xlim=xlim,
        ylim=ylim,
        marginal_ticks=False,
    )

    legend_handles = []
    for medium in ENV_TO_COLOR:
        medium_data = df[df["medium"] == medium]
        if medium_data.empty:
            continue
        color = ENV_TO_COLOR[medium]
        for experiment, group in medium_data.groupby("experiment", sort=True):
            marker = "o" if experiment == 1 else "x"
            linestyle = "-" if experiment == 1 else "--"
            legend_handles.append(Line2D(
                [0],
                [0],
                color=color,
                marker=marker,
                linestyle=linestyle,
                linewidth=0.8,
                markersize=5,
                label=f"{medium} (Experiment {int(experiment)})",
            ))
            g.ax_joint.scatter(
                group[fx],
                group[fy],
                s=28,
                marker=marker,
                color=color,
                alpha=0.28,
                linewidths=0.45 if experiment == 2 else 0,
                zorder=1,
            )
            if ui_covariance.value:
                add_ellipse(
                    g.ax_joint,
                    group[fx],
                    group[fy],
                    n_std=1,
                    facecolor=color,
                    edgecolor=color,
                    linewidth=0.8,
                    linestyle=linestyle,
                    alpha=0.20,
                    zorder=2,
                )
            sns.kdeplot(
                data=group,
                x=fx,
                ax=g.ax_marg_x,
                color=color,
                linestyle=linestyle,
                linewidth=0.8,
                fill=False,
                clip=xlim,
                cut=0,
                warn_singular=False,
            )
            sns.kdeplot(
                data=group,
                y=fy,
                ax=g.ax_marg_y,
                color=color,
                linestyle=linestyle,
                linewidth=0.8,
                fill=False,
                clip=ylim,
                cut=0,
                warn_singular=False,
            )

    g.ax_joint.grid(
        True,
        linestyle=":",
        color="0.55",
        alpha=0.55,
        linewidth=0.25,
    )
    g.ax_joint.set_xlabel(fx_info["title"])
    g.ax_joint.set_ylabel(fy_info["title"])
    g.ax_joint.set_title("")
    g.ax_joint.legend(
        handles=legend_handles,
        frameon=False,
        loc="best",
        fontsize=7,
    )
    g.ax_joint.tick_params(axis="both", labelsize=7, width=0.5, length=2.5)
    for marginal_axis in (g.ax_marg_x, g.ax_marg_y):
        marginal_axis.tick_params(
            axis="both",
            which="both",
            bottom=False,
            top=False,
            left=False,
            right=False,
            labelbottom=False,
            labeltop=False,
            labelleft=False,
            labelright=False,
        )
    for axis in (g.ax_joint, g.ax_marg_x, g.ax_marg_y):
        for spine in axis.spines.values():
            spine.set_linewidth(0.5)
    g.figure.subplots_adjust(
        left=0.15,
        right=0.97,
        bottom=0.14,
        top=0.97,
    )

    days_slug = "-".join(map(str, selected_days))
    experiments_slug = "-".join(map(str, selected_experiments))
    suffix = "_covariance" if ui_covariance.value else ""
    filename = f"{ui_ex.value}_days-{days_slug}_experiments-{experiments_slug}{suffix}"
    figures_dir = Path(__file__).resolve().parent / "figures"
    figures_dir.mkdir(exist_ok=True)

    for extension in ("png", "pdf"):
        g.figure.savefig(
            figures_dir / f"{filename}.{extension}",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.02,
        )

    g
    return


@app.cell
def _(Ellipse, np):
    def add_ellipse(ax, x, y, n_std=2, **kwargs):
        points = np.column_stack((x, y))
        points = points[np.isfinite(points).all(axis=1)]
        if len(points) < 2:
            return

        cov = np.cov(points, rowvar=False)
        mean = points.mean(axis=0)
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        vals, vecs = vals[order], vecs[:, order]
        vals = np.clip(vals, 0, None)
        angle = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
        width, height = 2 * n_std * np.sqrt(vals)
        ell = Ellipse(xy=mean, width=width, height=height, angle=angle, **kwargs)

        ax.add_patch(ell)

    return (add_ellipse,)


@app.cell
def _(EDITABLE_FIELDS, EXPERIMENTS, features, mo, ui_ex):
    scenario_day_defaults = {
        "Day_3": {3},
        "Day_1_merged_Day_2_omitted": {1, 3},
    }
    selected_scenario_days = scenario_day_defaults.get(ui_ex.value, {1, 2, 3})
    ui_d1 = mo.ui.checkbox(value=1 in selected_scenario_days, label="Day 1")
    ui_d2 = mo.ui.checkbox(value=2 in selected_scenario_days, label="Day 2")
    ui_d3 = mo.ui.checkbox(value=3 in selected_scenario_days, label="Day 3")

    selected_feature_ids = EXPERIMENTS[ui_ex.value]["features"]
    incomplete_fields = [
        (feature_id, field)
        for feature_id in selected_feature_ids
        for field in EDITABLE_FIELDS
        if (
            not str(features[feature_id].get(field) or "").strip()
            or "TODO" in str(features[feature_id].get(field) or "").upper()
        )
    ]
    initial_remaining_todos = len(incomplete_fields)
    ui_edit = mo.ui.switch(value=initial_remaining_todos > 0)
    return ui_d1, ui_d2, ui_d3, ui_edit


if __name__ == "__main__":
    import subprocess
    import sys

    try:
        returncode = subprocess.run(
            [
                sys.executable,
                "-m",
                "marimo",
                "-y",
                "run",
                "--no-token",
                "--no-sandbox",
                __file__,
                *sys.argv[1:],
            ],
            check=False,
        ).returncode
    except KeyboardInterrupt:
        returncode = 130
    raise SystemExit(returncode)
