import argparse
# https://github.com/AutoViML/featurewiz/tree/main
from featurewiz import FeatureWiz

# import sys
# import os
# scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# if scripts_dir not in sys.path:
#     sys.path.insert(0, scripts_dir)
from feature_loader import load_features



def get_filtered_features(exp_name, corr_limit, features_path):
    x_train, y_train = load_features(features_path=features_path, experiment_name=exp_name, partition_name="train")

    f_wiz = FeatureWiz(
        corr_limit=corr_limit,         # defaul 0.9
        feature_engg='',         # no new features, just filter; default=''
        category_encoders='',    # Irrelevant for numerical features; default=''
        add_missing=False,       # no missing values
        skip_sulov=False,        # Keep SULOV active; default=False
        skip_xgboost=False,      # Keep XGBoost active; default=False
        transform_target=False,   # My labels are alredy integers, numeric format; default=False
        scalers='std',           # Standardize features; default=None
        verbose=0 #2
    )

    print(x_train.shape)
    print(y_train.shape)


    x_train_selected, y_train_selected = f_wiz.fit_transform(x_train, y_train)
    selected_features = f_wiz.features

    print(f"num of features before: {x_train.shape[1]}; after: {len(selected_features)}")

    return selected_features


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process dark/light image pairs.")
    parser.add_argument("--experiment_name", required=True, help="name of experiment from experiment_config.json")
    parser.add_argument("--corr_limit", type=float, required=True, help="max, featuyre correlation limit")
    parser.add_argument("--features", required=True, help="path to features csv file")
    parser.add_argument("--output", required=True, help="path to output txt file")

    args = parser.parse_args()

    filtered_features = get_filtered_features(
            exp_name = args.experiment_name, 
            corr_limit = args.corr_limit, 
            features_path = args.features
        )

    with open(args.output, "w") as f:
        f.write(" ".join(filtered_features))