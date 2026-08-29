import argparse
import csv
from pathlib import Path
import yaml


class FoldedStr(str):
    pass
def folded_str_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")
yaml.add_representer(FoldedStr, folded_str_representer)


def process_features(output_file, exp_dir):
    exp_dir = Path(exp_dir)
    unique_features = set()

    for medium_dir in sorted(exp_dir.iterdir()):
        csv_path = medium_dir.joinpath("top_2_features_w_distance.csv")
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            first_row = next(reader)


        features = first_row.get("feature_combination", "").split(" ")

        for feature in features:
            unique_features.add(feature)


    features_data = {}
    for feature in unique_features:
        features_data[feature] = {
            "filter": "TODO",
            "stats": "TODO",
            "title": "TODO",
            "technical": FoldedStr("TODO\n"),
            "image": FoldedStr("TODO\n"),
            "biology": FoldedStr("TODO\n"),
        }

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(features_data, f, sort_keys=False, default_flow_style=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract unique features directly from experiment CSVs into a YAML template.")
    parser.add_argument("--output", required=True, help="Path to output YAML file")
    parser.add_argument("--exp_dir", required=True, help="Path to dirrectory with experiments")
    args = parser.parse_args()

    process_features(output_file=args.output, exp_dir=args.exp_dir)