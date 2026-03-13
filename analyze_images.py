import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage as ndi
import skimage
import csv
from core_utils import imoverlay
from segmentation import segment_cells, segment_cells_v2, segment
from tqdm import tqdm
from pathlib import Path, PurePath
import argparse
import xarray as xr
import pandas as pd
import pdb
import warnings
import re

# def process_images(input_directory, output_directory, file_ext=".tif"):

#     # Check if inputs are valid paths
#     if not isinstance(input_directory, PurePath):
#         input_directory = Path(input_directory)

#     if not input_directory.exists():
#         raise FileNotFoundError(f"The directory {input_directory} does not exist.")
    
#     # Check if output directory exists and creating it if not    
#     if not isinstance(output_directory, PurePath):
#         output_directory = Path(output_directory)

#     if not output_directory.exists():
#         output_directory.mkdir()

#     # Begin processing


#     for f in tqdm(files_list):

#         file = os.path.join(data_directory, f)
        
#         if os.path.isfile(file):
#             #print(f"Processing file: {file}")

#             # Determine output filename
#             fn = os.path.splitext(os.path.basename(file))[0]

#             # Read in image
#             image = skimage.io.imread(file)
#             image = skimage.color.rgb2gray(image)
            
#             # Identify the EB cells

#             if (fn == "HET66-1 2X") or (fn == "HET66-2 2X") or (fn == "HET66-3 2X"):
#                 # Handle these images
#                 labels, inner_cell_labels = segmentation.segment_cells(image, thresh = 0.95)
#             else:        
#                 labels, inner_cell_labels = segmentation.segment_cells(image)

#             # Measure properties
#             cell_props = skimage.measure.regionprops(labels)
#             inner_cell_props = skimage.measure.regionprops(inner_cell_labels)

#             mean_distances = []

#             for p in tqdm(cell_props, leave=False):
                
#                 # Calculate the average thickness of bright regions
#                 curr_cell_mask = np.zeros(labels.shape, dtype=np.bool)
#                 curr_cell_mask[labels == p['label']] = True

#                 contours = skimage.measure.find_contours(curr_cell_mask)

#                 # Return the longest contour
#                 longest = sorted(contours, key=len, reverse=True)[:1]
#                 longest = np.array(longest[0], dtype=int)

#                 curr_inner_mask = np.zeros(inner_cell_labels.shape, dtype=np.bool)
#                 curr_inner_mask[inner_cell_labels == p['label']] = True

#                 # Make a mask that leaves only the center region false
#                 curr_inner_mask_bg_filled = curr_inner_mask + (labels != p['label'])
#                 curr_inner_mask_bg_filled = skimage.morphology.remove_small_holes(curr_inner_mask_bg_filled, 500)

#                 curr_dist = ndi.distance_transform_edt(curr_inner_mask_bg_filled)

#                 mean_distances.append(np.mean(curr_dist[longest[:, 0], longest[:, 1]]))


#             # Save output
#             with open(os.path.join(output_directory, fn + ".csv"), 'w', newline='') as file:
            
#                 writer = csv.writer(file, delimiter=",")   
            
#                 #Write CSV headers
#                 writer.writerow(["Cell", "Label", "Total area (px)", "Bright region area (px)", "Ratio (Bright/Total)", "Mean Thickness (px)"])
            
#                 ctr = 0
#                 for p in cell_props:
#                     writer.writerow([ctr + 1, p.label, p.area, inner_cell_props[ctr].area, inner_cell_props[ctr].area/p.area, mean_distances[ctr]])
#                     ctr += 1
                    
#             ovimg = imoverlay(image, inner_cell_labels, [0, 1, 0, 0.4], plot_outlines=False)
#             skimage.io.imsave(os.path.join(output_directory, fn + ".png"), ovimg)

#             #print('\b...DONE', flush=True)

def process_timeseries_images(input_directory, output_directory, image_ext="tif"):

    # Assuming here that data is grouped by two levels of folders: Day > Genotype > image file (e.g., D7/sp7/0014.tif)

    # Check if inputs are valid paths
    if not isinstance(input_directory, PurePath):
        input_directory = Path(input_directory)

    if not input_directory.exists():
        raise FileNotFoundError(f"The directory {input_directory} does not exist.")
    elif not input_directory.is_dir():
        raise ValueError(f"The input {input_directory} is not a directory.")
    
    # Check if output directory exists and creating it if not
    if not isinstance(output_directory, PurePath):
        output_directory = Path(output_directory)

    if not output_directory.exists():
        output_directory.mkdir()

    # Generate a list to hold all data
    all_data = []

    # Navigate the directory structure
    time_dirs = get_subdirs(input_directory)

    if not time_dirs:
        raise FileNotFoundError(f"The directory {input_directory} does not seem to contain the expected sub-directories. Check if the directory structure is correct and that you are specifying the correct directory level.")

    for d in time_dirs:

        # Get a list of genotype directories
        gtype_dirs = get_subdirs(d)

        if not gtype_dirs:
            raise FileNotFoundError(f"The directory {d} does not seem to contain the expected sub-directories. Check if the directory structure is correct and that you are specifying the correct directory level.")
        
        for g in gtype_dirs:

            # Get a list of images
            image_files = list(g.glob(f"*.{image_ext}"))

            if not image_files:
                raise FileNotFoundError(f"The directory {g} does not seem to contain any images. Check that the image_ext is correct.")
            
            for f in image_files:
                print(f)
                props, overlay = process_image(f, threshold=0.90)

                # Build an xarray Dataset
                df = pd.DataFrame(props)

                df['genotype'] = (f.parent.name).lower()
                df['day'] = (f.parent.parent.name).lower()
                df['image'] = f.name

                xds = df.to_xarray()
                xds = xds.set_index(index=["genotype", "day", "image", "label"]).rename({'index':'cell_index'})

                # Append to data
                all_data.append(xds)

                fig, ax = plt.subplots(figsize=(12, 10))
                ax.imshow(overlay)

                for i in range(len(xds.cell_index)):
                    cell = xds.isel(cell_index=i)

                    y, x = cell['centroid-0'].values, cell['centroid-1'].values
                    lbl = int(cell['label'].values)

                    ax.text(x, y, str(lbl), color='yellow', fontsize=8,        ha='center', va='center', fontweight='bold',
                    bbox=dict(facecolor='black', alpha=0.4, pad=0.5, edgecolor='none'))

                fig.canvas.draw()
                annotated_img = np.asarray(fig.canvas.renderer.buffer_rgba())

                # Create sub-directories
                fig_output_dir = output_directory / f.parent.parent.name / f.parent.name
                if not fig_output_dir.exists():
                    fig_output_dir.mkdir(parents=True)
                skimage.io.imsave(fig_output_dir / (f.stem + ".png"), annotated_img)

                plt.close()

    full_ds = xr.concat(all_data, dim="cell_index", join="outer", data_vars="all")

    # Save data
    ds_flattened = full_ds.reset_index("cell_index")
    ds_flattened.to_netcdf(output_directory / "data.nc")

    df_final = full_ds.to_dataframe()
    df_final.to_csv(output_directory / "data.csv", index=True)     

def process_images_in_dir(input_directory, output_directory, image_ext="tif", additional_coords=None, genotype_by=None, include_subdirs=False, threshold=0.90, spacing=None):

    # Check if inputs are valid paths
    if isinstance(input_directory, str):
        input_directory = Path(input_directory)
    elif isinstance(input_directory, PurePath):
        # Do nothing
        pass
    else:
        raise ValueError("Input directory must be a str or Path.")

    # Check that the input is a directory
    if not input_directory.is_dir():        
        raise ValueError(f"The input {input_directory} is not a directory.")
        
    # Check if output directory exists and creating it if not
    if isinstance(output_directory, str):
        output_directory = Path(output_directory)
    elif isinstance(output_directory, PurePath):
        pass
    else:
        raise ValueError("Output directory must be a str or Path.")  

    # Create the output directory if it doesn't already exist
    if not output_directory.exists():
        output_directory.mkdir(parents=True)

    # Get a list of all matching images
    file_list = get_files(input_directory, include_subdirs=include_subdirs, file_ext=image_ext)

    if not file_list:
        raise FileNotFoundError(f"The directory {input_directory} does not contain any files matching {image_ext}.")
    
    # Initialize a list
    result = []
    
    for f in file_list:

        print(f)
        props, overlay = process_image(f, threshold=threshold, spacing=spacing)

        # Generate the coordinates
        num_cells = len(props['label'])

        if genotype_by is None:
            genotype_label = "Unspecified"
        elif genotype_by == "dir":
            genotype_label = str(f.parent.name).lower()
        elif genotype_by == "file":
            filename = str(f.stem).lower()
            match = re.match(r"^[a-zA-Z]+", filename)

            if not match:
                raise ValueError(f"The filename '{filename}' was expected to start with letters.")
            
            genotype_label = match.group()
        else:
            raise ValueError(f"Invalid genotype_by: '{genotype_by}'. Expected None, 'dir', or 'file'.")        

        # Build an xarray Dataset using "id" as the indexing variable
        curr_ds = xr.Dataset(
            data_vars={key: (['id'], value) for key, value in props.items()},
            coords={
                "image": ("id", [str(f.name)] * num_cells),
                "genotype": ("id", [genotype_label] * num_cells)
            }
        )

        if additional_coords:
            curr_ds = curr_ds.assign_coords(additional_coords)
        
        result.append(curr_ds)       

        # Generate a labeled image
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.imshow(overlay)

        for i in range(len(curr_ds.id)):
            cell = curr_ds.isel(id=i)

            # Handle the potential scaling of centroid values
            if spacing:
                y, x = cell['centroid-0'].values / spacing, cell['centroid-1'].values / spacing
            else:
                y, x = cell['centroid-0'].values, cell['centroid-1'].values

            lbl = int(cell['label'].values)

            ax.text(x, y, str(lbl), color='yellow', fontsize=8,        ha='center', va='center', fontweight='bold',
            bbox=dict(facecolor='black', alpha=0.4, pad=0.5, edgecolor='none'))

        fig.canvas.draw()
        annotated_img = np.asarray(fig.canvas.renderer.buffer_rgba())

        # Create output (sub-)directories as needed
        if include_subdirs:
            fig_output_dir = output_directory / f.parent.name
        else:
            fig_output_dir = output_directory

        if not fig_output_dir.exists():
            fig_output_dir.mkdir(parents=True)

        skimage.io.imsave(fig_output_dir / (f.stem + ".png"), annotated_img)

        plt.close()

    # Combine all the datasets
    ds = xr.concat(result, dim="id", join="outer")

    # Save data
    ds.to_netcdf(output_directory / "data.nc")

    # Convert to DataFrame and save
    df = ds.to_dataframe()
    df.to_csv(output_directory / "data.csv", index=True)


def get_subdirs(directory_path):

    subdirs = [x for x in directory_path.iterdir() if x.is_dir()]
    return subdirs

def get_files(root_dir, include_subdirs=False, file_ext=".tif"):
    """
    Get files from a directory or sub-directories

    Parameters
    ----------
    root_dir : str
        String containing the location of the directory
    include_subdirs : bool, optional
        If True, the function will return all matching files no matter the sub-directory level, by default False
    file_ext : str or list of str, optional
        Specifies the extension(s) of the files to return, by default ".tif"

    Returns
    -------
    list of Path
        Returns a list of pathlib.Paths for files matching the specified criteria.

    Raises
    ------
    ValueError
        If the root_dir is not a valid directory.
    ValueError
        If file_ext is not a str or list of str.
    """

    root_path = Path(root_dir)

    if not root_path.is_dir():
        raise ValueError(f"The path {root_path} is not a valid directory.")
    
    # Standardize file_ext into a set of lowercase strings
    if isinstance(file_ext, str):
        exts = {file_ext.lower() if file_ext.startswith('.') else f".{file_ext.lower()}"}
    elif isinstance(file_ext, list):
        exts = {e.lower() if e.startswith('.') else f".{e.lower()}" for e in file_ext}
    else:
        raise ValueError(f"file_ext must be a string or list of strings.")

    if include_subdirs:
        all_items = [f for f in root_path.rglob("*") if f.is_file()]
    else:
        all_items = [f for f in root_path.glob("*") if f.is_file()]

    # Filter the returned list by extension
    files = [f for f in all_items if f.suffix.lower() in exts]

    if not files:
        warnings.warn(f"No matching files were found. Check the file_ext and the include_subdirs flag.")

    return files


def process_image(file, spacing=None, **kwargs):
    """
    Identifies cells and measures cell properties in an image.

    Parameters
    ----------
    file : str or Path
        Location of file

    Returns
    -------
    props : dict
        Dictionary mapping property names to the value of that property.
    overlay : ndarray
        Array containing the input image overlaid wih boundaries of the each object.
    """

    image = skimage.io.imread(file)
    image_gray = skimage.color.rgb2gray(image)

    labels, _ = segment(image_gray, **kwargs)

    # microns_per_pixel = (1 / 594) * 1000

    # Measure cell properties
    cell_props = skimage.measure.regionprops_table(labels, properties=('label', 'area', 'feret_diameter_max', 'eccentricity', 'centroid'), spacing=spacing)

    # # Filter data and labels by size
    # areas = props['area']

    # area_threshold = np.mean(areas) - (5 * np.std(areas))

    # Generate an overlay image
    overlay = skimage.segmentation.mark_boundaries(image, labels, color=(0, 1, 0), mode='thick')

    return cell_props, overlay


def segment_and_plot(image_path, threshold):    

    if not isinstance(image_path , PurePath):
        image_path = Path(image_path)

    image = skimage.io.imread(image_path)
    image_gray = skimage.color.rgb2gray(image)

    labels, _ = segment(image_gray, threshold=threshold)

    overlay = skimage.segmentation.mark_boundaries(image, labels, color=(0, 1, 0), mode='thick')

    plt.imshow(overlay)
    plt.show()


def test_func():

    # files = r'\\pn.vai.org\projects\wen\vari-core-generated-data\OIC\OIC 01272026 Junwei'
    files2 = r'D:\Projects\OIC-267\data\20250927 real test batch1\D2'

    process_images_in_dir(files2, '../processed/test', include_subdirs=True, additional_coords={'Day': 2}, genotype_by="dir", spacing=(1000/594))

    files = r'D:\Projects\OIC-267\data\20250927 real test batch1\D6'

    process_images_in_dir(files, '../processed/test_d6', include_subdirs=True, additional_coords={'Day': 6}, genotype_by="dir", spacing=(1000/594))


    # files = [r'D:\Projects\OIC-267\data\20250927 real test batch1\D30\D64\0126.tif',
    #          r'D:\Projects\OIC-267\data\20250927 real test batch1\D30\C34\0052.tif',
    #          r'D:\Projects\OIC-267\data\20250927 real test batch1\D2\c34\0019.tif']
    
    # ctr = 1
    
    # for f in files:

    #     image = skimage.io.imread(f)
    #     image_gray = skimage.color.rgb2gray(image)

    #     labels, _ = segment(image_gray)

    #     overlay = skimage.segmentation.mark_boundaries(image, labels, color=(0, 1, 0), mode='thick')

    #     plt.subplot(1, 3, ctr)
    #     plt.imshow(overlay)

    #     ctr += 1

    # plt.show()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Analyze images of neuronal organoids.")
    parser.add_argument("filepath", help="Path(s) to images")
    parser.add_argument("-o", "--outputdir", help="Path to save data to", default='')
    parser.add_argument("-l", "--threshold", type=float, default=0.90, help="Threshold percentage (0 - 1)")
    parser.add_argument("-s", "--segmentonly", action="store_true", help="If True then only segment and plot the mask.")
    parser.add_argument("-t", "--timeseries", action="store_true", help="If True process data as a timeseries.")
    parser.add_argument("-e", "--extension", type=str, default="tif", help="Extension of image files.")
    parser.add_argument("-x", "--testonly", action="store_true", help="Only run current function I'm testing")

    args = parser.parse_args()

    if args.segmentonly:
        segment_and_plot(args.filepath, args.threshold)
    elif args.testonly:
        test_func()
    elif args.timeseries:
        process_timeseries_images(args.filepath, args.outputdir, image_ext=args.extension)
    else:

        pass