# Software for Interpretable Mitochondrial Texture Analysis

This archive contains two related software components used to extract, select,
inspect, visualize, and annotate mitochondrial image features.

## Components

### 1. `explorer/` — try the paper results

Mito Explorer provides an interactive feature plot and annotation interface,
plus a patch viewer for inspecting source images in selected feature spaces.
It includes the precomputed results used for the paper and can be tried
immediately without running the feature-extraction pipeline.

From the archive root, launch Feature Explorer:

```console
cd explorer
./feature_explorer.py
```

Or, from the same `explorer/` directory, launch Patch Explorer:

```console
./patch_explorer.py
```

See the <a href="explorer/README.html" target="_blank" rel="noopener">Explorer
README</a> for detailed instructions.

#### Dataset

The image, mask, and metadata dataset is not bundled with this software. It is
published separately, and the software downloads the required files from that
public record when needed.

[![Dataset DOI: 10.5281/zenodo.21261399](https://zenodo.org/badge/DOI/10.5281/zenodo.21261399.svg)](https://doi.org/10.5281/zenodo.21261399)

By default, both Explorer and the pipeline share a dataset directory beside
their component directories. Missing files are downloaded and extracted there
automatically:

```text
<archive-root>/
├── explorer/
├── pipeline/
└── yeast-mitochondria-patches/
    ├── metadata.csv
    ├── images/
    └── masks/
```

### 2. `pipeline/` — optionally recompute the features

The Mito Feature Pipeline downloads the referenced microscopy data, extracts
image features, evaluates classification scenarios, and prepares selected
feature definitions. Running it is optional for trying the Explorers.

To reproduce the computational outputs, run the complete Snakemake workflow
from the archive root:

```console
cd pipeline
conda env create -f environment.yaml
conda activate snakemake_zenodo
snakemake --cores all --use-conda
```

After a successful run, both Explorer applications automatically use the
complete result set under `pipeline/results/` instead of their bundled paper
copies. The generated `feature_explanations.yaml` is intentionally a template
whose descriptions contain `TODO` placeholders. Completing those explanations
is a manual step in Feature Explorer and requires the domain expertise
described in the paper. The pipeline alone does not reproduce the paper's
completed feature explanations.

The bundled paper-result files are curated for review and are therefore not
expected to be byte-for-byte identical to fresh pipeline outputs:

- `paper_results/features.csv` contains only the features retained for the
  paper's selected scenarios, while `pipeline/results/features/features.csv`
  contains the wider extracted feature table;
- `paper_results/feature_explanations.yaml` contains completed annotations,
  while the pipeline creates a `TODO` template. YAML key order may also differ
  and has no semantic meaning.

Compare selected feature values and explanation fields by their identifiers,
not by file size, checksum, column order, or YAML key order.

If the pipeline output is absent or incomplete, both Explorer applications keep using
the complete paper-result set and report that choice; files from the two sets
are never mixed.

You can then return to `explorer/` and launch either application again to
inspect the recomputed features and, in Feature Explorer, complete the manual
annotations.

See the <a href="pipeline/README.html" target="_blank" rel="noopener">pipeline
README</a> for detailed setup and usage instructions.

## Archive integrity and documentation

See `MANIFEST.sha256` for file checksums. Component-specific setup and usage
instructions are included in each component directory. Every bundled Markdown
README also has a sibling standalone HTML rendering for convenient viewing
without a Markdown renderer.

## Citation and license

Please cite the exact archived release. Machine-readable citation metadata is
provided in [`CITATION.cff`](CITATION.cff); its version is filled from the
release identifier when the archive is built. DOI: <https://doi.org/10.5281/zenodo.21825095>.

This software is distributed under the BSD 3-Clause License. See
[`LICENSE`](LICENSE).
