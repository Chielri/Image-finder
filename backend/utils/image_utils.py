import logging

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def load_image_rgb(path: str) -> np.ndarray:
    pil_img = Image.open(path).convert("RGB")
    return np.array(pil_img)


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def rgb_to_bgr(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
