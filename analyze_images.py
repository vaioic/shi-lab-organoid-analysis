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

def process_images(input_directory, output_directory, file_ext=".tif"):

    # Check if inputs are valid paths
    if not isinstance(input_directory, PurePath):
        input_directory = Path(input_directory)

    if not input_directory.exists():
        raise FileNotFoundError(f"The directory {input_directory} does not exist.")
    
    # Check if output directory exists and creating it if not    
    if not isinstance(output_directory, PurePath):
        output_directory = Path(output_directory)

    if not output_directory.exists():
        output_directory.mkdir()

    # Begin processing


    for f in tqdm(files_list):

        file = os.path.join(data_directory, f)
        
        if os.path.isfile(file):
            #print(f"Processing file: {file}")

            # Determine output filename
            fn = os.path.splitext(os.path.basename(file))[0]

            # Read in image
            image = skimage.io.imread(file)
            image = skimage.color.rgb2gray(image)
            
            # Identify the EB cells

            if (fn == "HET66-1 2X") or (fn == "HET66-2 2X") or (fn == "HET66-3 2X"):
                # Handle these images
                labels, inner_cell_labels = segmentation.segment_cells(image, thresh = 0.95)
            else:        
                labels, inner_cell_labels = segmentation.segment_cells(image)

            # Measure properties
            cell_props = skimage.measure.regionprops(labels)
            inner_cell_props = skimage.measure.regionprops(inner_cell_labels)

            mean_distances = []

            for p in tqdm(cell_props, leave=False):
                
                # Calculate the average thickness of bright regions
                curr_cell_mask = np.zeros(labels.shape, dtype=np.bool)
                curr_cell_mask[labels == p['label']] = True

                contours = skimage.measure.find_contours(curr_cell_mask)

                # Return the longest contour
                longest = sorted(contours, key=len, reverse=True)[:1]
                longest = np.array(longest[0], dtype=int)

                curr_inner_mask = np.zeros(inner_cell_labels.shape, dtype=np.bool)
                curr_inner_mask[inner_cell_labels == p['label']] = True

                # Make a mask that leaves only the center region false
                curr_inner_mask_bg_filled = curr_inner_mask + (labels != p['label'])
                curr_inner_mask_bg_filled = skimage.morphology.remove_small_holes(curr_inner_mask_bg_filled, 500)

                curr_dist = ndi.distance_transform_edt(curr_inner_mask_bg_filled)

                mean_distances.append(np.mean(curr_dist[longest[:, 0], longest[:, 1]]))


            # Save output
            with open(os.path.join(output_directory, fn + ".csv"), 'w', newline='') as file:
            
                writer = csv.writer(file, delimiter=",")   
            
                #Write CSV headers
                writer.writerow(["Cell", "Label", "Total area (px)", "Bright region area (px)", "Ratio (Bright/Total)", "Mean Thickness (px)"])
            
                ctr = 0
                for p in cell_props:
                    writer.writerow([ctr + 1, p.label, p.area, inner_cell_props[ctr].area, inner_cell_props[ctr].area/p.area, mean_distances[ctr]])
                    ctr += 1
                    
            ovimg = imoverlay(image, inner_cell_labels, [0, 1, 0, 0.4], plot_outlines=False)
            skimage.io.imsave(os.path.join(output_directory, fn + ".png"), ovimg)

            #print('\b...DONE', flush=True)

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

    # TODO: Test if the data loads back correctly           
    
    # Note: 
    # When you load it back (xr.open_dataset), you will need to run .set_index(cell_index=["image_id", "label_id"]) again to restore your sorting/selection powers.

def get_subdirs(directory_path):

    subdirs = [x for x in directory_path.iterdir() if x.is_dir()]
    return subdirs

def process_image(file, **kwargs):

    image = skimage.io.imread(file)
    image_gray = skimage.color.rgb2gray(image)

    labels, _ = segment(image_gray, **kwargs)

    # microns_per_pixel = (1 / 594) * 1000

    # Measure cell properties
    cell_props = skimage.measure.regionprops_table(labels, properties=('label', 'area', 'feret_diameter_max', 'eccentricity', 'centroid'))

    # Generate an overlay image
    overlay = skimage.segmentation.mark_boundaries(image, labels, color=(0, 1, 0), mode='thick')

    return cell_props, overlay


def segment_and_plot(image_path, **kwargs):    

    if not isinstance(image_path , PurePath):
        image_path = Path(image_path)

    image = skimage.io.imread(image_path)
    image_gray = skimage.color.rgb2gray(image)

    labels, _ = segment(image_gray, **kwargs)

    overlay = skimage.segmentation.mark_boundaries(image, labels, color=(0, 1, 0), mode='thick')

    plt.imshow(overlay)
    plt.show()


def test_func():

    files = [r'D:\Projects\OIC-267\data\20250927 real test batch1\D30\D64\0126.tif',
             r'D:\Projects\OIC-267\data\20250927 real test batch1\D30\C34\0052.tif',
             r'D:\Projects\OIC-267\data\20250927 real test batch1\D2\c34\0019.tif']
    
    ctr = 1
    
    for f in files:

        image = skimage.io.imread(f)
        image_gray = skimage.color.rgb2gray(image)

        labels, _ = segment(image_gray)

        overlay = skimage.segmentation.mark_boundaries(image, labels, color=(0, 1, 0), mode='thick')

        plt.subplot(1, 3, ctr)
        plt.imshow(overlay)

        ctr += 1

    plt.show()


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