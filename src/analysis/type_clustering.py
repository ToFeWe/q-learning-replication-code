"""

A module to perform a cluster analysis of the types/
strategies that participants use in the individual 
choice treatments.
"""
import sys

import numpy as np
import pandas as pd
import json
from sklearn.mixture import GaussianMixture

from bld.project_paths import project_paths_join as ppj


def estimate_multiple_mixture_models(data, max_clusters):
    

    # Dictionary to save all BICs for each model
    all_bics = dict()
    
    # Lowest bic initialized to np.inf
    lowest_bic = np.inf
    data_with_type_lowest_bic = None

    for n_clusters in range(1,max_clusters+1):
        current_bic, current_data_with_type = estimate_single_mixture_model(
                                                data=data,
                                                n_clusters=n_clusters
                                              )
        all_bics[str(n_clusters)] = current_bic

        if current_bic < lowest_bic:
            lowest_bic = current_bic
            data_with_type_lowest_bic = current_data_with_type
    
    return all_bics, data_with_type_lowest_bic



def estimate_single_mixture_model(data, n_clusters):

    # Subset to relevant columns
    data_subset = data[['participant.code', 'round', 'price']]

    # Reshape to wide format such that each column represents a price in one specific round
    data_subset_pivot = data_subset.pivot(index='participant.code', columns='round', values='price')
    data_subset_pivot.reset_index(level=0, inplace=True)
    
    # Create a list with the variable names (round numbers)
    var_list = list(data_subset_pivot)
    var_list.remove('participant.code')

    # Create a matrix from the DataFrame that contains only the prices by round for each subject
    X_matrix = data_subset_pivot[list(range(1, 12))]
    model = GaussianMixture(n_components=n_clusters, random_state=0,
                            covariance_type='full', init_params='kmeans',
                            n_init=50, max_iter=1000, tol=1e-7).fit(X_matrix)
    
    # Save the value of the Bayesian information criterion
    bic_model = model.bic(X_matrix)

    # In sample prediction to get the type classification
    data_subset_pivot['strategy_type'] = model.predict(X_matrix)

    # Merge the strategy type to the original data 
    data_type_classification = data_subset_pivot[['participant.code', 'strategy_type']]
    data_out = data.merge(data_type_classification, how='left', on='participant.code')

    return bic_model, data_out

if __name__ == '__main__':
    TREATMENT =  sys.argv[1]
    # We focus on the behaviour in the last super game when participants
    # had the chance to learn.
    LAST_SUPER_GAME = 3

    # Maximal number of cluster we will consider for the analysis
    MAX_CLUSTERS = 10

    data_individual_level = pd.read_pickle(ppj("OUT_DATA", "data_individual_level.pickle"))
    data_for_clustering = data_individual_level.loc[(data_individual_level['treatment'] == TREATMENT) &
                                                    (data_individual_level['super_game'] == LAST_SUPER_GAME)]
    
    bic_dict, data_with_types = estimate_multiple_mixture_models(data = data_for_clustering,
                                                                 max_clusters = MAX_CLUSTERS)

    with open(
        ppj("OUT_ANALYSIS", f"bic_data_type_clustering_{TREATMENT}.json"), "w"
    ) as f:
        json.dump(bic_dict, f, indent=4)
    
    data_with_types.to_pickle(ppj("OUT_ANALYSIS", f"data_individual_with_types_{TREATMENT}.pickle"))
    data_with_types.to_csv(ppj("OUT_ANALYSIS", f"data_individual_with_types_{TREATMENT}.csv"))
