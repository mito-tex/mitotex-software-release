import csv
import json
from pathlib import Path
import yaml
import argparse


def process_experiments(output_file, exp_dir):
    exp_dir = Path(exp_dir)


    descriptions = {}
    with open("configs/experiment_config.json", "r", encoding="utf-8") as f:
        config_data = json.load(f)
    for medium_key, val in config_data["experiments"].items():
        descriptions[medium_key] = val["description"]


    yaml_data = {}

    for medium_dir in sorted(exp_dir.iterdir()):
        medium_name = medium_dir.name
        csv_path = medium_dir.joinpath("top_2_features_w_distance.csv")

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            first_row = next(reader)


        features= first_row.get("feature_combination", "").split(" ")

        mean_f1 = float(first_row.get("mean_f1_macro", 0.0))
        std_f1 = float(first_row.get("std_f1_macro", 0.0))

        desc = descriptions[medium_name]

        yaml_data[medium_name] = {
            "description": desc,
            "features": features,
            "mean_f1_macro": mean_f1,
            "std_f1_macro": std_f1,
        }

    # 4. Save result to YAML
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, sort_keys=False, default_flow_style=False)

    print(
        f"Successfully processed {len(yaml_data)} items into '{output_file}'."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="copose yaml file with expeeriments results")
    parser.add_argument("--output", required=True, help="Path to output YAML file")
    parser.add_argument("--exp_dir", required=True, help="Path to dirrectory with experiments")
    args = parser.parse_args()

    process_experiments(output_file=args.output, exp_dir=args.exp_dir)