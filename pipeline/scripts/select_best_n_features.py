import argparse
from itertools import combinations
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import json

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import classification_report


from feature_loader import load_features


def select_features(features_path:str, experiment_name: str, num_of_features_to_select: int, weights: str, pre_selected_features_pth: str):
    print()
    with open("configs/project_config.json", 'r') as f:
        project_config = json.load(f)
    num_threads = project_config["select_best_n_num_threads"]

    with open(pre_selected_features_pth, 'r') as file:
        line = file.readline().strip()
    preslected_f = line.split(" ")

    train_x, train_y = load_features(features_path, experiment_name, partition_name="train", features_preselction=preslected_f)
    val_x, val_y = load_features(features_path, experiment_name, partition_name="val", features_preselction=preslected_f)
    train_y, val_y = train_y.to_numpy(), val_y.to_numpy()

    if num_of_features_to_select == 0: # select all
        num_of_features_to_select = len(preslected_f)
    

    data_collection = []

    column_combinations = list(combinations(preslected_f, num_of_features_to_select))
    column_combinations_pbar = tqdm(column_combinations, desc=f"iterating feature combination: {num_of_features_to_select} out of {len(preslected_f)}", unit="comb")
    for feature_combination in column_combinations_pbar:
        feature_combination = list(feature_combination)

        feature_subse_train_x = train_x[feature_combination].to_numpy()
        feature_subse_val_x = val_x[feature_combination].to_numpy()

        X = np.concatenate([feature_subse_train_x, feature_subse_val_x])
        y = np.concatenate([train_y, val_y])

        rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=42)

        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            # ('knn', KNeighborsClassifier(n_neighbors=5, weights='uniform'))
            ('knn', KNeighborsClassifier(n_neighbors=5, weights=weights))
        ])
        
        scores = cross_val_score(
            pipeline,
            X,
            y,
            cv=rskf,
            scoring='f1_macro',
            n_jobs=num_threads
        )

        mean_f1 = scores.mean()
        std_f1 = scores.std()

        data_collection.append({
            "feature_combination": " ".join(feature_combination),
            "mean_f1_macro": mean_f1,
            "std_f1_macro": std_f1
        })

    return data_collection


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process dark/light image pairs.")
    parser.add_argument("--experiment_name", required=True, help="name of experiment from experiment_config.json")
    parser.add_argument("--select_n_features", type=int, required=True, help="num, how many features to select")
    parser.add_argument("--weights", type=str, required=True, help="how knn should wight distances 'uniform' or 'distance'")
    parser.add_argument("--features", required=True, help="path to features csv file")
    parser.add_argument("--pre_selected_features_path", type=str, required=True, help="path to txt file, with pre selected features")
    parser.add_argument("--output", type=str, required=True, help="path to csv file, for output")

    args = parser.parse_args()

    data_collection = select_features(
            features_path = args.features,
            experiment_name = args.experiment_name, 
            num_of_features_to_select = args.select_n_features, 
            weights = args.weights, 
            pre_selected_features_pth = args.pre_selected_features_path
        )

    df = pd.DataFrame(data_collection)
    TOP_N = 50
    df_sorted = df.sort_values(by=['mean_f1_macro', 'std_f1_macro'], ascending=[False, True])
    top = df_sorted.head(TOP_N)
    top.to_csv(args.output, index=False)
