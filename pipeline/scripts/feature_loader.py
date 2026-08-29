import numpy as np
import json
import pandas as pd
from data_paths import DATASET_DIR
import os

PARTITIONS_NAMES = ["train", "val", "test"]






def load_experiment_split(experiment_class_mapping: dict[str, str]) -> dict[str, list[int]]:
    """
    Load a dataset split and select only the classes specified in `experiment_class_mapping`.

    Parameters
    ----------
    experiment_class_mapping : dict[str, str]
        Dictionary mapping original dataset classes to experiment classes.
        Keys should match classes in the dataset split file.
        Values can be used to remap/merge classes (not used here since we only return IDs).

    Returns
    -------
    dict[str, list[int]]
        Dictionary with keys "train", "val", "test", containing lists of sample IDs
        that belong to the selected classes in the experiment.
    """
    with open("configs/split.json", 'r') as f:
        dataset_split = json.load(f)

    experiment_split = {"train": [], "val": [], "test": []}
    for org_class in experiment_class_mapping.keys():
        for split_name in PARTITIONS_NAMES:
            experiment_split[split_name].extend(dataset_split[org_class][split_name])
    return experiment_split









def get_experiment_int_to_class_mapping(experiment_class_mapping):
    unique_values = sorted(set(experiment_class_mapping.values()))
    int_to_value = {idx: val for idx, val in enumerate(unique_values)}

    return int_to_value, unique_values








def get_experiment_classs_to_int_mapping(experiment_class_mapping):
    unique_values = sorted(set(experiment_class_mapping.values()))
    value_to_int = {val: idx for idx, val in enumerate(unique_values)}

    return value_to_int



def load_features(features_path: str, experiment_name:str, partition_name:str = "train", features_preselction: list[str] =None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    load extracted features: mirp + freeAeon
    optional features_preselction: list of specific feature names to fetch, default None = all features
    optional list_of_id: list of specific scenes to fetch, default None = all scenes
    """
    # if partition_name not in PARTITIONS_NAMES: return None, None


    features = pd.read_csv(features_path)
    features["scan_number"] = features["id"].str.split("_").str[0]



    # load partition ids
    with open("configs/experiment_config.json", 'r') as f:
        experiment_config = json.load(f)
    experiment_class_mapping = experiment_config["experiments"][experiment_name]["class_mapping"]
    list_of_parition_scene_ids = load_experiment_split(experiment_class_mapping)[partition_name]

    # filter rows/scenes
    features = features[features['scan_number'].isin(list_of_parition_scene_ids)]
    labels = features["id"]

    # filter columns/features
    if features_preselction is not None: # keep only selected set of features
        features = features[features_preselction]
    else:
        features = features.drop(columns=["scan_number", "id"])


    features = features.replace([np.inf, -np.inf], np.nan) # get rif of non compatible values
    features = features.dropna(axis=1)  # drop columns with any NaN
    features = features.astype(float)


    # load labels mappings
    org_labels = pd.read_csv(DATASET_DIR / "metadata.csv")
    org_labels["medium_day"] = org_labels["medium"].astype(str) + "_D" + org_labels["day"].astype(str)

    id_rawEnv_map = org_labels.set_index('image')['medium_day'].to_dict()
    orgEnv_expClass_map = experiment_class_mapping
    expClass_to_int_map = get_experiment_classs_to_int_mapping(experiment_class_mapping)


    labels = labels.map(id_rawEnv_map).map(orgEnv_expClass_map).map(expClass_to_int_map)

    return features, labels
