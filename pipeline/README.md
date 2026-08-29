# Mito Feature Extraction and Selection Pipeline

The pipeline and Mito Explorer share a single dataset directory named
`yeast-mitochondria-patches` beside their repository directories. Set
`YEAST_MITOCHONDRIA_PATCHES_DIR` to the same absolute path for both applications
to override that location. Missing files are retrieved from the public Zenodo
record.

## Setup and run
The pipeline requires Snakemake, the Snakemake Zenodo storage plugin, and Conda
or Mamba to create the rule-specific environments used by `--use-conda`.

### Recommended: Conda

Create the Snakemake controller environment from `environment.yaml`:

```bash
conda env create -f environment.yaml
conda activate snakemake_zenodo
```

### Alternative Snakemake installation

Snakemake and its Zenodo plugin can instead be installed in a Python virtual
environment, but Conda or Mamba must still be installed and available for the
rule-specific environments:

```bash
pip install "snakemake>=8.0.0" snakemake-storage-plugin-zenodo
```

## Verify the installation
Check that Snakemake is available:
```bash
snakemake --version
```

## Run the pipeline
Run the pipeline from the repository root:
```bash
snakemake --cores all --use-conda
```

## Output
The pipeline downloads microscopy patches of mitochondria and extracts a set of
texture features from each image. The extracted features are aggregated into a
single CSV file.

Feature extraction takes a moderate amount of time.

For each scenario defined in `configs/experiment_config.json`, the pipeline
identifies the most descriptive features and selects the top two features based
on their ability to separate the data.

The desired number of selected features can be changed in the configuration.
Increasing this number can substantially increase computational requirements.

Generated output files:

- `results/features/features.csv` — all extracted features for all images;
- `results/scenarios_features.yaml` — the top two features for each scenario;
- `results/feature_explanations.yaml` — a template containing TODO descriptions
  for the selected features.

The pipeline reproduces the computational outputs, but it does not generate the
finished explanatory text used for the paper. Completing the TODO fields in
`feature_explanations.yaml` is a manual annotation step performed in
Feature Explorer.

The feature CSV bundled as a paper result is a filtered version of the wider
pipeline output: it retains only features selected for the paper's scenarios.
The bundled paper explanation YAML contains completed annotations and may order
its keys differently from the generated template. YAML key order has no
semantic meaning; compare entries by feature identifier.

When this repository is used from the combined software bundle, both Explorer
applications automatically use these files once the complete set exists. Until
then, they use the bundled paper results.
