"""Generate test fixtures: a document image with known patterns and query images."""
import os

import numpy as np
from PIL import Image, ImageDraw

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "tests", "fixtures")


def create_logo(size=(40, 40)) -> np.ndarray:
    img = np.ones((*size, 3), dtype=np.uint8) * 255
    img[5:35, 5:35] = [200, 50, 50]  # red rectangle
    img[15:25, 15:25] = [255, 255, 255]  # white center
    return img


def create_document_with_logos(doc_size=(800, 600), logo_positions=None) -> np.ndarray:
    if logo_positions is None:
        logo_positions = [(100, 100), (400, 200), (600, 400)]
    doc = np.ones((*doc_size[::-1], 3), dtype=np.uint8) * 240
    logo = create_logo()
    lh, lw = logo.shape[:2]
    for x, y in logo_positions:
        doc[y : y + lh, x : x + lw] = logo
    return doc


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    logo = create_logo()
    Image.fromarray(logo).save(os.path.join(OUTPUT_DIR, "query_logo.png"))
    print("Created query_logo.png")

    doc = create_document_with_logos()
    Image.fromarray(doc).save(os.path.join(OUTPUT_DIR, "doc_with_3_logos.png"))
    print("Created doc_with_3_logos.png (3 matches expected)")

    doc_empty = np.ones((600, 800, 3), dtype=np.uint8) * 240
    Image.fromarray(doc_empty).save(os.path.join(OUTPUT_DIR, "doc_empty.png"))
    print("Created doc_empty.png (0 matches expected)")


if __name__ == "__main__":
    main()
