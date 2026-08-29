"""Select one complete set of Explorer result files."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResultFiles:
    features: Path
    scenarios: Path
    explanations: Path
    source: str
    root: Path

    @property
    def description(self) -> str:
        label = (
            "recomputed pipeline results"
            if self.source == "pipeline"
            else "bundled paper results"
        )
        return f"{label} ({self.root})"


def _pipeline_files(root: Path) -> ResultFiles:
    return ResultFiles(
        features=root / "features" / "features.csv",
        scenarios=root / "scenarios_features.yaml",
        explanations=root / "feature_explanations.yaml",
        source="pipeline",
        root=root,
    )


def _paper_files(root: Path) -> ResultFiles:
    return ResultFiles(
        features=root / "features.csv",
        scenarios=root / "scenarios_features.yaml",
        explanations=root / "feature_explanations.yaml",
        source="paper",
        root=root,
    )


def _missing(files: ResultFiles) -> list[Path]:
    return [
        path
        for path in (files.features, files.scenarios, files.explanations)
        if not path.is_file()
    ]


def resolve_result_files(
    app_dir: Path | None = None,
    pipeline_results: Path | None = None,
) -> ResultFiles:
    """Prefer a complete pipeline result set; otherwise use the paper set."""
    app_dir = (app_dir or Path(__file__).resolve().parent.parent).resolve()
    if pipeline_results is not None:
        candidates = [pipeline_results.resolve()]
    else:
        candidates = [
            app_dir.parent / "pipeline" / "results",
            app_dir.parent / "mito-feature-pipeline" / "results",
        ]

    incomplete: list[tuple[Path, list[Path]]] = []
    for root in candidates:
        files = _pipeline_files(root)
        missing = _missing(files)
        if not missing:
            return files
        if root.exists():
            incomplete.append((root, missing))

    paper = _paper_files(app_dir / "paper_results")
    missing_paper = _missing(paper)
    if missing_paper:
        names = ", ".join(str(path) for path in missing_paper)
        raise FileNotFoundError(f"Bundled paper result set is incomplete; missing: {names}")

    if incomplete:
        details = "; ".join(
            f"{root}: {', '.join(str(path.relative_to(root)) for path in missing)}"
            for root, missing in incomplete
        )
        warnings.warn(
            f"Pipeline results are incomplete; using bundled paper results. Missing: {details}",
            RuntimeWarning,
            stacklevel=2,
        )
    return paper


RESULT_FILES = resolve_result_files()
