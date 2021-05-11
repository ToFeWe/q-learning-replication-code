"""

A module to create a JSON/pickle(dict) file which
contains the best-responses for the
algorithmic sellers as used in the otree
experiment and also the state of convergence
for the super star agent.
"""
import json
import pickle
import sys

from bld.project_paths import project_paths as pp
from bld.project_paths import project_paths_join as ppj
from qpricesim.simulations.utils_simulation import gen_possible_prices
from qpricesim.simulations.utils_simulation import (
    gen_price_combination_byte_mappings,
)
from qpricesim.simulations.utils_simulation import (
    int_state_to_price_state,
)


def create_best_response_dict(super_star, parameter):
    """
    A function that takes the super star agent and returns
    a dictionary which maps all possible price states to
    price actions

    Args:
        super_star (QLearningAgent): The best-performing agent from the grid search
        parameter (dict): Parameter dict as explained somewhere else TODO

    Returns:
        dict: Dictionary which maps price state to picked price actions from the
              super star agent.
    """
    _, int_to_prices_dict = gen_price_combination_byte_mappings(parameter=parameter)
    all_int_states = int_to_prices_dict.keys()
    price_array = gen_possible_prices(parameter=parameter)
    agent_br_dict = {}

    # For each integer state get the best response (price) of the
    # agent and the corresponding price state representation
    # and add it to a dict.
    for int_state in all_int_states:
        br_int_action = super_star.get_best_action(int_state)
        br_price_action = price_array[br_int_action]
        price_state = int_state_to_price_state(
            int_state=int_state, int_to_prices_dict=int_to_prices_dict
        )

        # Make price state immutable (e.g. to tuple) such that it can act as a
        # key
        price_state_tuple = tuple(price_state)
        agent_br_dict[price_state_tuple] = br_price_action

    return agent_br_dict


def int_state_of_convergence_to_prices(int_state, parameter):
    """
    A function to transform the integer/index representation of the state
    of convergence of the super star agent to the price combination
    representation.

    Args:
        int_state (integer): Integer/index representation of
                             the state of convergence of the
                             super star agent.
        parameter (dict): Explained somewhere else TODO

    Returns:
        array: Array of prices, which are the state of convergence.
    """
    _, int_to_prices_dict = gen_price_combination_byte_mappings(parameter=parameter)
    price_state = int_state_to_price_state(
        int_state=int_state, int_to_prices_dict=int_to_prices_dict
    )
    return tuple(price_state)


def output_dict_to_json(path, output_dict):
    """
    Takes the output dictionary and transforms all keys/values to string.
    Furthermore, it saves the dictionary as a JSON file.

    Args:
        path (string): Path where the JSON file is saved.
        output_dict (dict): Dictionary with all outputs that should be written to disc
                            It is assumed that the dictionary has the following keys:

                            output_dict['prices_to_br'] -> Another dictionary as created by
                                                           create_best_response_dict().
                            output_dict['state_of_convergence'] -> State of convergence of the
                                                                   super star in the price re-
                                                                   presentation.
    """
    # Transform to String for JSON output
    output_dict["prices_to_br"] = {
        str(k): str(v) for k, v in output_dict["prices_to_br"].items()
    }
    output_dict["state_of_convergence"] = str(output_dict["state_of_convergence"])
    with open(path, "w") as f:
        json.dump(output_dict, f, indent=4)


if __name__ == "__main__":
    N_AGENTS = sys.argv[1]

    # Load the super star for the given market size.
    with open(
        ppj(
            f"IN_SIMULATION_{N_AGENTS}_AGENT",
            f"experiment_super_star_{N_AGENTS}_agent.pickle",
        ),
        "rb",
    ) as f:
        best_agent_output = pickle.load(f)

    # Load the parameters that are used in the market.
    with open(
        ppj("IN_SIMULATION_PARAMETER", f"parameter_super_star_{N_AGENTS}_agent.json"),
        "r",
    ) as f:
        PARAMETER_IN = json.load(f)

    # State of convergence is the second to last element
    # in the super star output.
    int_state_of_convergence = best_agent_output[-2]

    # The actual QLearningAgent is the first element in the
    # super star output.
    SUPER_STAR_AGENT = best_agent_output[0]

    # Create the best response dict
    br_dict = create_best_response_dict(
        super_star=SUPER_STAR_AGENT, parameter=PARAMETER_IN
    )

    # Get the price representation of the state of convergence from
    # the super star agent.
    price_state_of_convergence = int_state_of_convergence_to_prices(
        int_state=int_state_of_convergence, parameter=PARAMETER_IN
    )

    OUTPUT_DICT = {}
    OUTPUT_DICT["prices_to_br"] = br_dict
    OUTPUT_DICT["state_of_convergence"] = price_state_of_convergence

    # Write the dict to JSON and pickle for oTree
    output_dict_to_json(
        path=ppj("OUT_DATA", f"otree_super_star_{N_AGENTS}_agents.json"),
        output_dict=OUTPUT_DICT,
    )
    with open(ppj("OUT_DATA", f"otree_super_star_{N_AGENTS}_agents.pickle"), "wb") as f:
        pickle.dump(OUTPUT_DICT, f)
