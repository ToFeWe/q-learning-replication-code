"""

A module which simulates the market prices played by the
agents starting from the states of convergence with and
without a deviation.
"""
import json
import pickle
import sys

import numpy as np

from bld.project_paths import project_paths as pp
from bld.project_paths import project_paths_join as ppj
from src.analysis.utils_simulate_play import play_n_periods
from src.analysis.utils_simulate_play import play_period
from src.analysis.utils_simulate_play import play_without_deviation
from qpricesim.simulations.utils_simulation import (
    concatenate_new_price_state,
)
from qpricesim.simulations.utils_simulation import gen_possible_prices
from qpricesim.simulations.utils_simulation import (
    gen_price_combination_byte_mappings,
)
from qpricesim.simulations.utils_simulation import (
    int_state_to_price_state,
)
from qpricesim.simulations.utils_simulation import (
    price_state_to_int_state,
)



def play_with_deviation(
    parameter, all_agents, prices_to_int_dict, possible_prices, initial_price_state
):
    """
    Starting from the state of convergence the agents play in the market
    for a certain amount of periods. Then, an exogenous deviation is induced
    in the sense that the first agent in the list *all_agents* deviates by
    playing a price one step (one integer) below the price he would have played.
    Then, from this new deviation price state, the agents continue playing
    using the learned limit strategies.

    Args:
        parameter (dict): Parameter for the deviation simulation
        all_agents (list): List of QLearningAgents
        prices_to_int_dict (dict): Mapping dict from price to index states
        possible_prices (array): Array of possible prices
        initial_price_state (array): Price state in which the simulation starts.

    Returns:
        array: Array with all simulated prices states. First state is the
               state of convergence.
               Note that the array is of shape
               (parameter["total_periods"], n_agents).
    """
    #  Periods before deviation + 1 deviation period + state of convergence
    periods_after_deviation = (
        parameter["total_periods"] - parameter["periods_before_deviation"] - 1 - 1
    )

    # Play rounds after the initial price state and before the deviation
    price_seq_inital = play_n_periods(
        n_periods=parameter["periods_before_deviation"],
        all_agents=all_agents,
        prices_to_int_dict=prices_to_int_dict,
        possible_prices=possible_prices,
        start_price_state=initial_price_state,
    )
    # Induce one period deviation
    # If the last price was already the lowest price possible
    # there is no possible deviation.

    # Price state that would have been played in the deviation
    # period if there would be no induced deviation
    price_state_before_deviation = price_seq_inital[-1, :]
    int_state_before_deviation = price_state_to_int_state(
        price_state=price_state_before_deviation, prices_to_int_dict=prices_to_int_dict
    )

    hypothetical_prices = play_period(
        all_agents=all_agents,
        possible_prices=possible_prices,
        int_state=int_state_before_deviation,
    )

    # Take the prices that would have been played and induce a deviation.
    # Note that the agent can only deviate if a smaller prices exists.
    n_agents = len(all_agents)
    if hypothetical_prices[0] == possible_prices.min():
        deviation_price_state = hypothetical_prices
    else:
        deviation_price_state = hypothetical_prices - np.array(
            [1] + [0] * (n_agents - 1)
        )

    # Continue to play for the remaining periods
    price_seq_after = play_n_periods(
        n_periods=periods_after_deviation,
        all_agents=all_agents,
        prices_to_int_dict=prices_to_int_dict,
        possible_prices=possible_prices,
        start_price_state=deviation_price_state,
    )
    out_array = np.vstack(
        (initial_price_state, price_seq_inital, deviation_price_state, price_seq_after)
    )
    return out_array


def sim_dev_no_dev(parameter_market, parameter_deviation, all_super_star_tuple):
    """
    Run the entire simulation for all markets with and without deviation.

    Args:
        parameter_market (dict): Parameter as explained somewhere else TODO
        parameter_deviation (dict): Parameter for the deviation simulation
        all_super_star_tuple (list): List of tuples, where each tuple is one
                                     market upon convergence.
                                     (state of convergence,
                                     List with QLearningAgents)

    Returns:
        tuple: Two arrays with the outputs from the simulations over
               all markets with and without deviation from the state of
               convergence (array_no_deviation_simulations,
               array_deviation_simulations).

               The shape is (number of market, number of periods, number of agents).

    """
    total_periods = parameter_deviation["total_periods"]
    n_agents = parameter_market["n_agent"]

    # Generate the translation dicts
    prices_to_int_dict, int_to_prices_dict = gen_price_combination_byte_mappings(
        parameter=parameter_market
    )
    possible_prices = gen_possible_prices(parameter=parameter_market)

    n_super_star_simulations = len(all_super_star_tuple)

    # Initialize the output arrays
    array_deviation_simulations = np.empty(
        (n_super_star_simulations, total_periods, n_agents), dtype=int
    )
    array_no_deviation_simulations = np.empty(
        (n_super_star_simulations, total_periods, n_agents), dtype=int
    )

    # Loop over all markets and simulate the prices with and without
    # deviation as specified in the settings.
    for ix_tuple, super_star_tuple in enumerate(all_super_star_tuple):
        state_of_conv, all_agents = super_star_tuple
        price_state_of_conv = int_state_to_price_state(
            int_state=state_of_conv, int_to_prices_dict=int_to_prices_dict
        )

        price_seq_deviation = play_with_deviation(
            parameter=parameter_deviation,
            all_agents=all_agents,
            prices_to_int_dict=prices_to_int_dict,
            possible_prices=possible_prices,
            initial_price_state=price_state_of_conv,
        )
        price_seq_no_deviation = play_without_deviation(
            parameter=parameter_deviation,
            all_agents=all_agents,
            prices_to_int_dict=prices_to_int_dict,
            possible_prices=possible_prices,
            initial_price_state=price_state_of_conv,
        )

        array_deviation_simulations[ix_tuple, :, :] = price_seq_deviation
        array_no_deviation_simulations[ix_tuple, :, :] = price_seq_no_deviation
    return array_no_deviation_simulations, array_deviation_simulations


def run_and_save_simulation(
    n_agents, parameter_market, parameter_deviation, super_star_tuples
):
    """
    Load the needed data, run the simulation and save the simulation
    data.

    Args:
        n_agents (integer): Number of agents in the markets.
        parameter_market (dict): Explained somewhere else TODO
        parameter_deviation (dict): Dictionary with the deviation simulation
                                    parameter.
        super_star_tuples (list): List of tuples, where each tuple is one
                                  market upon convergence.
                                  (state of convergence,
                                  List with QLearningAgents)
    """
    (array_no_deviation_simulations, array_deviation_simulations) = sim_dev_no_dev(
        parameter_market=parameter_market,
        parameter_deviation=parameter_deviation,
        all_super_star_tuple=super_star_tuples,
    )

    with open(
        ppj("OUT_ANALYSIS", f"array_no_deviation_simulations_{n_agents}_agents.pickle"),
        "wb",
    ) as f:
        pickle.dump(array_no_deviation_simulations, f)

    with open(
        ppj("OUT_ANALYSIS", f"array_deviation_simulations_{n_agents}_agents.pickle"),
        "wb",
    ) as f:
        pickle.dump(array_deviation_simulations, f)


if __name__ == "__main__":
    N_AGENTS = sys.argv[1]

    with open(
        ppj("IN_SIMULATION_PARAMETER", f"parameter_{N_AGENTS}_agent_base.json")
    ) as f:
        PARAMETER_MARKET = json.load(f)
    with open(ppj("IN_MODEL_SPECS", "deviation_simulation.json")) as f:
        PARAMETER_DEVIATION = json.load(f)

    with open(ppj("OUT_DATA", f"all_super_stars_{N_AGENTS}_agents.pickle"), "rb") as f:
        SUPER_STAR_TUPLES = pickle.load(f)

    run_and_save_simulation(
        n_agents=N_AGENTS,
        parameter_market=PARAMETER_MARKET,
        parameter_deviation=PARAMETER_DEVIATION,
        super_star_tuples=SUPER_STAR_TUPLES,
    )
