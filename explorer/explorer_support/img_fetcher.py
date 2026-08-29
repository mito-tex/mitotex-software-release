import os
import logging
import cv2
import numpy as np
import numpy.typing as npt

from .zenodo_fetcher import BASE_DIR, check_content


logger = logging.getLogger(__name__)

IMAGES_FOLDER = "images"
MASKS_FOLDER = "masks"



def min_max_normalzie_masked_img(image: np.ndarray, mask: np.ndarray) -> npt.NDArray[np.uint8]:
    """
    Normalize image so content of mask is in min-max normalzied in range 1-255
    background of image is 0
    """
    mask_bool = mask.astype(bool)
    roi_pixels = image[mask_bool]
    
    min_val = np.min(roi_pixels)
    max_val = np.max(roi_pixels).astype(np.float32)
    
    if max_val - min_val == 0:
        return np.zeros_like(image, dtype=np.float32)
        
    normalized = np.zeros_like(image, dtype=np.float32) # zros for background
    normalized[mask_bool] = (image[mask_bool].astype(np.float32) - min_val) / (max_val - min_val) * 254 + 1 # RoI in range 1-255
    
    return normalized.astype(np.uint8)




def fetch_thumbs(image_filenames):
    required_folders = [f"{IMAGES_FOLDER}.zip", f"{MASKS_FOLDER}.zip"]
    check_content(required_folders)
    
    image_dir = os.path.join(BASE_DIR, IMAGES_FOLDER)
    mask_dir = os.path.join(BASE_DIR, MASKS_FOLDER)

    thumbs = []
    # for file_name in os.listdir(image_dir):
    for file_name in image_filenames:
        file_name = f"{file_name}.png"
        img_path = os.path.join(image_dir, file_name)
        mask_path = os.path.join(mask_dir, file_name)

        if not os.path.exists(mask_path):
            logger.warning("Mask for %s not found in mask folder; skipping", file_name)
            continue
        
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        mask = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)

        thumbs.append(
                cv2.cvtColor( 
                    cv2.normalize(
                        min_max_normalzie_masked_img(img, mask), 
                        dst=None, 
                        alpha=0, 
                        beta=255, 
                        norm_type=cv2.NORM_MINMAX, 
                        dtype=cv2.CV_8U
                    ),
                    cv2.COLOR_GRAY2BGR
                )
            )
        
    return thumbs
