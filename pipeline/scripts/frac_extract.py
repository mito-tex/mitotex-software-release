import argparse
import numpy as np
import pandas as pd
from tqdm.auto import tqdm

# from FreeAeonFractal.FAImageFourier import CFAImageFourier
from FreeAeonFractal.FAImage import CFAImage
from FreeAeonFractal.FAImageLacunarity import CFAImageLacunarity

# from FreeAeonFractal.FA1DMFS import CFA1DMFS
#CPU version
from FreeAeonFractal.FAImageDimension import CFAImageDimension
from FreeAeonFractal.FA2DMFS import CFA2DMFS


#GPU version
# from FreeAeonFractal.FAImageDimensionGPU import CFAImageDimensionGPU as CFAImageDimension
# from FreeAeonFractal.FA2DMFSGPU import CFA2DMFSGPU as CFA2DMFS


import sys
import os
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
from utils import normalize_masked_for_fractal, load_images
from data_paths import DATASET_DIR





def get_fractal_dimensions_features(gray_image):
    # 2d_fd
    bin_image, threshold = CFAImage.otsu_binarize(gray_image)
    fd_bc = CFAImageDimension(bin_image, with_progress = False).get_bc_fd(corp_type=-1)
    # fd_dbc = CFAImageDimension(gray_image, with_progress = False).get_dbc_fd(corp_type=-1)
    fd_sdbc = CFAImageDimension(gray_image, with_progress = False).get_sdbc_fd(corp_type=-1)

    fd_features = {
        "fd_bc": fd_bc['fd'],
        # "fd_dbc": fd_dbc['fd'],
        "fd_sdbc": fd_sdbc['fd']
    }

    return fd_features





def get_multifractal_scale_analysis_features(gray_image, q_list = np.linspace(-5, 5, 41)):
    MFS = CFA2DMFS(gray_image, q_list = q_list, bg_threshold=0.001, bg_otsu=False, with_progress=False)
    # df_mass, df_fit, df_spec = MFS.get_mfs()
    df_mass, df_fit, df_spec = MFS.get_mfs(min_points=5, use_middle_scales=True, fit_scale_frac=(0.1, 0.9))

    # MFS features:
    alpha_min = df_spec['alpha'].min()
    alpha_max = df_spec['alpha'].max()
    delta_alpha = alpha_max - alpha_min

    # Find the Peak (D0 - Capacity Dimension)
    idx_peak = df_spec['f_alpha'].idxmax()
    f_alpha_max = df_spec.loc[idx_peak, 'f_alpha']
    alpha_0 = df_spec.loc[idx_peak, 'alpha']

    # Bounded Asymmetry (-1 to 1)
    left_width = alpha_0 - alpha_min
    right_width = alpha_max - alpha_0
    total_width = left_width + right_width
    asymmetry = (left_width - right_width) / total_width if total_width != 0 else 0

    # Delta f
    idx_min_alpha = df_spec['alpha'].idxmin()
    idx_max_alpha = df_spec['alpha'].idxmax()
    delta_f = df_spec.loc[idx_min_alpha, 'f_alpha'] - df_spec.loc[idx_max_alpha, 'f_alpha']

    # 1. Information Dimension (D1) - explicitly grabs the non-NaN value
    d1 = df_fit['D1'].dropna().iloc[0] if not df_fit['D1'].dropna().empty else 0

    # 2. Correlation Dimension (D2) - safely finding q closest to 2.0
    idx_q2 = (df_fit['q'] - 2.0).abs().argmin()
    d2 = df_fit.loc[idx_q2, 'Dq']

    # 3. Fit Quality Features
    mean_r2 = (df_fit['r_value'] ** 2).mean()
    mean_std_err = df_fit['std_err'].mean()


    mfs_features = {
        'mfs_spec_width': delta_alpha,
        'mfs_spec_peak': f_alpha_max,
        'mfs_asymmetry': asymmetry,
        'mfs_alpha_at_peak': alpha_0,
        'mfs_delta_f': delta_f,
        'mfs_info_dim_d1': d1,
        'mfs_corr_dim_d2': d2,
        'mfs_mean_r2': mean_r2,
        'mfs_mean_std_err': mean_std_err
    }
    return mfs_features





def get_lacunarity_features(gray_image):
    # 2d_lacunarity
    m_scale = max(gray_image.shape) // 4
    lacunarity = CFAImageLacunarity(gray_image, max_scales=m_scale, with_progress=False)
    lac_gray = lacunarity.get_lacunarity(corp_type=-1, use_binary_mass=False, include_zero=False)
    fit_gray = lacunarity.fit_lacunarity(lac_gray)

    log_lac = np.log(lac_gray["lacunarity"])
    lac_features = {
        "lac_slope": fit_gray["slope"],
        "lac_intercept": fit_gray["intercept"],
        "lac_r_value": fit_gray["r_value"],
        "lac_r2": fit_gray["r_value"]**2,
        "lac_start": lac_gray["lacunarity"][0],
        "lac_end": lac_gray["lacunarity"][-1],
        "lac_mean": np.mean(lac_gray["lacunarity"]),
        "lac_std": np.std(lac_gray["lacunarity"]),
        "lac_log_mean": np.mean(log_lac),               # Overall "average" texture
        "lac_log_std": np.std(log_lac)
    }
    return lac_features






def extract_features_fractal(outpu_pth):
    total_files = len(os.listdir(DATASET_DIR / "images"))
    image_generator = load_images(path_size=1, img_normalization_function=normalize_masked_for_fractal)

    for batch_rois, batch_masks, batch_metadata in tqdm(image_generator, total=total_files, desc="Extracting Fractal Features"):
        roi = batch_rois[0]
        img_metadata = batch_metadata[0]

        row = {"id": img_metadata["id"]}
        row.update(get_fractal_dimensions_features(roi))
        row.update(get_multifractal_scale_analysis_features(roi))
        row.update(get_lacunarity_features(roi))

        result = pd.DataFrame([row])
        result.to_csv(outpu_pth, mode="a", header=not os.path.exists(outpu_pth), index=False)

    print(f"FINISHED, saved to: {outpu_pth}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="extract first-order and GLM features from img/mask image pairs.")
    parser.add_argument("--output", required=True, help="Path to output csv file")
    args = parser.parse_args()

    extract_features_fractal(args.output)

