import numpy as np
import numpy.typing as npt
import math
import cv2
import os

from data_paths import DATASET_DIR





def zScore_masked_img(image: np.ndarray, mask: np.ndarray) -> npt.NDArray[np.float32]:
    """
    Normalize images content of mask to standard normal distribution.
    background is 0
    """
    mask_bool = mask.astype(bool)
    roi_pixels = image[mask_bool]

    mean = np.mean(roi_pixels)
    std = np.std(roi_pixels)
    if std == 0:
        return np.zeros_like(image, dtype=np.float32)
    normalized = (image.astype(np.float32) - mean) / std
    normalized[~mask_bool] = 0.0 # mask background

    return normalized





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




def crop_padd_to_pow2_shape(img: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    crop/padd(with 0) img and its mask into shape, where width and hight are size of its closest power of 2
    """
    def get_optimized_dim(current_dim: int, min_dim: int=256):
        """
        Find the nearest power of 2
        log2 returns float, round it, then 2**that_power
        """
        p2 = 2 ** round(math.log2(current_dim))
        return max(p2, min_dim)
    
    h, w = img.shape
    target_h = get_optimized_dim(h)
    target_w = get_optimized_dim(w)
    
    # Handle Height
    if h > target_h:    
        diff = h - target_h
        top = diff // 2
        img = img[top : top + target_h, :]
        mask = mask[top : top + target_h, :]
    elif h < target_h:
        diff = target_h - h
        top = diff // 2
        bottom = diff - top
        img = cv2.copyMakeBorder(img, top, bottom, 0, 0, cv2.BORDER_CONSTANT, value=0)
        mask = cv2.copyMakeBorder(mask, top, bottom, 0, 0, cv2.BORDER_CONSTANT, value=0)

    # Handle Width
    h, w = img.shape # just to be sure (but should be redundant step, width should not be affected)
    if w > target_w:    
        diff = w - target_w
        left = diff // 2
        img = img[:, left : left + target_w]
        mask = mask[:, left : left + target_w]
    elif w < target_w:
        diff = target_w - w
        left = diff // 2
        right = diff - left
        img = cv2.copyMakeBorder(img, 0, 0, left, right, cv2.BORDER_CONSTANT, value=0)
        mask = cv2.copyMakeBorder(mask, 0, 0, left, right, cv2.BORDER_CONSTANT, value=0)

    return img, mask










def normalize_masked_for_fractal(img: np.ndarray, mask: np.ndarray) -> npt.NDArray[np.uint8]:
    """
    applay gaussian blure and min_max_normalzie_masked_img
    """
    img = cv2.GaussianBlur(img, (3, 3), sigmaX=0.8)
    cropped, croppped_mask = crop_padd_to_pow2_shape(img, mask)
    norm = min_max_normalzie_masked_img(cropped, croppped_mask)
    return norm






def load_images(path_size=0, img_normalization_function: callable = None):
    folder_path = DATASET_DIR
    batch_rois = []
    batch_masks = []
    batch_ids = []

    for filename in os.listdir(folder_path / "images"):
        img = cv2.imread(str(folder_path / "images" / filename), cv2.IMREAD_UNCHANGED)
        mask = cv2.imread(str(folder_path / "masks" / filename), cv2.IMREAD_GRAYSCALE)

        if img_normalization_function is None:
            norm_roi = img
        else:
            norm_roi = img_normalization_function(img, mask)

        batch_rois.append(norm_roi)
        batch_masks.append(mask)
        # scan_number, mask_number = filename.split("_")
        # batch_metadata.append({"scene_id": scan_number, "mask_number": mask_number,})
        batch_ids.append({"id": filename.split(".")[0]})

        # Yield every path_size images
        if path_size > 0 and len(batch_rois) >= path_size:
            yield batch_rois, batch_masks, batch_ids
            batch_rois = []
            batch_masks = []
            batch_ids = []

    # Yield remaining images, or everything when path_size == 0
    if len(batch_rois) != 0:
        yield batch_rois, batch_masks, batch_ids



