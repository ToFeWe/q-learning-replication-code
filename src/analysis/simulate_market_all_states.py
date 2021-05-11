"""

A module to simulate all super star markets starting from all possible
initial states.
"""
import json
import pickle
import sys

import numpy as np

from bld.project_paths import project_paths as pp
from bld.project_paths import project_paths_join as ppj
from src.analysis.utils_simulate_play import play_without_deviation
from qpricesim.simulations.utils_simulation import gen_possible_prices
from qpricesim.simulations.utils_simulation import (
    gen_price_combination_byte_mappings,
)
from qpricesim.simulations.utils_simulation import (
    int_state_to_price_state,
)



def play_from_all_states(
    super_star_markets, n_agents, parameter_deviation, parameter_market
):
    """

    For each market in the list *super_star_markets* simulate
    the market play starting from all possible states. We do
    this to test how sensitive the agents are to the initial
    state.

    Args:
        super_star_markets (list): List of all simulated super star markets with all agents.
        n_agents (integer): Number of agents in the market.
        parameter_deviation (dict): Parameter for the deviation simulation. Note that we use it
                                    here to get the number of periods we should simulate.
        parameter_market (dict): Explained somewhere else TODO

    Returns:
        array: Array with all play simulations
               Shape: (n_markets, n_states, n_periods, n_agents)
    """

    possible_prices = gen_possible_prices(parameter=parameter_market)
    prices_to_int_dict, int_to_prices_dict = gen_price_combination_byte_mappings(
        parameter=parameter_market
    )
    all_int_states = int_to_prices_dict.keys()

    n_states = len(all_int_states)
    n_markets = len(super_star_markets)
    n_periods = parameter_deviation["total_periods"]

    all_state_simulations = np.empty(
        (n_markets, n_states, n_periods, n_agents), dtype=int
    )
    # Loop over all states and markets for the play simulation
    for current_int_state in all_int_states:
        for i_current_market, current_market in enumerate(super_star_markets):
            current_price_state = int_state_to_price_state(
                int_state=current_int_state, int_to_prices_dict=int_to_prices_dict
            )
            played_prices = play_without_deviation(
                parameter=parameter_deviation,
                all_agents=current_market,
                prices_to_int_dict=prices_to_int_dict,
                possible_prices=possible_prices,
                initial_price_state=current_price_state,
            )
            all_state_simulations[
                i_current_market, current_int_state, :, :
            ] = played_prices
    return all_state_simulations


if __name__ == "__main__":
    N_AGENTS = sys.argv[1]

    with open(
        ppj("IN_SIMULATION_PARAMETER", f"parameter_super_star_{N_AGENTS}_agent.json")
    ) as f:
        PARAMETER_MARKET = json.load(f)

    with open(ppj("IN_MODEL_SPECS", "deviation_simulation.json")) as f:
        PARAMETER_DEVIATION = json.load(f)

    with open(ppj("OUT_DATA", f"all_super_stars_{N_AGENTS}_agents.pickle"), "rb") as f:
        super_star_tuples = pickle.load(f)

    _, all_super_star_markets = zip(*super_star_tuples)

    array_all_state_simulations_results = play_from_all_states(
        super_star_markets=all_super_star_markets,
        n_agents=int(N_AGENTS),
        parameter_deviation=PARAMETER_DEVIATION,
        parameter_market=PARAMETER_MARKET,
    )
    with open(
        ppj("OUT_ANALYSIS", f"array_all_state_simulations_{N_AGENTS}_agents.pickle"),
        "wb",
    ) as f:
        pickle.dump(array_all_state_simulations_results, f)
