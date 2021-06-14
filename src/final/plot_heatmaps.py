"""

Modules to plot heatmaps for different
"""
import json
import pickle
import sys

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from bld.project_paths import project_paths_join as ppj


def set_ticks_heatmap(axis_in, parameter_cases):
    """
    Add ticks to the heatmap given by the *axis_in*
    element.

    Args:
        axis_in (matplotlib.axis.Axis): Axis element of the heatmap
        parameter_cases (dict): Parameter cases as used in the simulation TODO:Explain somwhere

    Returns:
        matplotlib.axis.Axis: Axis element with added ticks and labels.
    """
    beta_mid_point = np.round(
        (parameter_cases["beta_max"] - parameter_cases["beta_min"]) / 2, 6
    )
    alpha_mid_point = (parameter_cases["alpha_max"] + parameter_cases["alpha_min"]) / 2

    # Make Labels for beta
    axis_in.set_xlabel(r"$\beta$", labelpad=10)
    axis_in.set_xticks(
        [0, parameter_cases["grid_points"] / 2, parameter_cases["grid_points"]]
    )
    axis_in.set_xticklabels(
        [parameter_cases["beta_min"], beta_mid_point, parameter_cases["beta_max"]]
    )

    # Label for alpha
    axis_in.set_ylabel(r"$\alpha$", rotation=0)
    axis_in.set_yticks(
        [0, parameter_cases["grid_points"] / 2, parameter_cases["grid_points"]]
    )
    axis_in.set_yticklabels(
        [parameter_cases["alpha_max"], alpha_mid_point, parameter_cases["alpha_min"]]
    )

    # Matplotlib magic
    axis_in.yaxis.set_label_coords(-0.17, 0.477)

    return axis_in


def value_function_heatmap(array_list, fun, title, n_agents, parameter_cases):
    """
    A function to plot the heatmap using the aggregation level provided by
    the *fun* argument, which is ideally a numpy funcion like np.mean().

    Args:
        array_list (list): List of arrays from a specific metric from the Monte Carlo simulation
        fun (function): Aggregation function used on the array list
        title (string): Title of the figure
        n_agent (integer): Number of agents in the market
        parameter_cases (dict): Parameter cases as used in the simulation TODO:Explain somewhere

    Returns:
        tuple: Figure and Axis element (matplotlib) of the heatmap
    """
    fig, ax = plt.subplots()

    # V^C = (1/(1-0.95)) * m_consumers * p^m / n_firms
    # V^D = (1/(1-0.95)) * m_consumers * p^NE / n_firms
    # Numpy Axis is always zero
    if n_agents == "3":
        # Flip up-down to have the smallest value in the bottom left corner
        sns.heatmap(np.flipud(fun(array_list, axis=0)), ax=ax, vmin=0, vmax=1800)
        cbar = ax.collections[0].colorbar
        cbar.set_ticks([0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800])
        cbar.set_ticklabels(
            [
                "0",
                "200",
                "$V^D=400$",
                "600",
                "800",
                "1000",
                "1200",
                "1400",
                "$V^C=1600$",
                "1800",
            ]
        )
    elif n_agents == "2":
        # Flip up-down to have the smallest value in the bottom left corner
        sns.heatmap(np.flipud(fun(array_list, axis=0)), ax=ax, vmin=0, vmax=2600)
        cbar = ax.collections[0].colorbar
        cbar.set_ticks(
            [
                0,
                200,
                400,
                600,
                800,
                1000,
                1200,
                1400,
                1600,
                1800,
                2000,
                2200,
                2400,
                2600,
            ]
        )
        cbar.set_ticklabels(
            [
                "0",
                "200",
                "400",
                "$V^D=600$",
                "800",
                "1000",
                "1200",
                "1400",
                "1600",
                "1800",
                "2000",
                "2200",
                "$V^C=2400$",
                "2600",
            ]
        )

    # Set ticks
    ax = set_ticks_heatmap(axis_in=ax, parameter_cases=parameter_cases)
    # Add title
    ax.set_title(title)

    return fig, ax


def zero_one_heatmap(array_list, fun, title, parameter_cases):
    """
    Generate a heatmap where the values are bound by zero and one.

    Args:
        array_list (list): List of arrays from a specific metric from the Monte Carlo simulation.
        fun (function): Aggregation function used on the array list
        title (string): Title of the figure
        parameter_cases (dict): Parameter cases as used in the simulation TODO:Explain somewhere

    Returns:
        tuple: Figure and Axis element (matplotlib) of the heatmap
    """
    fig, ax = plt.subplots()
    # Flip up-down to have the smallest value in the bottom left corner
    sns.heatmap(np.flipud(fun(array_list, axis=0)), ax=ax, vmin=0, vmax=1)
    cbar = ax.collections[0].colorbar
    cbar.set_ticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    cbar.set_ticklabels(["0", "0.2", "0.4", "0.6", "0.8", "1"])

    ax = set_ticks_heatmap(axis_in=ax, parameter_cases=parameter_cases)
    # Add title
    ax.set_title(title)

    return fig, ax


def price_heatmap(array_list, fun, title, parameter_cases):
    """
    Generate a heatmap where the values are bound by the minimal and
    maximal price.

    Args:
        array_list (list): List of arrays from a specific metric from the Monte Carlo simulation.
        fun (function): Aggregation function used on the array list
        title (string): Title of the figure
        parameter_cases (dict): Parameter cases as used in the simulation TODO:Explain somewhere

    Returns:
        tuple: Figure and Axis element (matplotlib) of the heatmap
    """
    fig, ax = plt.subplots()
    # Flip up-down to have the smallest value in the bottom left corner
    sns.heatmap(np.flipud(fun(array_list, axis=0)), ax=ax, vmin=0, vmax=5)
    cbar = ax.collections[0].colorbar
    cbar.set_ticks([0, 1, 2, 3, 4, 5])
    cbar.set_ticklabels(["0", "1", "2", "3", "4", "5"])

    ax = set_ticks_heatmap(axis_in=ax, parameter_cases=parameter_cases)
    # Add title
    ax.set_title(title)

    return fig, ax


def add_best_agent(ax, parameter_cases, parameter_super_star):
    """
    Add a dot to axis with the parameter of the super star.


    Args:
        ax (AxisElement): Matplotlib axis element of the plot
        parameter_cases (dict): Parameter cases as used in the simulation TODO:Explain somewhere
        parameter_super_star (dict): Parameter of the super star agent TODO:Explain somewhere

    Returns:
        [type]: [description]
    """

    alpha_grid = list(
        np.linspace(
            parameter_cases["alpha_min"],
            parameter_cases["alpha_max"],
            parameter_cases["grid_points"],
        )
    )
    beta_grid = list(
        np.linspace(
            parameter_cases["beta_min"],
            parameter_cases["beta_max"],
            parameter_cases["grid_points"],
        )
    )

    beta_index = beta_grid.index(parameter_super_star["beta_decay"])
    # Note that the alpha dimension has been Flip up-down to have
    # the smallest value in the bottom left corner.
    alpha_index = alpha_grid[::-1].index(parameter_super_star["learning_rate"])
    # TODO: Is the order here correct?! Not first alpha and then beta?!?! TODO
    ax.plot(beta_index, alpha_index, "x", markersize=5)[0]
    return ax


if __name__ == "__main__":
    N_AGENTS = sys.argv[1]
    METRIC = sys.argv[2]
    WITH_SUPER_STAR = sys.argv[3]

    # Title mapping dict:
    title_mapping = {
        "state_profitability": "Profitability in the state of convergence",
        "weighted_profitability": "Average weighted profitability",
        "best_response_share": "Share of best-reponses",
        "avg_profit": "Average profitability",
        "avg_price": "Average price upon convergence",
        "nash_equilibrium": "Share of Nash equilibria",
    }

    with open(
        ppj("IN_SIMULATION_PARAMETER", f"parameter_{N_AGENTS}_agent_cases.json")
    ) as f:
        PARAMETER_CASES = json.load(f)

    with open(ppj("OUT_DATA", f"grid_{N_AGENTS}_agents.pickle"), "rb") as f:
        DICT_GRID_VALUES = pickle.load(f)

    CURRENT_TITLE = title_mapping[METRIC]
    if METRIC == "best_response_share" or METRIC == "nash_equilibrium":
        current_fig, current_axis = zero_one_heatmap(
            array_list=DICT_GRID_VALUES[METRIC],
            fun=np.mean,
            title=CURRENT_TITLE,
            parameter_cases=PARAMETER_CASES,
        )
    elif METRIC == "avg_price":
        current_fig, current_axis = price_heatmap(
            array_list=DICT_GRID_VALUES[METRIC],
            fun=np.mean,
            title=CURRENT_TITLE,
            parameter_cases=PARAMETER_CASES,
        )
    else:
        current_fig, current_axis = value_function_heatmap(
            array_list=DICT_GRID_VALUES[METRIC],
            fun=np.mean,
            title=CURRENT_TITLE,
            n_agents=N_AGENTS,
            parameter_cases=PARAMETER_CASES,
        )
    if WITH_SUPER_STAR == "with":
        with open(
            ppj(
                "IN_SIMULATION_PARAMETER", f"parameter_super_star_{N_AGENTS}_agent.json"
            )
        ) as f:
            PARAMETER_SUPER_STAR = json.load(f)
        current_axis = add_best_agent(
            ax=current_axis,
            parameter_cases=PARAMETER_CASES,
            parameter_super_star=PARAMETER_SUPER_STAR,
        )
    current_fig.savefig(
        ppj(
            "OUT_FIGURES",
            f"heatmap_{METRIC}_{WITH_SUPER_STAR}_super_star_{N_AGENTS}_n_agents.pdf",
        ),
        bbox_inches="tight",
    )
