from pathlib import Path

from organoid_analyzer import organoid_analyzer as oa


def process_timeseries_images(input_directory, output_directory, **kwargs):
    """
    Process timeseries images.

    This function parses the timeseries data folder and calls the organoid-analyzer
    functions appropriately. The data is expected to be grouped by two levels of folders: Day > Genotype > image file (e.g., D7/sp7/0014.tif)

    Parameters
    ----------
    input_directory : _type_
        _description_
    output_directory : _type_
        _description_

    Raises
    ------
    FileNotFoundError
        _description_
    ValueError
        _description_
    FileNotFoundError
        _description_
    FileNotFoundError
        _description_
    FileNotFoundError
        _description_
    """

    #

    # Check if inputs are valid paths
    if isinstance(input_directory, str):
        input_directory = Path(input_directory)

    if not input_directory.exists():
        raise FileNotFoundError(f"The directory {input_directory} does not exist.")
    elif not input_directory.is_dir():
        raise ValueError(f"The input {input_directory} is not a directory.")

    # Check if output directory exists and creating it if not
    if isinstance(output_directory, str):
        output_directory = Path(output_directory)

    if not output_directory.exists():
        output_directory.mkdir(parents=True)

    # Generate a list to hold all data
    all_data = []

    # Navigate the directory structure
    time_dirs = get_subdirs(input_directory)

    if not time_dirs:
        raise FileNotFoundError(
            f"The directory {input_directory} does not seem to contain the expected sub-directories. Check if the directory structure is correct and that you are specifying the correct directory level."
        )

    for d in time_dirs:
        # Get a list of genotype directories
        gtype_dirs = get_subdirs(d)

        if not gtype_dirs:
            raise FileNotFoundError(
                f"The directory {d} does not seem to contain the expected sub-directories. Check if the directory structure is correct and that you are specifying the correct directory level."
            )

        for g in gtype_dirs:
            output_subdir = output_directory / g.parent.name / g.name
            # Try to resume - if the folder contains a "merged.csv" then skip it
            if (output_subdir / "merged.csv").exists():
                print("Merged CSV exists. Skipping directory.")
            else:
                try:
                    oa.process_directory(g, output_subdir, **kwargs)
                except ValueError:
                    print("Error occured: Skipping the rest.")

    # full_ds = xr.concat(all_data, dim="cell_index", join="outer", data_vars="all")

    # # Save data
    # ds_flattened = full_ds.reset_index("cell_index")
    # ds_flattened.to_netcdf(output_directory / "data.nc")

    # df_final = full_ds.to_dataframe()
    # df_final.to_csv(output_directory / "data.csv", index=True)


def get_subdirs(directory_path):

    subdirs = [x for x in directory_path.iterdir() if x.is_dir()]
    return subdirs
