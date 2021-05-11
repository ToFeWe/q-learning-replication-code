"""

A module to load the data from the
super star simulations and write it
to a single file.
"""
import pickle
import sys

from bld.project_paths import project_paths as pp
from bld.project_paths import project_paths_join as ppj
from src.data_management.utils_load_data import load_folder_files


def load_and_write_super_star_data(in_path, out_path):
    """
    A function to load all raw super star simulation data
    which is spread across different files and store
    it as a single pickle files.
    It is assumed that all raw simulation files can be found
    under the *in_path* and are pickle.

    Args:
        in_path (string): File path under which the files are stored
        out_path (string): Path to the file we write the list of
                           super star simulation outputs to.
    """
    list_all_super_stars = load_folder_files(file_path=in_path)

    with open(out_path, "wb") as outfile:
        pickle.dump(list_all_super_stars, outfile)


if __name__ == "__main__":
    n_agents = sys.argv[1]

    IN_PATH = pp[f"IN_SIMULATION_SUPER_STARS_{n_agents}_AGENT"]
    OUT_FILE_PATH = ppj("OUT_DATA", f"all_super_stars_{n_agents}_agents.pickle")
    load_and_write_super_star_data(in_path=IN_PATH, out_path=OUT_FILE_PATH)
