"""

In this module we analysis the different clusters in
that we have estimated in the module *type_clustering.py*.
"""

import pandas as pd
import json

from scipy.stats import mannwhitneyu

from bld.project_paths import project_paths_join as ppj


def test_differences_clusters_v_humans(data_humans, data_clusters):
    """
    A function to calculate the p-values based on Mann-Whitney-U
    tests comparing the market prices in the cluster (not) type 0 with
    the fully human markets.

    Args:
        data_humans (DataFrame): Human data for the respective treatment
                                 (supply subset only and only last SG).
        data_clusters (DataFrame): Data for the individual choice treatment
                                   with clusters.

    Returns:
        dict: P-values rounded to fourth decimal
    """
    # Aggregate human data by the general super group is to get independent
    # observations.
    data_humans_agg = data_humans.groupby(['super_group_id_general'])[
        'winning_price'].mean().values

    # Split the data based on the type 0 (cooperative type when looking into
    # data)
    data_not_type_0, data_type_0 = [
        x for _, x in data_clusters.groupby(
            data_clusters['strategy_type'] == 0)]
    # Get the independent observations for each of the cluster-subgroups
    # As the underlying treatment is individual choice, I can groupby by
    # participant.code
    data_type_0_agg = data_type_0.groupby(['participant.code'])[
        'winning_price'].mean().values
    data_not_type_0_agg = data_not_type_0.groupby(
        ['participant.code'])['winning_price'].mean().values
    
    print(data_not_type_0_agg)

    # Create an output dictionary
    p_values_out = dict()

    # First type 0 v humans
    p_value_type_0_v_human = mannwhitneyu(
        data_type_0_agg,
        data_humans_agg,
        use_continuity=False,
        alternative='two-sided'
    )[-1]
    p_values_out['type_0_v_human'] = round(p_value_type_0_v_human, 4)

    # Second ppl who are not type one v humans
    p_value_not_type_0_v_human = mannwhitneyu(
        data_not_type_0_agg,
        data_humans_agg,
        use_continuity=False,
        alternative='two-sided'
    )[-1]
    p_values_out['not_type_0_v_human'] = round(p_value_not_type_0_v_human, 4)

    return p_values_out


def get_cluster_shares(data_cluster_1H1A, data_cluster_1H2A):
    """
    A function to calculate the shares of each cluster within the data.

    Args:
        data_cluster_1H1A (DataFrame): Individual level data from 1H1A treatment with clusters
        data_cluster_1H2A (DataFrame): Individual level data from 1H2A treatment with clusters

    Returns:
        dict: Dict with shares for each cluster by treatment
    """
    # Get the cluster shares for 1H1A
    cluster_absolute_N_1H1A = data_cluster_1H1A.groupby(
        ['strategy_type'], as_index=True)[['participant.code']].nunique()
    cluster_share_1H1A = cluster_absolute_N_1H1A / \
        len(set(data_cluster_1H1A['participant.code']))

    # Get the cluster shares for 1H2A
    cluster_absolute_N_1H2A = data_cluster_1H2A.groupby(
        ['strategy_type'], as_index=True)[['participant.code']].nunique()
    cluster_share_1H2A = cluster_absolute_N_1H2A / \
        len(set(data_cluster_1H2A['participant.code']))

    # Add this information to a dictionary to save it as json (json but eval
    # to have string keys directly)
    cluster_shares = dict()
    cluster_shares['1H1A'] = eval(cluster_share_1H1A.to_json())
    cluster_shares['1H2A'] = eval(cluster_share_1H2A.to_json())

    return cluster_shares


if __name__ == '__main__':
    # Load the datasets for the cluster analysis
    data_cluster_1H1A_in = pd.read_pickle(
        ppj('OUT_ANALYSIS', 'data_individual_with_types_1H1A.pickle'))
    data_cluster_1H2A_in = pd.read_pickle(
        ppj('OUT_ANALYSIS', 'data_individual_with_types_1H2A.pickle'))

    # Load the entire human dataset as we will compare to the clusters
    data_group_level_in = pd.read_pickle(
        ppj('OUT_DATA', 'data_group_level.pickle'))
    # Subset human data to last super game as this is what we are interested in
    data_humans_last_sg = data_group_level_in.loc[
                             data_group_level_in['super_game'] == 3
                          ].copy()

    # Different datasets have to be used conditionally on the treatment
    # that we actually consider.
    CLUSTERED_TREATMENTS = ['1H1A', '1H2A']
    CLUSTERED_DATA = [data_cluster_1H1A_in, data_cluster_1H2A_in]
    HUMAN_TREATMENTS = ['2H0A', '3H0A']

    # calculate the p-values
    all_p_values = dict()
    for c_treatment, c_data, h_treatment in zip(
            CLUSTERED_TREATMENTS, CLUSTERED_DATA, HUMAN_TREATMENTS):

        # Subset the human data to specific treatment
        # Note that we have already created the subset for the last
        # super game before.
        data_human_subset = data_humans_last_sg.loc[
            data_humans_last_sg['treatment'] == h_treatment]

        # Calculate p values and save them to the dict
        current_p_values = test_differences_clusters_v_humans(
            data_humans=data_human_subset,
            data_clusters=c_data)
        all_p_values[f"{c_treatment}_v_{h_treatment}"] = current_p_values

    # Get cluster shares
    cluster_shares_dict = get_cluster_shares(
        data_cluster_1H1A=data_cluster_1H1A_in,
        data_cluster_1H2A=data_cluster_1H2A_in)

    # Dump the data as json
    with open(ppj("OUT_ANALYSIS", f"cluster_shares.json"), "w") as f:
        json.dump(cluster_shares_dict, f, indent=4)

    with open(ppj("OUT_ANALYSIS", f"p_values_cluster_analysis.json"), "w") as f:
        json.dump(all_p_values, f, indent=4)
