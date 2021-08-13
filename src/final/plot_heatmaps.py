"""

Modules to plot heatmaps for different
"""
import json
import pickle
import sys

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import rc
import matplotlib as mpl

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
    axis_in.set_xlabel(r"Exploration decay ($\beta$)", labelpad=10)
    axis_in.set_xticks(
        [0, parameter_cases["grid_points"] / 2, parameter_cases["grid_points"]]
    )
    axis_in.set_xticklabels(
        [parameter_cases["beta_min"], beta_mid_point, parameter_cases["beta_max"]], rotation="horizontal"
    )

    # Label for alpha
    axis_in.set_ylabel(r"Learning rate $(\alpha$)")
    axis_in.set_yticks(
        [0, parameter_cases["grid_points"] / 2, parameter_cases["grid_points"]]
    )
    # TODO: Continue with all those plots that they fit in the paper
    axis_in.set_yticklabels(
        [parameter_cases["alpha_max"], alpha_mid_point, parameter_cases["alpha_min"]], rotation="horizontal")

    axis_in.tick_params(axis='x', labelsize=8)
    axis_in.tick_params(axis='y', labelsize=8) 

    return axis_in


def value_function_heatmap(array_list, fun, n_agents, parameter_cases):
    """
    A function to plot the heatmap using the aggregation level provided by
    the *fun* argument, which is ideally a numpy funcion like np.mean().

    Args:
        array_list (list): List of arrays from a specific metric from the Monte Carlo simulation
        fun (function): Aggregation function used on the array list
        n_agent (integer): Number of agents in the market
        parameter_cases (dict): Parameter cases as used in the simulation TODO:Explain somewhere

    Returns:
        tuple: Figure and Axis element (matplotlib) of the heatmap
    """
    fig, ax = plt.subplots(figsize=(2.5,1.8))

    # V^C = (1/(1-0.95)) * m_consumers * p^m / n_firms
    # V^NE = (1/(1-0.95)) * m_consumers * p^NE / n_firms
    # Numpy Axis is always zero
    if n_agents == "3":
        # Flip up-down to have the smallest value in the bottom left corner
        sns.heatmap(np.flipud(fun(array_list, axis=0)), ax=ax, vmin=0, vmax=1600)
        # Add title
        ax.set_title("0H3A")

        cbar = ax.collections[0].colorbar
        
        cbar.set_ticks([0, 400, 1600])
        cbar.set_ticklabels(
            [
                "0",
                "$V^NE=400$",
                "$V^C=1600$",
            ]
        )
        cbar.ax.tick_params(labelsize=8)

    elif n_agents == "2":
        # Flip up-down to have the smallest value in the bottom left corner
        sns.heatmap(np.flipud(fun(array_list, axis=0)), ax=ax, vmin=0, vmax=2400)

        # Add title
        ax.set_title("0H2A")

        cbar = ax.collections[0].colorbar

        cbar.set_ticks(
            [
                0,
                600,
                2400,
            ]
        )
        cbar.set_ticklabels(
            [
                "0",
                "$V^NE=600$",
                "$V^C=2400$",
            ]
        )
    cbar.ax.tick_params(labelsize=8)

    # Set ticks
    ax = set_ticks_heatmap(axis_in=ax, parameter_cases=parameter_cases)

    return fig, ax


def zero_one_heatmap(array_list, fun, n_agents, parameter_cases):
    """
    Generate a heatmap where the values are bound by zero and one.

    Args:
        array_list (list): List of arrays from a specific metric from the Monte Carlo simulation.
        fun (function): Aggregation function used on the array list
        n_agent (integer): Number of agents in the market
        parameter_cases (dict): Parameter cases as used in the simulation TODO:Explain somewhere

    Returns:
        tuple: Figure and Axis element (matplotlib) of the heatmap
    """
    fig, ax = plt.subplots(figsize=(2.5,1.8))
    # Flip up-down to have the smallest value in the bottom left corner
    sns.heatmap(np.flipud(fun(array_list, axis=0)), ax=ax, vmin=0, vmax=1)
    cbar = ax.collections[0].colorbar
    cbar.set_ticks([0, 0.5, 1])
    cbar.set_ticklabels(["0", "0.5", "1"])
    cbar.ax.tick_params(labelsize=8)

    ax = set_ticks_heatmap(axis_in=ax, parameter_cases=parameter_cases)
    # Add title
    if n_agents == "2":
        ax.set_title("0H2A")
    else:
        ax.set_title("0H3A")

    return fig, ax


def price_heatmap(array_list, fun, n_agents, parameter_cases):
    """
    Generate a heatmap where the values are bound by the minimal and
    maximal price.

    Args:
        array_list (list): List of arrays from a specific metric from the Monte Carlo simulation.
        fun (function): Aggregation function used on the array list
        n_agent (integer): Number of agents in the market
        parameter_cases (dict): Parameter cases as used in the simulation TODO:Explain somewhere

    Returns:
        tuple: Figure and Axis element (matplotlib) of the heatmap
    """
    fig, ax = plt.subplots(figsize=(2.5,1.8))
    # Flip up-down to have the smallest value in the bottom left corner
    sns.heatmap(np.flipud(fun(array_list, axis=0)), ax=ax, vmin=0, vmax=5)
    cbar = ax.collections[0].colorbar
    cbar.set_ticks([0, 1, 2, 3, 4, 5])
    cbar.set_ticklabels(["0", "$p^{NE}=$1", "2", "3", "$p^{M}=$4", "5"])
    cbar.ax.tick_params(labelsize=8)

    ax = set_ticks_heatmap(axis_in=ax, parameter_cases=parameter_cases)

    # Add title
    if n_agents == "2":
        ax.set_title("0H2A")
    else:
        ax.set_title("0H3A")

    return fig, ax


if __name__ == "__main__":
    N_AGENTS = sys.argv[1]
    METRIC = sys.argv[2]
    WITH_SUPER_STAR = sys.argv[3]

    # Change font to look similar to latex
    # I cannot use Latex backend here with waf and matplotlib
    mpl.rc('font', family='serif') 
    mpl.rc('font', serif='Century') 
    plt.rcParams.update({'font.size': 12,
                         'axes.titlesize': 12})    

    with open(
        ppj("IN_SIMULATION_PARAMETER", f"parameter_{N_AGENTS}_agent_cases.json")
    ) as f:
        PARAMETER_CASES = json.load(f)

    with open(ppj("OUT_DATA", f"grid_{N_AGENTS}_agents.pickle"), "rb") as f:
        DICT_GRID_VALUES = pickle.load(f)

    if METRIC == "best_response_share" or METRIC == "nash_equilibrium":
        current_fig, current_axis = zero_one_heatmap(
            array_list=DICT_GRID_VALUES[METRIC],
            fun=np.mean,
            n_agents=N_AGENTS,
            parameter_cases=PARAMETER_CASES,
        )
    elif METRIC == "avg_price":
        current_fig, current_axis = price_heatmap(
            array_list=DICT_GRID_VALUES[METRIC],
            fun=np.mean,
            n_agents=N_AGENTS,
            parameter_cases=PARAMETER_CASES,
        )
    else:
        current_fig, current_axis = value_function_heatmap(
            array_list=DICT_GRID_VALUES[METRIC],
            fun=np.mean,
            n_agents=N_AGENTS,
            parameter_cases=PARAMETER_CASES,
        )
    current_fig.savefig(
        ppj(
            "OUT_FIGURES",
            f"heatmap_{METRIC}_{WITH_SUPER_STAR}_super_star_{N_AGENTS}_n_agents.pdf",
        ),
        bbox_inches="tight",
        pad_inches = 0
    )
