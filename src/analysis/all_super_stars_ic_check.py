"""

A module to check if, in expectation, the agents that use the
same parameters as the super star in the grid search learn
a behaviour that can be considered incentive compatible.
"""
import json
import pickle
import sys

import numpy as np

from bld.project_paths import project_paths_join as ppj
from src.analysis.check_ic import check_single_market_agent_ic


def check_ic_all_markets(
    array_markets_deviation, array_markets_no_deviation, parameter_market
):
    """

    A function to check for all markets if the first agent within this market learned a behaviour
    that can be considered incentive compatible.
    Note that it is assumed that for some market i,
    array_markets_deviation[i, :, :] and  array_markets_no_deviation[i, :, :] have the same agents
    with difference being that in the first their was an exogenously enforced deviation.

    Args:
        array_markets_deviation (array): Market prices in all markets without deviation
                                         Shape is (n_markets, n_periods, n_agents)
        array_markets_no_deviation (array): Market prices in all markets without deviation
                                            Shape is (n_markets, n_periods, n_agents)
        parameter_market (dict): Explained somewhere else TODO

    Returns:
        float: Share of all markets in which the first agent learned an IC behaviour.
    """
    n_markets = array_markets_deviation.shape[0]

    n_ic_markets = 0
    for i_market in range(n_markets):
        bool_ic, _, _ = check_single_market_agent_ic(
            market_prices_dev=array_markets_deviation[i_market, :, :],
            market_prices_no_dev=array_markets_no_deviation[i_market, :, :],
            parameter_market=parameter_market,
        )
        n_ic_markets += bool_ic

    share_ic_markets = n_ic_markets / n_markets
    return share_ic_markets


if __name__ == "__main__":
    N_AGENTS = sys.argv[1]

    with open(
        ppj("IN_SIMULATION_PARAMETER", f"parameter_super_star_{N_AGENTS}_agent.json")
    ) as f:
        PARAMETER_MARKET = json.load(f)

    with open(
        ppj("OUT_ANALYSIS", f"array_no_deviation_simulations_{N_AGENTS}_agents.pickle"),
        "rb",
    ) as f:
        ARRAY_NO_DEVIATION = pickle.load(f)

    with open(
        ppj("OUT_ANALYSIS", f"array_deviation_simulations_{N_AGENTS}_agents.pickle"),
        "rb",
    ) as f:
        ARRAY_DEVIATION = pickle.load(f)

    IC_SHARE = check_ic_all_markets(
        array_markets_deviation=ARRAY_DEVIATION,
        array_markets_no_deviation=ARRAY_NO_DEVIATION,
        parameter_market=PARAMETER_MARKET,
    )
    out_dict_all_markets = {
        f"IC_share_all_markets_{N_AGENTS}_agents": str(round(IC_SHARE, 3))
    }
    with open(
        ppj("OUT_ANALYSIS", f"ic_all_super_star_{N_AGENTS}_agents.json"), "w"
    ) as f:
        json.dump(out_dict_all_markets, f, indent=4)
