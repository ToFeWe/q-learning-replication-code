"""

A module to create subsets of the simulation data, which
will be used in the comparisons to the experimental data.
"""

import sys
import numpy as np
import json
import pickle
from bld.project_paths import project_paths_join as ppj



def recreate_grids(grid_info):
    """
    A function to create the simulation grid to retrieve the relevant indices 
    that ended up being the super star agents.


    Args:
        grid_info (dict): Information over the used grid

    Returns:
        tuple: beta_grid, alpha_grid
    """
    # Recreate the grid to retrieve the avg prices upon convergence which are of interest to us
    alpha_grid = list(
        np.linspace(
            grid_info['alpha_min'],
            grid_info['alpha_max'],
            grid_info['grid_points'],
        )
    )
    beta_grid = list(
        np.linspace(
            grid_info['beta_min'],
            grid_info['beta_max'],
            grid_info['grid_points'],
        )
    )

    return beta_grid, alpha_grid

def get_indices(parameter_super_star, beta_grid, alpha_grid):
    """
    
    Retrieve the indices of alpha and beta in the respective grids
    for the super star agents.

    Args:
        parameter_super_star (dict): Super star dict with infos about learning rate and decay
        beta_grid (array): Array with all betas used as in the simulation study
        alpha_grid (array): Array with all alphas used as in the simulation study

    Returns:
        tuple: beta_index, alpha_index
    """
    beta_index = beta_grid.index(parameter_super_star['beta_decay'])
    alpha_index = alpha_grid.index(parameter_super_star['learning_rate'])
    return beta_index, alpha_index

def create_and_save_subsets(n_agents):
    """
    
    For each simulation we want to retrieve the data which we use when we
    test for differences compared to the experimental outcomes.

    This will be the prices upon convergence in the super star markets and
    the averages prices across the entire grid of alphas and betas. 

    Args:
        n_agents (int): Number of firms in the market
    """

    with open(ppj("OUT_DATA", f"grid_{n_agents}_agents.pickle"), "rb") as f:
        all_output_grids = pickle.load(f)

    with open(ppj("IN_SIMULATION_PARAMETER", f"parameter_super_star_{n_agents}_agent.json"), "r") as f:
        PARAMETER_SUPER_STAR = json.load(f)

    with open(ppj("IN_SIMULATION_PARAMETER", f"parameter_{n_agents}_agent_cases.json"), "r") as f:
        GRID_INFO = json.load(f)

    beta_grid_recreated, alpha_grid_recreated = recreate_grids(grid_info=GRID_INFO)
    BETA_INDEX, ALPHA_INDEX = get_indices(parameter_super_star = PARAMETER_SUPER_STAR,
                                          beta_grid = beta_grid_recreated,
                                          alpha_grid = alpha_grid_recreated)
    avg_price_grid = np.array(all_output_grids['avg_price'])

    # First position is the observation, second the alpha, third the beta 
    # as it has been implemented in the simulation study
    super_star_avg_prices = avg_price_grid[:, ALPHA_INDEX, BETA_INDEX]

    # Dimension 1 and 2 are alpha and beta, dimension zero is the Monte Carlo 
    # repetition.
    entire_price_grid_avg_prices = np.mean(avg_price_grid, axis=(1,2))
    
    with open(ppj("OUT_DATA", f"super_star_avg_prices_{n_agents}_agents.pickle"), "wb") as outfile:
        pickle.dump(super_star_avg_prices, outfile)

    with open(ppj("OUT_DATA", f"entire_price_grid_avg_prices_{n_agents}_agents.pickle"), "wb") as outfile:
        pickle.dump(entire_price_grid_avg_prices, outfile)

if __name__ == '__main__':
    N_AGENTS = sys.argv[1]

    create_and_save_subsets(n_agents=N_AGENTS)