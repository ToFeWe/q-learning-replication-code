"""

A module to perform a cluster analysis of the types/
strategies that participants use in the individual
choice treatments. I use the Strategy frequency estimation
method.

Some parts of the code use samples from https://github.com/yaroslavrosokha/sfem
"""
import sys
import json

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from bld.project_paths import project_paths_join as ppj
from src.analysis.utils_strategies_clustering import exploit, exploit_at_2, always_cooperate, always_defect


def create_data_frame_sfem(data_sfem, strategy_order):
    """ Create the DataFrame that will be used for the
    type classification.

    Args:
        data_sfem (DataFrame): Individual level data that is
                               already subset to the correct level.
        strategy_order (list): Name of all strategies

    Returns:
        DataFrame: DataFrame for the type classification

    """
    # Create columns for each strategy
    # Few strategies & observations so there is no shame in using
    # the apply method.
    # Always cooperate
    data_sfem['ac'] = data_sfem.apply(
        lambda x: always_cooperate(
            x['price'],
            x['price_algorithm_1'],
            x['price_lag_1'],
            x['round']),
        axis=1)

    # Always defect
    data_sfem['ad'] = data_sfem.apply(
        lambda x: always_defect(
            x['price'],
            x['price_algorithm_1'],
            x['price_lag_1'],
            x['round']),
        axis=1)

    # Exploit
    data_sfem['exploit'] = data_sfem.apply(
        lambda x: exploit(
            x['price'],
            x['price_algorithm_1'],
            x['price_lag_1'],
            x['round']),
        axis=1)

    # Exploit2
    data_sfem['exploit_at_2'] = data_sfem.apply(
        lambda x: exploit_at_2(
            x['price'],
            x['price_algorithm_1'],
            x['price_lag_1'],
            x['round']),
        axis=1)

    # Sum up by participant how often the choice corresponded to the strategy
    # in total.
    data_agg_sum = data_sfem.groupby(
        ['participant.code'], as_index=False).sum()

    # Create a matrix
    correct_matrix = data_agg_sum[strategy_order].values

    # Create the counterpart how often the choice is not correct conditional on a specific
    # strategy.
    incorrect_matrix = np.ones(correct_matrix.shape) * \
        data_sfem['round'].max() - correct_matrix
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
    C = args[0]  # I in the paper
    E = args[1]  # 1 - I in the paper

    bc = np.power(x[0], C)  # beta to the power of C
    be = np.power(1 - x[0], E)  # beta to the power of E
    prodBce = np.multiply(bc, be)  # Hadamard product

    # maximum is taken so that there is no log(0) warning/error
    res = np.log(np.maximum(np.dot(prodBce, x[1:]), np.nextafter(0, 1))).sum()

    return -res


def constraint1(x):
    """ Some constraint to ensure that the probabilities sum to one. """
    return x[1:].sum() - 1


def create_random_starting_values(n_strats):
    """

    Helper function to create random starting values with the length
    n_strats + 1.
    """

    # Some random starting point
    starting_values = np.zeros(n_strats + 1)
    starting_values[0] = .5 + .5 * np.random.random()
    temp = np.random.random(n_strats)
    starting_values[1:] = temp / temp.sum()

    return starting_values


def single_estimation(
        n_tries,
        n_strats,
        matrix_correct,
        matrix_incorrect,
        bnds,
        cons):
    """ Perform a single estimation with the
    strategy frequency estimation method.

    Args:
        n_tries (integer): Number of different starting values to try
        n_strats (integer): Number of strategies (without sigma)
        matrix_correct (array): Array with the sum of choices that
                                correspond to a given strategy for each
                                individual.
        matrix_incorrect (array): Array with the sum of choices that
                                  do not correspond to a given strategy
                                  for each individual.
        bnds (tuple): Tuple with bounds for each parameter.
        cons (tuple): Constraint that ensure that the probabilities sum
                      to one.

    Returns:
        array: Estimates that yield the largest loglikelihood
    """
    # Some random starting point
    x0 = create_random_starting_values(n_strats=n_strats)

    # Best value is the initial value
    bestX = x0
    bestObjective = objective(x0, [matrix_correct, matrix_incorrect])

    # Do many times so that there is low chance of getting stuck in local
    # optimum
    for _ in range(n_tries):
        # Draw new starting values each iteration
        x0 = create_random_starting_values(n_strats=n_strats)

        # Notice that we are minimizing the negative
        solution = minimize(objective,
                            x0,
                            method='SLSQP',
                            bounds=bnds,
                            constraints=cons,
                            args=([matrix_correct,
                                   matrix_incorrect]))
        x = solution.x
        obj = solution.fun

        if bestObjective > obj:
            bestObjective = obj
            bestX = x

    return bestX


def estimation(data_for_sfem, strategies, n_bootstrap, n_tries):
    """ A function to perform the estimation procedure
    as described in the paper.

    Args:
        data_for_sfem (DataFrame): Individual level data that is
                               already subset to the correct level.
        strategies (list): List of strategy names to consider
        n_bootstrap (integer): Number of bootstrap iterations for the standard errors
        n_tries (integer): Number of times different starting values are tried

    Returns:
        dict: Parameter dict with standard errors
    """

    # Reshape data for the estimation procedure
    correct_matrix, incorrect_matrix = create_data_frame_sfem(
        data_sfem=data_for_sfem, strategy_order=strategies)
    n_strats = len(strategies)
    # Create array to save bootstrap output
    # n_strategies + 1 as we also estimate sigma in each iteration
    estimates_bootstrap = np.zeros((n_bootstrap, n_strats + 1))
    n_participants = correct_matrix.shape[0]

    # Set up the boundaries and constraints
    b0 = (np.nextafter(0.5, 1), 1 - np.nextafter(0, 1))
    b1 = (np.nextafter(0, 1), 1 - np.nextafter(0, 1))
    bnds = tuple([b0] + [b1] * n_strats)  # Beta is at least .5
    con1 = {'type': 'eq', 'fun': constraint1}
    cons = ([con1])

    # Get the standard errors by bootstrapping
    for b in range(n_bootstrap):
        # create bootstrap sample by drawing integers with replacement
        index_sample = np.random.randint(0, n_participants, n_participants)
        correct_boot = correct_matrix[index_sample, :]
        incorrect_boot = incorrect_matrix[index_sample, :]
        est = single_estimation(n_tries=n_tries,
                                n_strats=n_strats,
                                matrix_correct=correct_boot,
                                matrix_incorrect=incorrect_boot,
                                bnds=bnds,
                                cons=cons)
        estimates_bootstrap[b, :] = est

    # Parameter estimation now
    main_parameter = single_estimation(n_tries=n_tries,
                                       n_strats=n_strats,
                                       matrix_correct=correct_matrix,
                                       matrix_incorrect=incorrect_matrix,
                                       bnds=bnds,
                                       cons=cons)
    bootstraped_std = np.std(estimates_bootstrap, axis=0)
    out_dict = {}
    out_dict['name'] = ['sigma'] + strategies
    out_dict['parameter'] = main_parameter.tolist()
    out_dict['standard_errors'] = bootstraped_std.tolist()

    return out_dict


if __name__ == '__main__':
    # Set random seed
    np.random.seed(9)

    TREATMENT = sys.argv[1]
    # We focus on the behaviour in the last super game when participants
    # had the chance to learn.
    LAST_SUPER_GAME = 3

    # Bootstrap iterations to calculate standard errors.
    BOOTSTRAP_ITERATIONS = 2500

    # Number of times we try different starting values to avoid that
    # we get stuck in a local minimum.
    TRIES_LOCAL = 25
    # Strategies to consider
    ALL_STRATEGIES = ['exploit', 'ac', 'ad', 'exploit_at_2']

    data_individual_level = pd.read_pickle(
        ppj("OUT_DATA", "data_individual_level.pickle"))
    data_for_clustering = data_individual_level.loc[(data_individual_level['treatment'] == TREATMENT) & (
        data_individual_level['super_game'] == LAST_SUPER_GAME)]
    # Only a subset of the variables is required
    data_for_sfem_in = data_for_clustering[[
        'participant.code', 'round', 'price', 'price_algorithm_1', 'price_lag_1']].copy()

    paramter_dict = estimation(data_for_sfem=data_for_sfem_in,
                          strategies=ALL_STRATEGIES,
                          n_bootstrap=BOOTSTRAP_ITERATIONS,
                          n_tries=TRIES_LOCAL)

    with open(
        ppj("OUT_ANALYSIS", f"output_type_clustering_{TREATMENT}.json"), "w", encoding='utf8'
    ) as f:
        json.dump(paramter_dict, f, indent=4)
