"""

Calculate the p-values and other results used for the fully algorithmic market comparisons.
"""

import json
import pickle

import numpy as np
from scipy.stats import mannwhitneyu
from bld.project_paths import project_paths_join as ppj


def share_mean_above_threshold(value_array, threshold):
    """
    Calculates the share of cells within a simulation array (*value_array*)
    that are on average above the *threshold*.
    Note that it assumes that *value_array* is three dimensional, where the
    first dimension refers to the number of simulation iterations and the later
    to the grid points over alpha and beta.

    Args:
        value_array (array): Array to consider
        threshold (float): Threshold to consider

    Returns:
        float: Share of cells in which the average over the first dimension
               is larger than the threshold.
    """
    share = np.where(value_array.mean(axis=0) > threshold, 1, 0).mean()
    return share


def calc_all_results(price_array_3_agents, price_array_2_agents):
    """
    Calculate and derive the results used in Section 6.1 of the paper.

    Args:
        price_array_3_agents (array): Price array for three firm markets
        price_array_2_agents (array): Price array for two firm markets

    Returns:
        Dict: Dict with all result values
    """
    THRESHOLD_NE = 1
    THRESHOLD_COLLUSIVE = 3

    all_results = {}
    all_results['prices_above_stage_game'] = {}
    all_results['prices_above_stage_game']['0H2A'] = share_mean_above_threshold(
        value_array=price_array_2_agents, threshold=THRESHOLD_NE)
    all_results['prices_above_stage_game']['0H3A'] = share_mean_above_threshold(
        value_array=price_array_3_agents, threshold=THRESHOLD_NE)
    all_results['above_three_0H2A'] = share_mean_above_threshold(
        value_array=price_array_2_agents, threshold=THRESHOLD_COLLUSIVE)
    all_results['max_average_price_0H3A'] = array_avg_price_3_agents.mean(
        axis=0).max()
    all_results['max_grid_p_value_0H2A_v_0H3A'] = mannwhitneyu(
        price_array_3_agents,
        price_array_2_agents,
        axis=0,
        alternative='two-sided',
        use_continuity=False)[1].max()

    return all_results


if __name__ == '__main__':
    # Load all grids
    with open(ppj("OUT_DATA", "grid_3_agents.pickle"), "rb") as f:
        all_grids_3_agents = pickle.load(f)
    with open(ppj("OUT_DATA", "grid_2_agents.pickle"), "rb") as f:
        all_grids_2_agents = pickle.load(f)

    # Get the avg price array for both
    array_avg_price_3_agents = np.array(all_grids_3_agents['avg_price'])
    array_avg_price_2_agents = np.array(all_grids_2_agents['avg_price'])

    # Calculate results and save to json
    all_results_fully_algo = calc_all_results(
        price_array_3_agents=array_avg_price_3_agents,
        price_array_2_agents=array_avg_price_2_agents)
    with open(
        ppj("OUT_ANALYSIS", "all_results_fully_algo.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(all_results_fully_algo, f, indent=4)
