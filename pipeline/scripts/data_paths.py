"""Shared dataset location used by the MitoTex pipeline."""

import os
from pathlib import Path


DATASET_DIR = Path(
    os.environ.get(
        "YEAST_MITOCHONDRIA_PATCHES_DIR",
        Path(__file__).resolve().parents[2] / "yeast-mitochondria-patches",
    )
).expanduser().resolve()
