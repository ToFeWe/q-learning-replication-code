"""

A module to calculate results for the section
in which in compare mixed markets.
"""

import json
import pickle

from scipy.stats import mannwhitneyu

from bld.project_paths import project_paths_join as ppj


def calculate_p_values(
        super_group_level_data,
        algo_prices_2_firms,
        algo_prices_3_firms):
    """ A function to calcualte the p-values for the section
    that compares mixed markets.

    Args:
        super_group_level_data (DataFrame): DataFrame with the mean market
                                            price pooled over all supergames
                                            and aggregate by matching group
        algo_prices_2_firms (array): Average market prices in the markets
                                     from the selected algorithm (0H2A)
        algo_prices_3_firms (array): Average market prices in the markets
                                     from the selected algorithm (0H3A)

    Returns:
        dict: Dict with p-values
    """

    # Create dict to save the p-values
    results_dict = dict()

    # Calculate all p-values based on MWU two sided tests
    results_dict['2H0A_v_1H1A'] = mannwhitneyu(
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '2H0A'
        ]['winning_price'],
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '1H1A'
        ]['winning_price'],
        use_continuity=False,
        alternative='two-sided'
    )[-1]

    results_dict['0H2A_v_1H1A'] = mannwhitneyu(algo_prices_2_firms,
                                               super_group_level_data.loc
                                                  [super_group_level_data['treatment'] == '1H1A'
                                               ]['winning_price'],
                                               use_continuity=False, alternative='two-sided')[-1]

    results_dict['3H0A_v_2H1A'] = mannwhitneyu(
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '3H0A'
        ]['winning_price'],
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '2H1A'
        ]['winning_price'],
        use_continuity=False,
        alternative='two-sided'
    )[-1]
    
    results_dict['2H1A_v_1H2A'] = mannwhitneyu(
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '2H1A'
        ]['winning_price'],
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '1H2A'
        ]['winning_price'],
        use_continuity=False,
        alternative='two-sided'

    )[-1]

    results_dict['3H0A_v_1H2A'] = mannwhitneyu(
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '3H0A'
        ]['winning_price'],
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '1H2A'
        ]['winning_price'],
        use_continuity=False,
        alternative='two-sided'
    )[-1]

    results_dict['0H3A_v_1H2A'] = mannwhitneyu(
        algo_prices_3_firms,
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '1H2A'
        ]['winning_price'],
        use_continuity=False,
        alternative='two-sided'
    )[-1]
    results_dict['0H3A_v_3H0A'] = mannwhitneyu(
        algo_prices_3_firms,
        super_group_level_data.loc[
            super_group_level_data['treatment'] == '3H0A'
        ]['winning_price'],
        use_continuity=False,
        alternative='two-sided'
    )[-1]

    return results_dict

def calc_share_weird_states(data_individual_mixed, data_group_mixed):
    """ In some states the strategy of the algorithm does not
    perfectly align with the win-stay lose-shift strategy described
    in the paper. I calculate the share of those states here
    (there are very very few).

    Args:
        data_individual_mixed (DataFrame): Individual level data from the experiment
        data_group_mixed (DataFrame): Group level data from the experiments

    Returns:
        float: Share of weird states from all rounds in the experiments
    """
    
    # Round in which the algorithm did NOT play the price of 1 or 4
    # This happens rarely bcs the strategy in three-firm markets is not
    # perfect WSLS.
    data_algos_group = data_group_mixed.loc[~data_group_mixed['treatment'].isin(['2H0A', '3H0A'])].copy()
    n_price_not_1_or_4 = len(data_algos_group.loc[~data_algos_group['price_algorithm'].isin([1,4])]) 


    #  Similarly if the algo plays a price of 4 after an upwards deviation
    data_algos_individual = data_individual_mixed.loc[
                               ~data_individual_mixed['treatment'].isin(['2H0A', '3H0A'])
                            ].copy()

    # Note that those are in 1H1A and thus individual = Group from an otree-data perspective
    n_price_4_but_different_state = len(data_algos_individual.loc[
                                        (data_algos_individual['price_algorithm'] == 4) &
                                        (~data_algos_individual['price_lag_1'].isin([1,4])) & 
                                        (data_algos_individual['round']>1)
                                    ])
    share_weird_states = (n_price_not_1_or_4 + n_price_4_but_different_state) / len(data_algos_group)
    return share_weird_states
                

if __name__ == '__main__':

    # Load data from algorithmic market
    with open(ppj("OUT_DATA", "super_star_avg_prices_2_agents.pickle"), "rb") as f:
        super_star_avg_prices_2_agents = pickle.load(f)
    with open(ppj("OUT_DATA", "super_star_avg_prices_3_agents.pickle"), "rb") as f:
        super_star_avg_prices_3_agents = pickle.load(f)

    # Load data from experiments
    with open(ppj("OUT_DATA", "data_individual_level.pickle"), "rb") as f:
        data_individual_level = pickle.load(f)

    with open(ppj("OUT_DATA", "data_group_level.pickle"), "rb") as f:
        data_group_level = pickle.load(f)

    # Create a DataFrame that aggregate the winning price on supergroup level
    data_mixed_pooled = data_group_level.groupby(
                            ['super_group_id_general', 'treatment'],
                            as_index=False)[
                                ['winning_price']
                        ].mean()

    # Get the p-values
    dict_out = calculate_p_values(super_group_level_data=data_mixed_pooled,
                                  algo_prices_2_firms=super_star_avg_prices_2_agents,
                                  algo_prices_3_firms=super_star_avg_prices_3_agents)

    dict_out['share_weird_states'] = calc_share_weird_states(data_individual_mixed=data_individual_level,
                                                             data_group_mixed=data_group_level)

    with open(
        ppj("OUT_ANALYSIS", f"results_mixed_markets.json"), "w", encoding='utf8'
    ) as f:
        json.dump(dict_out, f, indent=4)
