"""

A module that collects function to check the incentive
compatibility of the agents decision.
"""
import numpy as np

from qpricesim.model_code.economic_environment import calc_reward
from qpricesim.model_code.economic_environment import calc_winning_price


def check_single_market_agent_ic(
    market_prices_dev, market_prices_no_dev, parameter_market
):
    """
    For a single market simulation takes in the simulation market prices over all periods
    and calculates if a deviation was profitable or not.
    It is assumed that the first agent (index 0) deviated.

    Args:
        market_prices_dev (array): Array with prices with a exogenously enforced deviation.
                                   The shape should be (simulation periods, number of agents).
        market_prices_no_dev (array): Array with prices without a deviation. The shape should
                                      be (simulation periods, number of agents).
        parameter_market (dict): Dict with market specs explained somewhere else TODO

    Returns:
        # TODO MAKE OUTPUT DICT HERE ALREADY
        tuple: - Boolean: True if the deviation was not profitable, else False
               - Profit without deviation
               - Profit with deviation
    """
    p_star_n_winners_dev = np.apply_along_axis(calc_winning_price, 1, market_prices_dev)
    p_star_n_winners_no_dev = np.apply_along_axis(
        calc_winning_price, 1, market_prices_no_dev
    )
    total_profit_dev = 0
    total_profit_no_dev = 0

    n_periods = market_prices_dev.shape[0]
    discount_rate = parameter_market["discount_rate"]

    # TODO: Vectorize for readability?
    for t in range(n_periods):
        period_reward_dev = calc_reward(
            p_i=market_prices_dev[t, 0],
            winning_price=p_star_n_winners_dev[t, 0],
            n_winning_price=p_star_n_winners_dev[t, 1],
            reservation_price=parameter_market["reservation_price"],
            m_consumer=parameter_market["m_consumer"],
        )
        total_profit_dev = total_profit_dev + discount_rate ** t * period_reward_dev

        period_reward_no_dev = calc_reward(
            p_i=market_prices_no_dev[t, 0],
            winning_price=p_star_n_winners_no_dev[t, 0],
            n_winning_price=p_star_n_winners_no_dev[t, 1],
            reservation_price=parameter_market["reservation_price"],
            m_consumer=parameter_market["m_consumer"],
        )
        total_profit_no_dev = (
            total_profit_no_dev + discount_rate ** t * period_reward_no_dev
        )

    # TODO: MAKE DICT HERE ALREADY
    if total_profit_no_dev >= total_profit_dev:
        return (True, total_profit_no_dev, total_profit_dev)
    else:
        return (False, total_profit_no_dev, total_profit_dev)
