"""

Check if the super star agents which are used in the oTree experiment with humans
learned a behaviour that is incentive compatible.
"""
import json
import pickle
import sys

import numpy as np

from bld.project_paths import project_paths_join as ppj
from src.analysis.check_ic import check_single_market_agent_ic
from src.analysis.simulate_dev_no_dev import play_with_deviation
from src.analysis.utils_simulate_play import play_without_deviation
from qpricesim.simulations.utils_simulation import gen_possible_prices
from qpricesim.simulations.utils_simulation import (
    gen_price_combination_byte_mappings,
)
from qpricesim.simulations.utils_simulation import (
    int_state_to_price_state,
)


def _is_int(val):
    if type(val) == int:
        return True
    else:
        if val.is_integer():
            return True
        else:
            return False


def _check_if_agents_same(agent_grid, agent_super_s_sim):
    """
    A helper function to check if the agent saved agent
    from the grid search (super star) is the same as the
    first agent from the super star simulation with the
    same random seed.

    Args:
        agent_grid (QLearningAgent): Agent from the grid search which is used in oTree.
        agent_super_s_sim (QLearningAgent): Agent from the super star simulation with the
                                            same random seed as *agent_grid*.
    """
    # Check if the Q-Matrix of both agents is the same.
    assert np.all(
        agent_grid._qvalues == agent_super_s_sim._qvalues
    ), "Agents Q-Matrices are not the same while they should be."

    # Check if the epsilon is the same for both agents.
    assert (
        agent_grid.epsilon == agent_super_s_sim.epsilon
    ), "Agents epsilon is not the same while it should be."


def get_super_star_market_participants(n_agents):
    """
    Load the super star market that the agent learned in
    which is used in the oTree experiment.

    Note: I did not save the entire super star market
    when running the grid search. I only saved one
    market participant from the best run. I can reconstruct
    it however from the super star simulation as I know all
    parameter and then random seed is the same in both
    simulations.


    Args:
        n_agents (integer): Number of agents in the market

    Returns:
        tuple: (index state of convergence, List of QLeaningAgents)
    """

    with open(
        ppj(
            f"IN_SIMULATION_{n_agents}_AGENT",
            f"experiment_super_star_{n_agents}_agent.pickle",
        ),
        "rb",
    ) as f:
        super_star_grid_search = pickle.load(f)

    # Random Seed is the PBS index
    PBS_index = int(super_star_grid_search[-1])

    # Read respective file from the super star simulation.
    # with the PBS_index as the identifier in the file name.
    with open(
        ppj(
            f"IN_SIMULATION_SUPER_STARS_{n_agents}_AGENT",
            f"simulated_arrays_{n_agents}_agents_seed_{PBS_index}.pickle",
        ),
        "rb",
    ) as f:
        entire_super_star_market = pickle.load(f)

    # Check if the first agent from the entire super star market is
    # actually the same as the super star from the grid search simulation.
    # entire_super_star_market[-1] -> All QLearningAgent - > [0] bcs we look at the first
    # in the market.
    # super_star_grid_search[0] -> First element in the grid search super star output
    # is always the agent itself.
    _check_if_agents_same(
        agent_grid=super_star_grid_search[0],
        agent_super_s_sim=entire_super_star_market[-1][0],
    )

    return entire_super_star_market


def check_otree_super_star(super_star_market, parameter_market, parameter_deviation):
    """
    Main function of the module that checks if the first agent in the given
    *super_star_market* learned a behaviour that is considered "incentive
    compatible".

    Args:
        super_star_market (tuple): (index state of convergence, List of QLeaningAgents)
        parameter_market (dict): Explained somewhere else TODO
        parameter_deviation (dict): Dictionary with the parameter for the deviation
                                    simulation.

    Returns:
        dict: Dictionary with the outputs (IC: True/False + Value-functions)
    """

    # Generate the translation dicts.
    prices_to_int_dict, int_to_prices_dict = gen_price_combination_byte_mappings(
        parameter=parameter_market
    )

    # Generate array of possible market prices.
    possible_prices = gen_possible_prices(parameter=parameter_market)

    # Unroll super star market tuple
    state_of_conv, all_agents = super_star_market

    # Transform state of convergence to its market price representation
    price_state_of_conv = int_state_to_price_state(
        int_state=state_of_conv, int_to_prices_dict=int_to_prices_dict
    )

    # Get the market prices with and without deviation...
    prices_dev = play_with_deviation(
        parameter=parameter_deviation,
        all_agents=all_agents,
        prices_to_int_dict=prices_to_int_dict,
        possible_prices=possible_prices,
        initial_price_state=price_state_of_conv,
    )
    prices_no_dev = play_without_deviation(
        parameter=parameter_deviation,
        all_agents=all_agents,
        prices_to_int_dict=prices_to_int_dict,
        possible_prices=possible_prices,
        initial_price_state=price_state_of_conv,
    )
    # ... check for incentive compatibility.
    ic_output = check_single_market_agent_ic(
        market_prices_dev=prices_dev,
        market_prices_no_dev=prices_no_dev,
        parameter_market=parameter_market,
    )

    # Write the results to a dictionary and return it.
    out_dict = {}
    out_dict["IC"] = str(ic_output[0])
    out_dict["V_NO_DEV"] = str(ic_output[1])
    out_dict["V_DEV"] = str(ic_output[2])

    return out_dict


if __name__ == "__main__":
    N_AGENTS = sys.argv[1]

    with open(
        ppj("IN_SIMULATION_PARAMETER", f"parameter_super_star_{N_AGENTS}_agent.json")
    ) as f:
        PARAMETER_MARKET = json.load(f)

    with open(ppj("IN_MODEL_SPECS", "deviation_simulation.json")) as f:
        PARAMETER_DEVIATION = json.load(f)

    super_star_market_in = get_super_star_market_participants(n_agents=N_AGENTS)

    out_dict_otree = check_otree_super_star(
        super_star_market=super_star_market_in,
        parameter_market=PARAMETER_MARKET,
        parameter_deviation=PARAMETER_DEVIATION,
    )
    with open(
        ppj("OUT_ANALYSIS", f"ic_otree_super_star_{N_AGENTS}_agents.json"), "w"
    ) as f:
        json.dump(out_dict_otree, f, indent=4)
