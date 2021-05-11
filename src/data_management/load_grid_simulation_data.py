"""

A module to load the data from the Monte Carlo
simulation
"""
import json
import pickle
import sys
from copy import copy

import numpy as np

from bld.project_paths import project_paths as pp
from bld.project_paths import project_paths_join as ppj
from src.data_management.utils_load_data import load_folder_files


def load_grid_simulation_data(file_path):
    """
    Load all files from the grid search simulation which are stored in the
    directory *file_path* and write them to a list of lists.
    Each list then contains the arrays for all simulation


    Args:
        file_path (string): Path to the simulation files

    Returns:
        list: list of list with the outcome arrays
              for all MC simulation.

              Ordered the following way:
              list[0]: Arrays of the convergence state profitability
              list[1]: Arrays with the weighted profitability
              list[2]: Arrays with the best response shares
              list[3]: Array with the average profitability
              list[4]: Array with the average price after convergence
              list[5]: Array with the Nash equilibria
              list[6]: All super star agents in the grid search
    """
    # Get all files
    simulation_results = load_folder_files(file_path=file_path)

    # Unroll the dictionaries
    all_dicts = [d.values() for d in simulation_results]

    # TODO: Add a check here that all simulations are used and the seeds are all
    # unique
    # TODO: Similar Code used in simulation part which is NOT in waf
    # Should be refactored!
    return all_dicts


def sim_results_to_dict(file_path):
    """

    Returns the simulation results arrays.


    Args:
        file_path (string): Path to the simulation files

    Returns:
        dict: Dict with all simulation results arrays
    """
    all_simulation_dicts = load_grid_simulation_data(file_path=file_path)

    # Dropping the super star tuple here.
    (
        state_profitability_array,
        weighted_profitability_array,
        best_response_share_array,
        avg_profit_array,
        avg_price_array,
        nash_equilibrium_array,
        _,
    ) = zip(*all_simulation_dicts)

    all_arrays = {}
    all_arrays["state_profitability"] = state_profitability_array
    all_arrays["weighted_profitability"] = weighted_profitability_array
    all_arrays["best_response_share"] = best_response_share_array
    all_arrays["avg_profit"] = avg_profit_array
    all_arrays["avg_price"] = avg_price_array
    all_arrays["nash_equilibrium"] = nash_equilibrium_array

    return all_arrays


if __name__ == "__main__":
    n_agents = sys.argv[1]

    # Load all data from project path
    OUT_ARRAYS = sim_results_to_dict(pp[f"IN_SIMULATION_GRID_{n_agents}_AGENT"])

    # Write it to OUT_DATA
    with open(ppj("OUT_DATA", f"grid_{n_agents}_agents.pickle"), "wb") as outfile:
        pickle.dump(OUT_ARRAYS, outfile)
