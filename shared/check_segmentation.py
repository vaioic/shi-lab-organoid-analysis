from shared.segmentation import segment_cells
from shared.core_utils import imoverlay
import skimage
from pathlib import Path, PurePath
from matplotlib import pyplot as plt
import argparse
import numpy as np


def segment_and_plot(image_path, thresh=0.90):

    if not isinstance(image_path, PurePath):
        image_path = Path(image_path)

    image = skimage.io.imread(image_path)
    image_gray = skimage.color.rgb2gray(image)

    labels, inner_cell_labels = segment_cells(image_gray, thresh=thresh)

    plt.imshow(labels)
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Segment and plot an image.")
    parser.add_argument("filepath", help="Path to image file")
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.90,
        help="Threshold percentage (0 - 1)",
    )

    args = parser.parse_args()
    segment_and_plot(args.filepath, args.threshold)
