"""

A module to plot the deviation simulation
results.
"""
import json
import pickle
import sys

import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from bld.project_paths import project_paths_join as ppj




def make_plot(devation_array, parameter_deviation, parameter_market, out_path):
    """
    A function to make the deviation plots.

    Args:
        devation_array (array): Array with the price sequences with a deviation
        parameter_deviation (dict): Parameters for the deviation simulation
        parameter_market (dict): Parameters that describe the market environment
        number_of_firms (integer): Number of firms in the market
        out_path (string): filename/path where to save the graph
    """
    periods_to_consider = parameter_deviation["total_plotting_periods"]

    # We cut the first periods as they have a higher variation given that
    # some agents might have converged in a period where they picked a random
    # action. This, however, is misleading, as it is not the actual
    # steady-state of convergence
    cut_first_periods = parameter_deviation["cut_first_periods"]
    n_agent = parameter_market["n_agent"]
    all_marker = ["o", "x", "*"]
    all_label = ["Firm 1", "Firm 2", "Firm 3"]
    all_color = ["#3498db", "#e74c3c", "#2ecc71"]

    x_axis = np.arange(1, periods_to_consider - cut_first_periods + 1)

    array_to_plot = np.array(devation_array)[
        :, cut_first_periods:periods_to_consider, :
    ]

    prices_std = np.std(np.array(array_to_plot), axis=0)
    prices_mean = np.mean(np.array(array_to_plot), axis=0)

    # fig, ax = plt.subplots(figsize=[10, 6])  # TODO: do it general? figsize=(5,3.6)
    fig, ax = plt.subplots(figsize=(3.2,2.4))

    for agent_i in range(n_agent):
        _, caps, bars = ax.errorbar(
            x_axis,
            prices_mean[:, agent_i],
            yerr=prices_std[:, agent_i],
            capsize=2,
            capthick=2,
            marker=all_marker[agent_i],
            label=all_label[agent_i],
            color=all_color[agent_i],
        )

        [bar.set_alpha(0.3) for bar in bars]
        [cap.set_alpha(0.3) for cap in caps]

    ax.set_ylim([0, 5])
    ax.set_xlabel("t")
    ax.set_ylabel("Price")
    ax.set_xticks(x_axis)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.legend(fontsize=8)
    
    # Turn off xaxis grid
    plt.gca().xaxis.grid(False)

    # Set labelsize
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8) 

    # Add title
    if n_agent == 2:
        ax.set_title('0H2A')
    else:
        ax.set_title('0H3A')

    fig.savefig(out_path, bbox_inches="tight", pad_inches = 0)


if __name__ == "__main__":
    N_AGENTS = sys.argv[1]
   
    # Change font to look similar to latex
    # I cannot use Latex backend here with waf and matplotlib
    plt.style.use('seaborn-whitegrid')
    mpl.rc('font', family='serif') 
    mpl.rc('font', serif='Century') 
    plt.rcParams.update({'font.size': 12,
                         'axes.titlesize': 12})    

    with open(
        ppj("IN_SIMULATION_PARAMETER", f"parameter_{N_AGENTS}_agent_base.json")
    ) as f:
        PARAMETER_MARKET = json.load(f)

    with open(ppj("IN_MODEL_SPECS", "deviation_simulation.json")) as f:
        PARAMETER_DEVIATION = json.load(f)

    with open(
        ppj("OUT_ANALYSIS", f"array_deviation_simulations_{N_AGENTS}_agents.pickle"),
        "rb",
    ) as f:
        ARRAY_DEVIATION_SIMULATION = pickle.load(f)

    OUT_PATH = ppj("OUT_FIGURES", f"deviation_plot_{N_AGENTS}_agents.pdf")


    make_plot(
        devation_array=ARRAY_DEVIATION_SIMULATION,
        parameter_deviation=PARAMETER_DEVIATION,
        parameter_market=PARAMETER_MARKET,
        out_path=OUT_PATH,
    )
