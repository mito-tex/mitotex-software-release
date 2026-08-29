#!/usr/bin/env -S uv run --locked --script

"""
Patch Explorer

Run:
    > ./patch_explorer.py
    > ./patch_explorer.py --scenario YPGal
    > ./patch_explorer.py --list-scenarios
    or
    > uv run --locked patch_explorer.py
    or if you have the dependencies installed python 
    > python patch_explorer.py

Description:
    Interactive embedding visualization tool that renders image thumbnails at embedding locations.

    The viewer supports:
    - Pan  (left mouse drag)
    - Zoom (right mouse drag or wheel alternative)
"""

# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = [
#   "numpy",
#   "pandas",
#   "opencv-python",
#   "PyYAML",
#   "requests",
#   "tqdm"
# ]
# ///

import argparse
import numpy as np
import pandas as pd
import cv2
import logging

from explorer_support.colors import LABEL_TO_COLOR
from explorer_support.feature_fetcher import (
    EXPERIMENTS,
    RESULT_FILES,
    fetch_feature_names,
    fetch_feature_table,
)
from explorer_support.img_fetcher import fetch_thumbs

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Explore image patches in a scenario's two-feature space.",
    )
    parser.add_argument(
        "--scenario",
        choices=EXPERIMENTS,
        default="Day_3",
        metavar="ID",
        help="scenario ID to display (default: Day_3)",
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="list scenario IDs and descriptions, then exit",
    )
    return parser.parse_args()


args = parse_args()
if args.list_scenarios:
    width = max(map(len, EXPERIMENTS))
    for scenario_id, details in EXPERIMENTS.items():
        print(f"{scenario_id:<{width}}  {details['description']}")
    raise SystemExit(0)

features = fetch_feature_names(args.scenario)
scenario_description = EXPERIMENTS[args.scenario]["description"]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger.info("Results source: %s", RESULT_FILES.description)

# ----------------------------
# CONFIG / CONSTANTS
# ----------------------------

FALLBACK_VIEW_SIZE = (1920, 1080)
BG_COLOR = 0
TINT_FACTOR = 0.75 # how strong the color - coding will be


THUMB_SIZE = 224-64 # crop slightly to mitigate patch clutter
COLOR_MODE = False
CANVAS_LONG_EDGE = 30_000

# ZOOM_INIT = 1.0
ZOOM_MIN = 0.05
ZOOM_MAX = 50.0
ZOOM_SENSITIVITY = 200.0

EPS = 1e-9

df = fetch_feature_table()

# ----------------------------
# Load images (FAST)
# ----------------------------

logger.info("Loading images")


# Load images and keep the dataframe positionally aligned with them.
# images = [cv2.imread(f"{DIR_THUMBS}/{image_id}.png") for image_id in df["id"]]
images = fetch_thumbs(df["image"])
available = np.fromiter((image is not None for image in images), dtype=bool)

df = df.loc[available].reset_index(drop=True)
imgs_gray = [image for image in images if image is not None]

imgs_color = [img.copy() for img in imgs_gray]

N = len(imgs_gray)
logger.info("Loaded %d images", N)

visible     = np.ones(N, dtype=bool)
visible_day = np.ones(N, dtype=bool)
visible_env = np.ones(N, dtype=bool)
visible_experiment = np.ones(N, dtype=bool)

# turn gray patches to green
for img in imgs_gray:
    img[...,0] = 0
    img[...,2] = 0

# Color the border
# for label, img in zip (df['label'], imgs_color):
#     img[:10, :,::-1] = LABEL_TO_COLOR[label]
#     img[-10:,:,::-1] = LABEL_TO_COLOR[label]
#     img[:,-10:,::-1] = LABEL_TO_COLOR[label]
#     img[: ,:10,::-1] = LABEL_TO_COLOR[label]

# Tint the tiles
for medium, day, img in zip(df['medium'], df['day'], imgs_color):
    # Get the RGB color and match the BGR layout using [::-1]
    label = f"{medium}_D{day}"
    color_bgr = np.array(LABEL_TO_COLOR[label][::-1], dtype=img.dtype)
    
    # Apply the tint across the entire image dimensions
    img[:, :] = cv2.addWeighted(img, 1 - TINT_FACTOR, np.full_like(img, color_bgr), TINT_FACTOR, 0)    

imgs = imgs_color if COLOR_MODE else imgs_gray



# ----------------------------
# Normalize embedding (for display only)
# ----------------------------

embedding = df[features].to_numpy().astype(np.float32)


emb = embedding.copy()
# emb = (emb - emb.min(0)) / (emb.ptp(0) + 1e-9)


emb = emb - emb.min(axis=0)
emb = emb / (emb.max(axis=0) - emb.min(axis=0) + EPS)

# ----------------------------
# Window viewport
# ----------------------------
WIN = f"Mito Explorer: Scenario: {scenario_description} ({args.scenario})"

def open_window():
    """Create the window and return its actual drawable size."""
    fallback_w, fallback_h = FALLBACK_VIEW_SIZE

    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    # A window has no reliable image rectangle on every backend until imshow()
    # has created its drawing surface.
    cv2.imshow(WIN, np.zeros((fallback_h, fallback_w, 3), dtype=np.uint8))

    # Pump a few GUI events so the window manager can finish creating the window.
    for _ in range(3):
        cv2.waitKey(1)

    try:
        _, _, view_w, view_h = cv2.getWindowImageRect(WIN)
    except (AttributeError, cv2.error):
        return FALLBACK_VIEW_SIZE

    if view_w <= 1 or view_h <= 1:
        return FALLBACK_VIEW_SIZE
    return view_w, view_h


VIEW_W, VIEW_H = open_window()

if VIEW_W >= VIEW_H:
    CANVAS_W = CANVAS_LONG_EDGE
    CANVAS_H = round(CANVAS_LONG_EDGE * VIEW_H / VIEW_W)
else:
    CANVAS_H = CANVAS_LONG_EDGE
    CANVAS_W = round(CANVAS_LONG_EDGE * VIEW_W / VIEW_H)

logger.info("Window viewport: %d x %d", VIEW_W, VIEW_H)
logger.info("World canvas: %d x %d", CANVAS_W, CANVAS_H)

# Center the canvas in the initial viewport.
cx0 = CANVAS_W / 2
cy0 = CANVAS_H / 2

# ----------------------------
# Canvas setup
# ----------------------------

def build_canvas():
    if COLOR_MODE:
        return np.full((CANVAS_H, CANVAS_W, 3), BG_COLOR, dtype=np.uint8), \
               np.zeros((CANVAS_H, CANVAS_W, 3), dtype=bool)
    else:
        return np.full((CANVAS_H, CANVAS_W, 3), BG_COLOR, dtype=np.uint8), \
               np.zeros((CANVAS_H, CANVAS_W), dtype=bool)

canvas, occupied = build_canvas()

def render_thumbnails():
    global canvas, occupied

    canvas, occupied = build_canvas()

    for i in np.flatnonzero(visible):
        img = imgs[i]
        if img is None:
            continue

        interp = cv2.INTER_AREA if COLOR_MODE else cv2.INTER_NEAREST
        img_resized = cv2.resize(img, (THUMB_SIZE, THUMB_SIZE), interpolation=interp)

        x, y = xs[i], ys[i]
        x0, y0 = x, y
        x1, y1 = x + THUMB_SIZE, y + THUMB_SIZE

        canvas[y0:y1, x0:x1] = img_resized
        occupied[y0:y1, x0:x1] = True

# ----------------------------
# Map embeddings → pixels
# ----------------------------
xs = (     emb[:, 0]  * (CANVAS_W - THUMB_SIZE)).astype(int)
ys = ((1 - emb[:, 1]) * (CANVAS_H - THUMB_SIZE)).astype(int)

logger.info("Rendering thumbnails...")
render_thumbnails()
logger.info("Rendering done")


state = {
    "zoom": min(VIEW_W / CANVAS_W, VIEW_H / CANVAS_H),
    "cx": cx0,
    "cy": cy0,
    "drag": False,
    "last": None,
    "mode": None,
}


def apply_day_filters(day : int):
    global visible_day, visible_env, visible_experiment

    # masks = visible.copy()
    visible_day [df["day"] == day] = ~visible_day [df["day"] == day]
    set_filter(visible_day, visible_env, visible_experiment)

def apply_env_filters(env : str):
    global visible_day, visible_env, visible_experiment

    visible_env [df["medium"] == env] = ~visible_env [df["medium"] == env]
    set_filter(visible_day, visible_env, visible_experiment)

def apply_experiment_filter(experiment: int):
    global visible_day, visible_env, visible_experiment

    selected = df["experiment"] == experiment
    visible_experiment[selected] = ~visible_experiment[selected]
    set_filter(visible_day, visible_env, visible_experiment)


def set_filter(mask_day, mask_env, mask_experiment):
    global visible
    visible = np.asarray(mask_day & mask_env & mask_experiment, dtype=bool)
    render_thumbnails()
    render()


def update_window_title():
    active_days = [
        str(day)
        for day in sorted(df["day"].unique())
        if visible_day[df["day"] == day].any()
    ]
    active_experiments = [
        str(experiment)
        for experiment in sorted(df["experiment"].unique())
        if visible_experiment[df["experiment"] == experiment].any()
    ]
    day_text = ", ".join(active_days) if active_days else "none"
    experiment_text = ", ".join(active_experiments) if active_experiments else "none"
    title = (
        # f"Mito Explorer "
        f"{args.scenario} ({scenario_description}) - "
        f"Days: {day_text} - Experiments: {experiment_text}"
    )
    try:
        cv2.setWindowTitle(WIN, title)
    except (AttributeError, cv2.error):
        pass

def render():
    update_window_title()
    z = state["zoom"]

    # affine camera model (no cropping)
    M = np.array([
        [z, 0, (-state["cx"] * z + VIEW_W / 2)],
        [0, z, (-state["cy"] * z + VIEW_H / 2)]
    ], dtype=np.float32)

    view = cv2.warpAffine(
        canvas,
        M,
        (VIEW_W, VIEW_H),
        flags=cv2.INTER_NEAREST,
        borderValue=BG_COLOR
    )

    cv2.imshow(WIN, view)


def mouse(event, x, y, flags, param):
    # safety: recover from lost mouse-up events (macOS OpenCV issue)
    if event == cv2.EVENT_MOUSEMOVE and flags == 0 and state.get("drag", False):
        state["drag"] = False
        state["mode"] = None
        return

    match event:
        case cv2.EVENT_LBUTTONDOWN:
            state["drag"] = True
            state["last"] = (x, y)
            state["mode"] = "pan"
        case cv2.EVENT_LBUTTONUP:
            state["drag"] = False
            state["mode"] = None
        case cv2.EVENT_RBUTTONDOWN:
            state["drag"] = True
            state["last"] = (x, y)
            state["mode"] = "zoom"
        case cv2.EVENT_RBUTTONUP:
            state["drag"] = False
            state["mode"] = None

        case cv2.EVENT_MOUSEMOVE:
            if not state["drag"]: return

            dx = x - state["last"][0]
            dy = y - state["last"][1]

            match state["mode"]:
                case "pan":
                    # convert screen movement to world movement
                    state["cx"] -= dx / state["zoom"]
                    state["cy"] -= dy / state["zoom"]
                case "zoom":
                    # zoom anchored around drag (simple exponential feel)
                    state["zoom"] *= (1.0 + (-dy / ZOOM_SENSITIVITY))
                    state["zoom"] = np.clip(state["zoom"], ZOOM_MIN, ZOOM_MAX)

            state["last"] = (x, y)
            render()
        
cv2.setMouseCallback(WIN, mouse)

KEY_ESC = 27
KEY_Q = ord('q')
KEY_C = ord('c')

KEY_0 = ord('0')
KEY_1 = ord('1')
KEY_2 = ord('2')
KEY_3 = ord('3')
KEY_LEFT_BRACKET = ord('[')
KEY_RIGHT_BRACKET = ord(']')

KEY_d = ord('d')
KEY_l = ord('l')
KEY_y = ord('y')
KEY_a = ord('a')
KEY_s = ord('s')


render()

try:
    while True:
        try:
            if cv2.getWindowProperty(WIN, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break

        key = cv2.waitKeyEx(20)
        if key != -1:
            key &= 0xFF

        if key in (KEY_Q, KEY_ESC):
            break
        if key == KEY_C:
            COLOR_MODE = not COLOR_MODE

            # reload image set
            imgs = imgs_color if COLOR_MODE else imgs_gray

            # rebuild canvas
            canvas, occupied = build_canvas()

            # redraw thumbnails
            render_thumbnails()

            logger.info("Color changed")
            render()

        if key == KEY_0:
            visible_day[:] = True
            visible_env[:] = True
            visible_experiment[:] = True
            set_filter(visible_day, visible_env, visible_experiment)

        if key == KEY_1:
            apply_day_filters(1)
        if key == KEY_2:
            apply_day_filters(2)
        if key == KEY_3:
            apply_day_filters(3)

        if key == KEY_LEFT_BRACKET:
            apply_experiment_filter(1)
        if key == KEY_RIGHT_BRACKET:
            apply_experiment_filter(2)

        if key == KEY_d:
            apply_env_filters('YPD')
        if key == KEY_l:
            apply_env_filters('YPGal')
        if key == KEY_y:
            apply_env_filters('YPGly')
        if key == KEY_a:
            apply_env_filters('AS')
        if key == KEY_s:
            apply_env_filters('SD')
except KeyboardInterrupt:
    logger.info("Closing patch explorer")
finally:
    cv2.destroyAllWindows()
