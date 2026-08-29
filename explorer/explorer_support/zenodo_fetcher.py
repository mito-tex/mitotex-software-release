import os
import logging
from pathlib import Path
import requests
import zipfile
from tqdm import tqdm

logger = logging.getLogger(__name__)

RECORD_ID = "21261399"
API_URL = f"https://zenodo.org/api/records/{RECORD_ID}"
# Both SW repositories use the same data directory by default. Override it
# when needed, for example:
# YEAST_MITOCHONDRIA_PATCHES_DIR=/data/yeast-mitochondria-patches.
BASE_DIR = str(
    Path(
        os.environ.get(
            "YEAST_MITOCHONDRIA_PATCHES_DIR",
            Path(__file__).resolve().parents[2] / "yeast-mitochondria-patches",
        )
    ).expanduser().resolve()
)


def check_content(content):
    for c in content:
        expected_local_name = c.replace('.zip', '')
        expected_path = os.path.join(BASE_DIR, expected_local_name)
        if not os.path.isdir(expected_path) and not os.path.exists(expected_path):
            logger.info("Missing local dataset content: %s", expected_path)
            download_content(c)
        else:
            logger.info("Dataset content already available: %s", expected_path)


def download_content(target_filename):
    os.makedirs(BASE_DIR, exist_ok=True)
    logger.info("Checking Zenodo for %s", target_filename)
    
    # 1. Fetch metadata to get the dynamic file IDs (this takes a fraction of a second)
    response = requests.get(API_URL)
    response.raise_for_status()
    
    files = response.json().get('files', [])

    # 2. Find only the file we want
    file_info = next((f for f in files if (f.get('filename') or f.get('key')) == target_filename), None)
    
    if not file_info:
        logger.error("%s was not found in Zenodo record %s", target_filename, RECORD_ID)
        return
    
    download_url = file_info['links'].get('download') or file_info['links'].get('self')
    file_path = os.path.join(BASE_DIR, target_filename)
    
    # 4. Download just that specific file
    logger.info("Downloading %s", target_filename)
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        
        with open(file_path, 'wb') as f, tqdm(
            desc=target_filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
                    
    # 5. Unzip and cleanup if necessary
    if target_filename.endswith('.zip'):
        logger.info("Extracting %s", target_filename)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(BASE_DIR)
        os.remove(file_path)
        
    logger.info("Successfully downloaded and processed %s", target_filename)
