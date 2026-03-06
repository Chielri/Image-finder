import logging

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert an RGB numpy array to grayscale."""
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def normalize_alpha(image: np.ndarray) -> np.ndarray:
    """Convert RGBA image to RGB with white background."""
    if len(image.shape) == 3 and image.shape[2] == 4:
        pil_img = Image.fromarray(image, "RGBA")
        background = Image.new("RGB", pil_img.size, (255, 255, 255))
        background.paste(pil_img, mask=pil_img.split()[3])
        return np.array(background)
    return image


def preprocess_for_matching(image: np.ndarray) -> np.ndarray:
    """Convert an image to grayscale, handling alpha channels."""
    image = normalize_alpha(image)
    return to_grayscale(image)
