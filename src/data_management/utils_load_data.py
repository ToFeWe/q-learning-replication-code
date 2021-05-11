"""

Collection of utility function
used in different data management
scripts.
"""
import pickle
from os import walk


def load_folder_files(file_path):
    """
    A function to load all files in a given
    directory and return it as a list.
    Note that its assumed that in the folder
    all files are pickle files.

    Args:
        file_path (string): Path to the files

    Returns:
        list: List of elements that were stored in the
              the pickle files.
    """
    # Get all files
    all_files = []
    for (dirpath, dirnames, filenames) in walk(file_path):
        all_files.extend(filenames)
        break

    # Load the files
    out_results = []
    for file in all_files:
        in_path = file_path + "\\" + file
        with open(in_path, "rb") as f:
            out_results.append(pickle.load(f))

    return out_results
