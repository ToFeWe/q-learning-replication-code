"""

A script to calculate the p-values and averages for Section 6.3 of the paper.
"""
import json
import pickle
import numpy as np
from scipy.stats import mannwhitneyu, ttest_1samp

from bld.project_paths import project_paths_join as ppj


def calc_p_value_by_super_game(
        data_experiment,
        super_star_data,
        grid_data,
        sg,
        treatment):
    """Calcualte the respective p values mentioned in the paper.

    Args:
        data_experiment (DataFrame): DataFrame with the experimental data on group level
        super_star_data (array): Price array from the best performing market
        grid_data (array): Entire price grid array
        sg (integer): Super game indicator
        treatment (string): Treatment indicator

    Returns:
        tuple: p_value_super_star, p_value_grid_avg, avg_grid

               p_value_super_star (float): p-value when comparing the experimental data
                                           to the best performing market with MWU test.
               p_value_grid_avg (float): p-value when comparing the experimental data
                                         to the average of the price grid with t-test.
               avg_grid (float): Average of the price grid.

    """
    # Aggregate the group for a given super game on super group matching group
    # level
    subset_sg = data_experiment.loc[(data_experiment['super_game'] == sg) &
                                    (data_experiment['treatment'] == treatment)
                                    ].groupby(['super_group_id_general', 'treatment'],
                                              as_index=False)[['winning_price']].mean()

    p_value_super_star = mannwhitneyu(
        subset_sg['winning_price'],
        super_star_data,
        use_continuity=False,
        alternative='two-sided'
    )[-1]

    # Compare against average of grid
    avg_grid = grid_data.mean()
    p_value_grid_avg = ttest_1samp(
        subset_sg['winning_price'],
        avg_grid,
        alternative='two-sided'
    )[-1]

    return p_value_super_star, p_value_grid_avg, avg_grid


def create_result_dict(
        data_experiment,
        super_star_data_2,
        super_star_data_3,
        grid_data_2,
        grid_data_3):
    """
    Create a dictionary with all p values from Section 6.3.

    Args:
        data_experiment (DataFrame): DataFrame with the experimental data on group level
        super_star_data_2 (array): Price array from the best performing market (2 firm market)
        super_star_data_3 (array): Price array from the best performing market (3 firm market)
        grid_data_2 (array): Entire price grid array (2 firm market)
        grid_data_3 (array): Entire price grid array (3 firm market)

    Returns:
        dict: Dictionary with all p values
    """

    # Algo v Human
    all_results = {}
    all_results['algo_v_human'] = {}

    combinations = [('2H0A', super_star_data_2, grid_data_2),
                    ('3H0A', super_star_data_3, grid_data_3)]
    supergames = [1, 2, 3]

    for t, d_super_star, d_grid in combinations:
        all_results['algo_v_human'][t] = {}
        for current_sg in supergames:
            all_results['algo_v_human'][t][f'supergame_{current_sg}'] = {}
            p_value_super_star, p_value_grid_avg, avg_grid = calc_p_value_by_super_game(
                data_experiment=data_experiment,
                super_star_data=d_super_star,
                grid_data=d_grid, sg=current_sg,
                treatment=t)
            all_results['algo_v_human'][t][f'supergame_{current_sg}']['p_value_super_star'] = p_value_super_star
            all_results['algo_v_human'][t][f'supergame_{current_sg}']['p_value_grid_avg'] = p_value_grid_avg
            all_results['algo_v_human'][t][f'supergame_{current_sg}']['avg_grid'] = avg_grid

    # Human v Human
    all_results['human_v_human'] = {}

    # By supergame
    for current_sg in supergames:
        data_agg_sg = data_group_level.loc[
            (data_group_level['super_game'] == current_sg)
        ].groupby(['super_group_id_general', 'treatment'], as_index=False)[['winning_price']].mean()
        p_value_humans_sg = mannwhitneyu(
            data_agg_sg.loc[data_agg_sg['treatment'] == '3H0A']['winning_price'],
            data_agg_sg.loc[data_agg_sg['treatment'] == '2H0A']['winning_price'],
            use_continuity=False,
            alternative='two-sided'
        )[-1]
        all_results['human_v_human'][f'supergame_{current_sg}'] = p_value_humans_sg

    # Pooled
    data_agg_pooled = data_group_level.groupby(
        ['super_group_id_general', 'treatment'], as_index=False)[['winning_price']].mean()
    p_value_humans_pooled = mannwhitneyu(
        data_agg_pooled.loc[data_agg_pooled['treatment'] == '3H0A']['winning_price'],
        data_agg_pooled.loc[data_agg_pooled['treatment'] == '2H0A']['winning_price'],
        use_continuity=False,
        alternative='two-sided'
    )[-1]
    all_results['human_v_human']['pooled'] = p_value_humans_pooled

    return all_results


if __name__ == '__main__':

    # Load the simulation data
    # Two firm algorithm markets
    with open(ppj("OUT_DATA", "grid_2_agents.pickle"), "rb") as f:
        all_output_grids_2_agents = pickle.load(f)
    all_prices_2_agents_grid = np.array(all_output_grids_2_agents['avg_price'])
    with open(ppj("OUT_DATA", "super_star_avg_prices_2_agents.pickle"), "rb") as f:
        super_star_avg_prices_2_agents = pickle.load(f)

    # Three firm algorithm markets
    with open(ppj("OUT_DATA", "grid_3_agents.pickle"), "rb") as f:
        all_output_grids_3_agents = pickle.load(f)
    all_prices_3_agents_grid = np.array(all_output_grids_3_agents['avg_price'])
    with open(ppj("OUT_DATA", "super_star_avg_prices_3_agents.pickle"), "rb") as f:
        super_star_avg_prices_3_agents = pickle.load(f)

    # Load the group level data from the experiments
    with open(ppj("OUT_DATA", "data_group_level.pickle"), "rb") as f:
        data_group_level = pickle.load(f)

    # Calc all results
    result_dict = create_result_dict(
        data_experiment=data_group_level,
        super_star_data_2=super_star_avg_prices_2_agents,
        super_star_data_3=super_star_avg_prices_3_agents,
        grid_data_2=all_prices_2_agents_grid,
        grid_data_3=all_prices_3_agents_grid)
    # Write to JSON
    with open(
        ppj("OUT_ANALYSIS", "all_results_comparing_algos_and_humans.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(result_dict, f, indent=4)
