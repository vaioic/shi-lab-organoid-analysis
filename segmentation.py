import skimage
from scipy import ndimage as ndi
import numpy as np
from matplotlib import pyplot as plt

def segment_cells(image, thresh=0.99):

    mask = image < (thresh * np.max(image))  # Note: Most images have a saturated white background

    mask = skimage.morphology.opening(mask, skimage.morphology.disk(10))
    mask = skimage.morphology.remove_small_holes(mask, max_size=50)

    # plt.imshow(mask)
    # plt.show()
    # exit()
    
    distance = ndi.distance_transform_edt(mask)

    # plt.imshow(distance)
    # plt.show()

    # coords = skimage.feature.peak_local_max(distance, footprint=np.ones((3, 3)), labels=mask, threshold_abs=(0.4 * np.max(distance)), min_distance=50)

    coords = skimage.feature.peak_local_max(distance, footprint=skimage.morphology.disk(15), labels=mask, threshold_abs=35, min_distance=60)

    mask_marker = np.zeros(distance.shape, dtype=bool)
    mask_marker[tuple(coords.T)] = True
    markers, _ = ndi.label(mask_marker)

    # plt.imshow(image)
    # print(coords)
    # plt.scatter(coords[:, 1], coords[:, 0])
    # plt.show()
    # exit()
    
    labels = skimage.segmentation.watershed(-distance, markers, mask=mask)
    
    labels = skimage.segmentation.clear_border(labels)        
    labels = skimage.morphology.remove_small_objects(labels, max_size=200)

    # Do a global threshold to determine dark/light threshold
    thresh_cell = skimage.filters.threshold_otsu(image[labels > 0])
   
    inner_cell_mask = image >= thresh_cell
    
    inner_cell_labels = labels.copy()
    inner_cell_labels[~inner_cell_mask] = 0

    return (labels, inner_cell_labels)

def segment_cells_v2(image_path, thresh=0.90):

    image = skimage.io.imread(image_path)
    image_gray = skimage.color.rgb2gray(image)

    inverted_image = skimage.util.invert(image_gray)
    clean_image = skimage.filters.median(inverted_image, footprint=skimage.morphology.disk(15))    

    blobs = skimage.feature.blob_log(clean_image, min_sigma=12, max_sigma=70, threshold=0.2, num_sigma=10)

    mask = image_gray < (thresh * np.max(image_gray)) 

    mask = skimage.morphology.opening(mask, skimage.morphology.disk(10))
    mask = skimage.morphology.remove_small_holes(mask, max_size=50)

    distance = ndi.distance_transform_edt(mask)

    coords = blobs[:, :2].astype(int)

    mask_marker = np.zeros(distance.shape, dtype=bool)
    mask_marker[coords[:, 0], coords[:, 1]] = True
    markers, _ = ndi.label(mask_marker)

    labels = skimage.segmentation.watershed(-distance, markers, mask=mask)
    
    labels = skimage.segmentation.clear_border(labels)        

    labels = remove_small_labels(labels, max_size=200)

    labels = remove_small_holes_labels(labels, max_size=200)

    plt.imshow(labels)
    plt.scatter(blobs[:, 1], blobs[:, 0], s=2)
    plt.show()

def remove_small_labels(labels, max_size=10):

    new_labels = np.copy(labels)
    for prop in skimage.measure.regionprops(labels):
        if prop.area < max_size:
            new_labels[labels == prop.label] == 0

    return new_labels

def remove_small_holes_in_objects(labels, max_size=10):

    new_labels = np.copy(labels)
    unique_ids = np.unique(labels)

    #print(unique_ids)

    for id in unique_ids:

        if id == 0:
            # Don't process the background
            continue

        curr_mask = np.zeros_like(new_labels, dtype=bool)
        curr_mask[labels == id] = True

        # plt.subplot(1, 2, 1)
        # plt.imshow(curr_mask)

        curr_mask = skimage.morphology.remove_small_holes(curr_mask, max_size=max_size)

        # plt.subplot(1, 2, 2)
        # plt.imshow(curr_mask)
        # plt.show()

        new_labels[curr_mask] = id
        
    return new_labels

def segment(image, threshold=0.98, h_factor=0.4, circularity_bias=0.5, separation_factor=0.8, gauss_sigma=1.0):
    """
    Segment organoids in brightfield images. This algorithm attempts to identify dark objects against a light background, as well as attempting to separate touching objects using the watershed algorithm.

    This algorithm is designed to be scale-invariant and should work on different object sizes. To do this, the algorithm calculates average object sizes and uses this to inform the watershedding process.

    Additionally, the watershedding uses both the distance matrix and the intensity of the object. This helps provide control over the final result.    

    Parameters
    ----------
    image : array-like
        Image data. The data should be converted into grayscale first.
    threshold : float
        Threshold factor, dy default 0.98. Increase this value if objects are being missed. Decrease this value if too much background is being included.
    h_factor : float, optional
        How dark the center of an object must be to be, by default 0.4. Increase this value if there are too many markers in the middle of a single large blob. Decrease if faint objects are being missed.
    circularity_bias : float, optional
        Controls the shape of the watershed, by default 0.5. A higher value forces the watershed ridge lines to follow the distance transform more than the intensity of the image.
    separation_factor : float, optional
        How far apart should objects be, by default 0.8. The factor is used as a multiplier of the distance between objects (which is calculated automatically)
    gauss_sigma : float, optional
        Sigma of the Gaussian function used to blur the image, by default 1. Increase this value if watershed boundaries of objects are leaking into neighbors.

    Returns
    -------
    labels : ndarray(dtype=float)
        Label matrix of identified objects. Each object will have a unique label in the matrix.
    object_coords : ndarray(dtype=int)
        The [y, x] centers of the objects used as markers in the watershedding.
    """

    # Pre-process the image to clean up noise
    denoised = skimage.filters.median(image, skimage.morphology.disk(10))

    denoised = (denoised - (1.03 * np.min(denoised)))/((0.93 * np.max(denoised)) - (1.03 * np.min(denoised)))

    denoised[denoised > 1.0] = 1.0
    denoised[denoised < 0.0] = 0.0

    mask = denoised < threshold

    # Clean up the mask
    mask = skimage.morphology.opening(mask, skimage.morphology.disk(10))

    mask = skimage.morphology.remove_small_objects(mask, max_size=3000)
    mask = skimage.morphology.remove_small_holes(mask, max_size=100)

    # Further blur the image to remove any internal structure
    blurred = skimage.filters.gaussian(denoised, gauss_sigma)    

    # Refine the markers based on expected size of the object
    distance = ndi.distance_transform_edt(mask)

    # Blend the watershed with the distance transform to generate a hybrid map 
    # that takes both distance and the intensity profile into account.
    blurred_rescaled = (blurred - np.min(blurred)) / (np.max(blurred) - np.min(blurred))

    distance_rescaled = 1.0 - (distance / (np.max(distance) + 1e-8))

    hybrid = ((1 - circularity_bias) * blurred_rescaled) + (circularity_bias * distance_rescaled)

    # Mark the centers of each object
    h_value = np.std(hybrid) * h_factor
    h_minima = skimage.morphology.h_minima(hybrid, h=h_value)

    coords = np.column_stack(np.where(h_minima > 0))

    # Sort coords by distance: largest/deepest objects first
    # This ensures big blobs claim their area before small noise markers
    dist_values = distance[tuple(coords.T)]
    coords = coords[np.argsort(dist_values)[::-1]]
    
    final_markers_mask = np.zeros_like(image, dtype=int)
    kept_coords = []

    for coord in coords:
        y, x = coord
        # The exclusion radius is relative to the object's thickness at this point
        local_exclusion_r = distance[y, x] * separation_factor
        
        # Check against markers we've already accepted
        is_too_close = False
        for k_coord in kept_coords:
            # Euclidean distance check
            d = np.sqrt((y - k_coord[0])**2 + (x - k_coord[1])**2)
            if d < local_exclusion_r:
                is_too_close = True
                break
        
        if not is_too_close:
            kept_coords.append(coord)
            final_markers_mask[y, x] = 1

    # Label the filtered markers and watershed the smoothed intensity image
    markers = skimage.morphology.label(final_markers_mask)
    labels = skimage.segmentation.watershed(hybrid, markers, mask=mask)

    labels = skimage.segmentation.clear_border(labels)

    labels = remove_small_holes_in_objects(labels, max_size=50000)


    object_coords = np.array(kept_coords)

    # plt.imshow(blurred)
    # plt.scatter(kept_coords[:, 1], kept_coords[:, 0], 3)
    # plt.show()
    # exit()

    return labels, object_coords