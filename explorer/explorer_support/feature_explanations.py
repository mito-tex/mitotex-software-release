"""Round-trip loading and atomic updates for feature explanations."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Mapping

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import FoldedScalarString, ScalarString


EDITABLE_FIELDS = ("title", "image", "biology", "technical", "filter", "stats")


def _yaml() -> YAML:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 10_000
    return yaml


def load_feature_explanations(path: str | Path):
    path = Path(path)
    with path.open(encoding="utf-8") as stream:
        return _yaml().load(stream)


def update_feature_explanation(
    path: str | Path,
    feature_id: str,
    values: Mapping[str, str],
):
    """Validate and atomically persist editable values for one feature."""
    path = Path(path)
    unknown = set(values) - set(EDITABLE_FIELDS)
    if unknown:
        raise ValueError(f"Fields are not editable: {', '.join(sorted(unknown))}")

    cleaned = {field: value.strip() for field, value in values.items()}
    empty = [field for field, value in cleaned.items() if not value]
    if empty:
        raise ValueError(f"Fields cannot be empty: {', '.join(empty)}")

    data = load_feature_explanations(path)
    if feature_id not in data:
        raise KeyError(f"Unknown feature ID: {feature_id}")

    entry = data[feature_id]
    for field, value in cleaned.items():
        if field not in entry:
            raise KeyError(f"Feature {feature_id!r} has no field {field!r}")
        previous = entry[field]
        if isinstance(previous, FoldedScalarString):
            value += "\n"
        entry[field] = type(previous)(value) if isinstance(previous, ScalarString) else value

    descriptor = None
    temporary_path = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            text=True,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = None
            _yaml().dump(data, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return data[feature_id]
