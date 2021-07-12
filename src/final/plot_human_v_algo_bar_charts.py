"""

A module to plot the bar chart that compares
human and algorithms.
"""
import pickle

from matplotlib import rc

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from bld.project_paths import project_paths_join as ppj


def create_value_dict(data_last_super_game_agg,
                      super_star_avg_prices_2_agents,
                      super_star_avg_prices_3_agents,
                      entire_price_grid_avg_prices_2_agents,
                      entire_price_grid_avg_prices_3_agents):
    """
    A function to create a comprehensive dictionary with all
    values that we need to create the plot.

    Args:
        data_last_super_game_agg (DataFrame): DataFrame with experimental results
        super_star_avg_prices_2_agents (array): Average prices of super star markets upon convergence
                                                   (2 firm market).
        super_star_avg_prices_3_agents (array): Average prices of super star markets upon convergence
                                                   (3 firm market).
        entire_price_grid_avg_prices_2_agents (array): Average prices of the entire grid upon convergence
                                                          (2 firm market).
        entire_price_grid_avg_prices_3_agents (array): Average prices of the entire grid upon convergence
                                                          (3 firm market).
    Returns:
        dict: Dictionary with values for plotting
    """
    # To make the plotting easier, we write the data into a structured dict
    plotting_dict = {}

    # First the fully human markets
    plotting_dict['Humans'] = {}
    plotting_dict['Humans']['means'] = list()
    plotting_dict['Humans']['means'].extend(
        [data_last_super_game_agg.loc[data_last_super_game_agg['treatment'] == '2H0A']['winning_price'].mean(),
         data_last_super_game_agg.loc[data_last_super_game_agg['treatment'] == '3H0A']['winning_price'].mean()]
    )
    plotting_dict['Humans']['std'] = list()
    plotting_dict['Humans']['std'].extend(
        [data_last_super_game_agg.loc[data_last_super_game_agg['treatment'] == '2H0A']['winning_price'].std(),
         data_last_super_game_agg.loc[data_last_super_game_agg['treatment'] == '3H0A']['winning_price'].std()]
    )

    # Now the algorithm markets
    # First the super star

    plotting_dict['Algorithm'] = {}
    plotting_dict['Algorithm']['means'] = list()
    plotting_dict['Algorithm']['means'].extend(
        [super_star_avg_prices_2_agents.mean(),
         super_star_avg_prices_3_agents.mean()]
    )
    plotting_dict['Algorithm']['std'] = list()
    plotting_dict['Algorithm']['std'].extend(
        [super_star_avg_prices_2_agents.std(),
         super_star_avg_prices_3_agents.std()]
    )

    return plotting_dict


def make_human_v_algo_plot(plotting_dict_in):
    # set width of bar

    barWidth = 0.35
    distance = 0
    all_colors = sns.color_palette('colorblind')

    fig, ax = plt.subplots(1)
    fig.set_size_inches(18.5, 10.5)

    all_groups = list(plotting_dict_in.keys())

    all_r = [np.arange(2) + barWidth * x for x in range(2)]

    # Make the plot
    for ix_group, group in enumerate(all_groups):
        ax.bar(all_r[ix_group], plotting_dict_in[group]['means'],
               yerr=plotting_dict_in[group]['std'],
               color=all_colors[ix_group], width=barWidth, edgecolor='white',
               label=group, capsize=4)

    ax.set_ylim([0, 5])
    ax.set_ylabel('Mean market price')

    # Create the label (mean price) over the error bar
    rects = ax.patches
    all_means = list(
        np.array([plotting_dict_in[group]['means'] for group in all_groups]).flat)
    all_sem = list(np.array([plotting_dict_in[group]['std']
                   for group in all_groups]).flat)
    labels = ['%.3f' % elem for elem in all_means]
    distances = all_sem

    label_ticks_pos = []
    for rect, label, distance in zip(rects, labels, distances):
        height = rect.get_height() + distance
        ax.text(rect.get_x() + rect.get_width() / 2, height, label,
                ha='center', va='bottom', fontweight='bold')

        # Posititon for x labels
        label_ticks_pos.append(rect.get_x() + rect.get_width() / 2)

    labels_bars = [
        '\\textsc{2H0A}',
        '\\textsc{3H0A}',
        '\\textsc{0H2A}',
        '\\textsc{0H3A}']

    ax.set_xticks(label_ticks_pos)
    ax.set_xticklabels(labels_bars)

    # Adding top labels with matplotlib magic numbers
    ax.text(0.01, 4.7, 'Two firm markets', fontsize=25)
    ax.text(1.00, 4.7, 'Three firm markets', fontsize=25)

    hatches = ['/', '/', '\\', '\\']

    # Loop over the bars to add hatches
    for i, thisbar in enumerate(rects):
        # Set a different hatch for each bar
        thisbar.set_hatch(hatches[i])

    # Create legend & Show graphic
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.14), ncol=3)
    
    # Turn of xaxis grid
    plt.gca().xaxis.grid(False)
    
    # Save the figure
    fig.savefig(ppj("OUT_FIGURES", "bar_plot_human_v_algos.pdf"),
                bbox_inches='tight')


if __name__ == '__main__':
    # Set some general global plotting parameter
    rc('text', usetex=True)
    plt.rcParams.update({'font.size': 20})    
    plt.style.use('seaborn-whitegrid')

    # Load the data
    # Two firm algorithm markets
    with open(ppj("OUT_DATA", "entire_price_grid_avg_prices_2_agents.pickle"), "rb") as f:
        entire_price_grid_avg_prices_2_agents_in = pickle.load(f)
    with open(ppj("OUT_DATA", "super_star_avg_prices_2_agents.pickle"), "rb") as f:
        super_star_avg_prices_2_agents_in = pickle.load(f)

    # Three firm algorithm markets
    with open(ppj("OUT_DATA", "entire_price_grid_avg_prices_3_agents.pickle"), "rb") as f:
        entire_price_grid_avg_prices_3_agents_in = pickle.load(f)
    with open(ppj("OUT_DATA", "super_star_avg_prices_3_agents.pickle"), "rb") as f:
        super_star_avg_prices_3_agents_in = pickle.load(f)

    # Load the data from the humans
    with open(ppj("OUT_DATA", "data_group_level.pickle"), "rb") as f:
        data_group_level = pickle.load(f)

    # Subset the human data to the last super game and the relevant treatments
    # for this plot.
    data_last_super_game = data_group_level.loc[
        (data_group_level['super_game'] == 3) &
        (data_group_level['treatment'].isin(['3H0A', '2H0A']))
    ].copy()

    # Aggregate the human data by super_group_id_general which gives us the mean
    # for each independent observation in the last super game
    data_last_super_game_agg_in = data_last_super_game.groupby(
        ['super_group_id_general', 'treatment'], as_index=False)[['winning_price']].mean()

    # Create plotting dict
    PLOTTING_DICT = create_value_dict(
        data_last_super_game_agg=data_last_super_game_agg_in,
        super_star_avg_prices_2_agents=super_star_avg_prices_2_agents_in,
        super_star_avg_prices_3_agents=super_star_avg_prices_3_agents_in,
        entire_price_grid_avg_prices_2_agents=entire_price_grid_avg_prices_2_agents_in,
        entire_price_grid_avg_prices_3_agents=entire_price_grid_avg_prices_3_agents_in)
    # Make the plot
    make_human_v_algo_plot(plotting_dict_in=PLOTTING_DICT)
