import argparse
import math
from tqdm import tqdm
import json
import pandas as pd

from mirp import extract_features
from mirp.settings.generic import SettingsClass
from mirp.settings.transformation_parameters import ImageTransformationSettingsClass
from mirp.settings.feature_parameters import FeatureExtractionSettingsClass
# from mirp.settings.resegmentation_parameters import ResegmentationSettingsClass
# from mirp.settings.perturbation_parameters import ImagePerturbationSettingsClass
# from mirp.settings.image_processing_parameters import ImagePostProcessingClass
# from mirp.settings.interpolation_parameters import ImageInterpolationSettingsClass, MaskInterpolationSettingsClass
from mirp.settings.general_parameters import GeneralSettingsClass


import sys
import os
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
from utils import zScore_masked_img, load_images
from data_paths import DATASET_DIR



def get_mirp_feature_extraction_settings_ibsi_compliant() -> SettingsClass:
    discretisation_method="fixed_bin_number"
    discretisation_n_bins=32

    general_settings = GeneralSettingsClass(
        by_slice =True,
        ibsi_compliant =True # LBP are not in IBSI
    )
    # Feature extraction parameters
    feature_computation_parameters = FeatureExtractionSettingsClass(
        by_slice =general_settings.by_slice,
        ibsi_compliant=general_settings.ibsi_compliant,
        no_approximation=True,
        base_feature_families="all",  # compute all radiomics families
        base_discretisation_method =discretisation_method,
        base_discretisation_n_bins =discretisation_n_bins,
        stat_percentile = [10.0, 90.0],
        stat_value_shift = 0.0,
        ivh_discretisation_method = discretisation_method,
        ivh_discretisation_n_bins = 128,
        glcm_distance =[1.0, 2.0, 4.0, 8.0, 16.0, 32.0], # pixel distance
        glcm_spatial_method =["2d_average"],
        glrlm_spatial_method =["2d_average"],
        glszm_spatial_method =["2d"],
        gldzm_spatial_method =["2d"],
        ngtdm_spatial_method =["2d"],
        ngldm_distance =[1.0, 2.0, 4.0, 8.0], # pixel distance
        ngldm_spatial_method =["2d"],
        ngldm_difference_level=[0.0, 1.0]
    )
    image_transformation_settings = ImageTransformationSettingsClass(
        by_slice =general_settings.by_slice,
        ibsi_compliant =general_settings.ibsi_compliant,

        response_map_feature_families="all",
        response_map_discretisation_method =discretisation_method,
        response_map_discretisation_n_bins =discretisation_n_bins,

        # Filters
        filter_kernels=["log", "laws", "gabor", "separable_wavelet"],
        boundary_condition = "mirror", # scipy.ndimage.convolve

        laplacian_of_gaussian_sigma=[1.0, 2.0, 4.0, 8.0],
        laplacian_of_gaussian_pooling_method = "none",
        laplacian_of_gaussian_kernel_truncate = 4.0,

        laws_kernel=["l5e5", "l5s5", "e5e5"],
        laws_compute_energy=True,
        laws_delta=7,
        laws_rotation_invariance=True,
        laws_pooling_method="max",

        gabor_sigma=[2.0, 4.0, 8.0],
        gabor_lambda=[4.0, 8.0, 16.0],
        gabor_theta=0.0,
        gabor_theta_step=45.0,
        gabor_pooling_method="max",
        gabor_response="modulus",

        separable_wavelet_families="coif1",
        separable_wavelet_set=["lh", "hh"],
        separable_wavelet_decomposition_level = [1, 2, 3],
        separable_wavelet_pooling_method = "max",
        separable_wavelet_rotation_invariance=True,

    )
    settings = SettingsClass(
        general_settings=general_settings,
        post_process_settings=None, # post_processor, #ImagePostProcessingClass(),
        img_interpolate_settings=None, # image_interpolation_settings,
        roi_interpolate_settings=None,
        roi_resegment_settings=None,  # no resegmentation
        perturbation_settings=None,   # no perturbation
        img_transform_settings=image_transformation_settings,
        feature_extr_settings=feature_computation_parameters
    )
    return settings


def get_mirp_feature_extraction_settings_NOT_ibsi_compliant() -> SettingsClass:
    discretisation_method="fixed_bin_number"
    discretisation_n_bins=32

    general_settings = GeneralSettingsClass(
        by_slice =True,
        ibsi_compliant =False # LBP are not in IBSI
    )
    # Feature extraction parameters
    feature_computation_parameters = FeatureExtractionSettingsClass(
        by_slice =general_settings.by_slice,
        ibsi_compliant=general_settings.ibsi_compliant,
        no_approximation=True,
        base_feature_families="none",  # compute all radiomics families
        base_discretisation_method =discretisation_method,
        base_discretisation_n_bins =discretisation_n_bins,
        stat_percentile = [10.0, 90.0],
        stat_value_shift = 0.0,
        ivh_discretisation_method = discretisation_method,
        ivh_discretisation_n_bins = 128,
        glcm_distance =[1.0, 2.0, 4.0, 8.0, 16.0, 32.0], # pixel distance
        glcm_spatial_method =["2d_average"],
        glrlm_spatial_method =["2d_average"],
        glszm_spatial_method =["2d"],
        gldzm_spatial_method =["2d"],
        ngtdm_spatial_method =["2d"],
        ngldm_distance =[1.0, 2.0, 4.0, 8.0], # pixel distance
        ngldm_spatial_method =["2d"],
        ngldm_difference_level=[0.0, 1.0]
    )
    image_transformation_settings = ImageTransformationSettingsClass(
        by_slice =general_settings.by_slice,
        ibsi_compliant =general_settings.ibsi_compliant,

        response_map_feature_families="all",
        response_map_discretisation_method =discretisation_method,
        response_map_discretisation_n_bins =discretisation_n_bins,

        filter_kernels=["lbp"],
        boundary_condition = "mirror", # scipy.ndimage.convolve
        lbp_method=["rotation_invariant"],
        lbp_filter_distance=[2, 6],
    )
    settings = SettingsClass(
        general_settings=general_settings,
        post_process_settings=None, # post_processor, #ImagePostProcessingClass(),
        img_interpolate_settings=None, # image_interpolation_settings,
        roi_interpolate_settings=None,
        roi_resegment_settings=None,  # no resegmentation
        perturbation_settings=None,   # no perturbation
        img_transform_settings=image_transformation_settings,
        feature_extr_settings=feature_computation_parameters
    )
    return settings



def extract_texture_features(outpu_pth):
    with open("configs/project_config.json", 'r') as f:
        project_config = json.load(f)
    num_threads = project_config["mirp_num_threads"]
    batch_size = project_config["mirp_feature_extraction_batch_size"]


    ibsi_settings = get_mirp_feature_extraction_settings_ibsi_compliant()
    lbp_settings = get_mirp_feature_extraction_settings_NOT_ibsi_compliant()


    total_files = len(os.listdir(DATASET_DIR / "images"))
    total_batches = math.ceil(total_files / batch_size) if batch_size > 0 else 1

    # Initialize the generator
    batch_generator = load_images(path_size=batch_size, img_normalization_function=zScore_masked_img)

    # Iterate cleanly over the generator using a for loop wrapped in tqdm
    for batch_rois, batch_masks, batch_metadata in tqdm(batch_generator, total=total_batches, desc="Extracting Features"):

        ibsi_results = extract_features(
            image=batch_rois,
            mask=batch_masks,
            settings=ibsi_settings,
            num_cpus=num_threads,
            parallel_backend="joblib"
        )

        lbp_results = extract_features(
            image=batch_rois,
            mask=batch_masks,
            settings=lbp_settings,
            num_cpus=num_threads,
            parallel_backend="joblib"
        )

        df_ibsi = pd.concat(ibsi_results, ignore_index=True)
        df_ibsi = df_ibsi.loc[:, ~df_ibsi.columns.str.startswith(("image_", "sample_name"))]

        df_lbp = pd.concat(lbp_results, ignore_index=True)
        df_lbp = df_lbp.loc[:, ~df_lbp.columns.str.startswith(("image_", "sample_name"))]

        df_meta = pd.DataFrame(batch_metadata)

        cols_to_use = df_lbp.columns.difference(df_ibsi.columns)

        result = pd.concat([df_meta, df_ibsi, df_lbp[cols_to_use]], axis=1)
        result.to_csv(outpu_pth, mode="a", header=not os.path.exists(outpu_pth), index=False)

    print(f"FINISHED, saved to: {outpu_pth}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="extract first-order and GLM features from img/mask image pairs.")
    parser.add_argument("--output", required=True, help="Path to output csv file")
    args = parser.parse_args()

    extract_texture_features(args.output)
