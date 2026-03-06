import skimage
import numpy as np

# Define function to generate overlay images
def imoverlay(image_A, image_B, color=[0, 1, 0], plot_outlines=True, normalize=True):
    # Always assume that image_A is supposed to be an image
    # Image_B can be an image, binary mask, or label

    # if normalize:
    #     if image_A.ndims == 1:
    #         image_A = 
    #     for c in range(image_A)
    

    if plot_outlines and (image_B.ndim == 2):
        image_B = skimage.segmentation.find_boundaries(image_B)
    else:
        image_B = image_B > 0
    # plt.imshow(outlines)

    image_out = np.zeros((image_A.shape[0], image_A.shape[1], 3), np.uint8)

    for c in range(3):
        if image_A.ndim < 3:
            curr_slice = (image_A - np.min(image_A))/(np.max(image_A) - np.min(image_A)) * 255
        else:
            curr_slice = image_A[:, :, c]            

        if len(color) < 4:
            alpha = 1
        else:
            alpha = color[3]
            
        curr_slice[image_B] = (color[c] * 255 * alpha) + ((1 - alpha) * curr_slice[image_B])
        image_out[:, :, c] = curr_slice

    return image_out