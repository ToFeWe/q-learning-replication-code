"""

A module to perform a cluster analysis of the types/
strategies that participants use in the individual 
choice treatments. I use the Strategy frequency estimation
method.

Some parts of the code use samples from https://github.com/yaroslavrosokha/sfem
"""
import sys

import numpy as np
import pandas as pd
import json
from scipy.optimize import minimize
from .utils_straetgies_clustering import exploit, exploit_at_2, always_cooperate, always_defect
from bld.project_paths import project_paths_join as ppj


def create_data_frame_sfem(data_sfem, strategy_order):
    
    # Create columns for each strategy
    data_sfem['ac'] = data_sfem.apply(lambda x: always_cooperate(x['price'], x['price_algorithm_1'], x['round']), axis=1)
    data_sfem['ad'] = data_sfem.apply(lambda x: always_defect(x['price'], x['price_algorithm_1'], x['round']), axis=1)
    data_sfem['exploit'] = data_sfem.apply(lambda x: exploit(x['price'], x['price_algorithm_1'], x['round']), axis=1)
    data_sfem['exploit_at_2'] = data_sfem.apply(lambda x: exploit_at_2(x['price'], x['price_algorithm_1'], x['round']), axis=1)
    
    # Sum up by participant how often the choice corresponded to the strategy in total
    data_agg_sum = data_sfem.groupby(['participant.code'], as_index=False).sum()

    # Create a matrix
    correct_matrix = data_agg_sum[strategy_order].values
    
    # Create the counterpart how often the choice is not correct conditional on a specfic
    # strategy.
    incorrect_matrix = np.ones(correct_matrix.shape) * data_sfem['round'].max() - correct_matrix
    return correct_matrix, incorrect_matrix


def objective(x, args):
    """
    Objective function that is being minimized
    -> Not that we minimize the negative of the
    likelihood function and hence maximize it.

    Args:
        x (array): Starting values for the parameter
                   x[0]: Sigma
                   x[1] - x[-1]: Frequencies as in the ALL_STRATEGIES list
        args (tuple): correct_matrix, incorrect_matrix

    Returns:
        float: Negative of the likelihood function
    """
    C = args[0] #  I in the paper
    E = args[1] # 1 - I in the paper 
    
    bc=np.power(x[0],C) #beta to the power of C
    be=np.power(1-x[0],E) #beta to the power of E
    prodBce = np.multiply(bc,be) #Hadamard product
    
    #maximum is taken so that there is no log(0) warning/error
    res = np.log(np.maximum(np.dot(prodBce, x[1:]),np.nextafter(0,1))).sum() 
    
    return -res

def constraint1(x):
    """ Some constraint to ensure that the probabilities sum to one. """    
    return x[1:].sum()-1


def single_estimation(n_tries, n_strats):
        #Some random starting point
        x0 = np.zeros(n_strats+1)
        x0[0] = .5+.5*np.random.random()
        temp = np.random.random(n_strats)
        x0[1:]=temp/temp.sum()
        
        # create bootstrap sample by drawing integers with replacement
        index_sample = np.random.randint(0, n_participants, n_participants)
        correct_boot = correct_matrix[index_sample, :]
        incorrect_boot = incorrect_matrix[index_sample, :]

        bestX=x0
        bestObjective=objective(x0,[correct_boot, incorrect_boot])

        #Do many times so that there is low chance of getting stuck in local optimum
        for _ in range(n_tries):
            # Draw new starting values each iteration
            x0 = np.zeros(n_strats+1)
            x0[0] = .5+.5*np.random.random()
            temp = np.random.random(n_strats)
            x0[1:]=temp/temp.sum()

            #Notice that we are minimizing the negative
            solution = minimize(objective,x0,method='SLSQP',bounds=bnds,constraints=cons,args=([correct_boot, incorrect_boot]))
            x = solution.x
            obj = solution.fun

            if bestObjective>obj:
                bestObjective=obj
                bestX=x

def estimation(data_for_sfem, strategies, n_bootstrap, n_tries):

    # Reshape data for the estimation procedure
    correct_matrix, incorrect_matrix = create_data_frame_sfem(data_sfem=data_for_sfem,
                                                              strategy_order=strategies)
    n_strats = len(strategies)
    # Create array to save bootstrap output
    # n_strategies + 1 as we also estimate sigma in each iteration
    estimates_bootstrap = np.zeros((n_bootstrap, n_strats + 1))
    n_participants = correct_matrix.shape[0]

    #Set up the boundaries and constraints
    b0 = (np.nextafter(0.5,1),1-np.nextafter(0,1))
    b1 = (np.nextafter(0,1),1-np.nextafter(0,1))
    bnds = tuple([b0]+[b1]*n_strats) #Beta is at least .5
    con1 = {'type': 'eq', 'fun': constraint1} 
    cons = ([con1])


    # Get the standard errors by bootstrapping
    for b in range(n_bootstrap):
        #Some random starting point
        x0 = np.zeros(n_strats+1)
        x0[0] = .5+.5*np.random.random()
        temp = np.random.random(n_strats)
        x0[1:]=temp/temp.sum()
        
        # create bootstrap sample by drawing integers with replacement
        index_sample = np.random.randint(0, n_participants, n_participants)
        correct_boot = correct_matrix[index_sample, :]
        incorrect_boot = incorrect_matrix[index_sample, :]

        bestX=x0
        bestObjective=objective(x0,[correct_boot, incorrect_boot])

        #Do many times so that there is low chance of getting stuck in local optimum
        for _ in range(n_tries):
            # Draw new starting values each iteration
            x0 = np.zeros(n_strats+1)
            x0[0] = .5+.5*np.random.random()
            temp = np.random.random(n_strats)
            x0[1:]=temp/temp.sum()

            #Notice that we are minimizing the negative
            solution = minimize(objective,x0,method='SLSQP',bounds=bnds,constraints=cons,args=([correct_boot, incorrect_boot]))
            x = solution.x
            obj = solution.fun

            if bestObjective>obj:
                bestObjective=obj
                bestX=x
        estimates_bootstrap[b,:] = x

if __name__ == '__main__':
    # Set random seed
    np.random.seed(9)


    TREATMENT =  sys.argv[1]
    # We focus on the behaviour in the last super game when participants
    # had the chance to learn.
    LAST_SUPER_GAME = 3

    # Bootstrap iterations to calculate standard errors.
    BOOTSTRAP_ITERATIONS = 1000

    # Number of times we try different starting values to avoid that
    # we get stuck in a local minimum.
    TRIES_LOCAL = 50

    # Strategies to consider
    ALL_STRATEGIES = ['exploit', 'ac', 'ad', 'exploit_at_2']

    data_individual_level = pd.read_pickle(ppj("OUT_DATA", "data_individual_level.pickle"))
    data_for_clustering = data_individual_level.loc[(data_individual_level['treatment'] == TREATMENT) &
                                                    (data_individual_level['super_game'] == LAST_SUPER_GAME)]
    # Only a subset of the variables is required                                              
    data_for_sfem = data_for_clustering[['participant.code', 'round', 'price', 'price_algorithm_1']].copy()    
    bic_dict, data_with_types = estimate_multiple_mixture_models(data = data_for_clustering,
                                                                 max_clusters = MAX_CLUSTERS)

    with open(
        ppj("OUT_ANALYSIS", f"bic_data_type_clustering_{TREATMENT}.json"), "w"
    ) as f:
        json.dump(bic_dict, f, indent=4)
    
    data_with_types.to_pickle(ppj("OUT_ANALYSIS", f"data_individual_with_types_{TREATMENT}.pickle"))
    data_with_types.to_csv(ppj("OUT_ANALYSIS", f"data_individual_with_types_{TREATMENT}.csv"))
