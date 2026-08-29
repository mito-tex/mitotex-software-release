"""
Interface to picked experiments
"""

import pandas as pd
import yaml
import os
import logging
from .result_paths import RESULT_FILES
from .zenodo_fetcher import BASE_DIR, check_content

logger = logging.getLogger(__name__)

EXPERIMENTS_PATH = RESULT_FILES.scenarios

with EXPERIMENTS_PATH.open() as f:
    EXPERIMENTS = yaml.safe_load(f)

EXPERIMENT_IDs = list(EXPERIMENTS)
CSV_FEATURES = RESULT_FILES.features
LABELS_FILE_NAME = "metadata.csv"

def fetch_feature_names(experiment):
    return EXPERIMENTS[experiment]["features"]


def fetch_feature_table():
    check_content([LABELS_FILE_NAME])
    df_labels   = pd.read_csv(os.path.join(BASE_DIR, LABELS_FILE_NAME))
    df_features = pd.read_csv(CSV_FEATURES)
    df = pd.merge(
        df_labels,
        df_features,
        left_on="image",
        right_on="id",
        how="inner"
    )

    return df

if __name__ == "__main__":
    """Just test"""

    logging.basicConfig(level=logging.INFO)
    logger.info("Scenarios: %s", EXPERIMENTS)
    exp = "SD"
    logger.info("Scenario: %s", exp)
    logger.info("Features: %s", fetch_feature_names(exp))
