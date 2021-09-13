"""

A module to plot the bar chart that compares
human and algorithms.
"""
import pickle

import matplotlib as mpl

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from bld.project_paths import project_paths_join as ppj


def create_value_dict(data_agg,
                      super_star_avg_prices_2_agents,
                      super_star_avg_prices_3_agents
                      ):
    """
    A function to create a comprehensive dictionary with all
    values that we need to create the plot.

    Args:
        data_agg (DataFrame): DataFrame with experimental results
        super_star_avg_prices_2_agents (array): Average prices of super star markets upon convergence
                                                   (2 firm market).
        super_star_avg_prices_3_agents (array): Average prices of super star markets upon convergence
                                                   (3 firm market).
    Returns:
        dict: Dictionary with values for plotting
    """
    # To make the plotting easier, we write the data into a structured dict
    plotting_dict = {}

    # First the fully human markets
    plotting_dict['Humans'] = {}
    plotting_dict['Humans']['means'] = {}
    plotting_dict['Humans']['std'] = {}

    # Loop over all super games
    for sg in range(1,4):
        # Create subset of data for current sg
        current_subset_sg = data_agg.loc[data_agg['super_game'] == sg]

        # get means and std
        plotting_dict['Humans']['means'][sg] = list()
        plotting_dict['Humans']['means'][sg].extend(
            [current_subset_sg.loc[current_subset_sg['treatment'] == '2H0A']['winning_price'].mean(),
             current_subset_sg.loc[current_subset_sg['treatment'] == '3H0A']['winning_price'].mean()]
        )
        plotting_dict['Humans']['std'][sg] = list()
        plotting_dict['Humans']['std'][sg].extend(
            [current_subset_sg.loc[current_subset_sg['treatment'] == '2H0A']['winning_price'].std(),
             current_subset_sg.loc[current_subset_sg['treatment'] == '3H0A']['winning_price'].std()]
        )

    # Now the algorithm markets
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
    spacing_groups= 1.7
    algo_color = ['#648FFF']
    human_color = sns.color_palette('colorblind')[7]
    all_colors = [human_color, algo_color]

    fig, ax = plt.subplots(figsize=(5,3.6))
    # fig.set_size_inches(18.5, 10.5)

    all_groups = list(plotting_dict_in.keys())

    all_r = [np.arange(2) * spacing_groups + barWidth * x for x in range(4)]

    # Create to lists (mean and std) to flatten the value dict
    # Those will be used as the labels in the plots
    all_means = []
    all_stds = []

    # Make the plot
    for ix_group, group in enumerate(all_groups):
        if group == 'Humans':
            for sg in range(1,4):
                means = plotting_dict_in[group]['means'][sg]
                stds = plotting_dict_in[group]['std'][sg]
                if sg == 1:
                    # Add the label only for the first super game
                    ax.bar(all_r[sg-1], means,
                        yerr=stds,
                        color=all_colors[ix_group], width=barWidth, edgecolor='white',
                        capsize=1, error_kw={'elinewidth':1}, label=group)
                else:
                    ax.bar(all_r[sg-1], means,
                        yerr=stds,
                        color=all_colors[ix_group], width=barWidth, edgecolor='white',
                        capsize=1, error_kw={'elinewidth':1})

                # Add values to lists
                all_means.extend(means)
                all_stds.extend(stds)
        else:
            # No super games for the algorithms
            means = plotting_dict_in[group]['means']
            stds = plotting_dict_in[group]['std']
            ax.bar(all_r[3], means,
                yerr=stds,
                color=all_colors[ix_group], width=barWidth, edgecolor='white',
                label=group, capsize=1, error_kw={'elinewidth':1})
            # Add values to lists
            all_means.extend(means)
            all_stds.extend(stds)

    ax.set_ylim([0, 5])
    ax.set_ylabel('Mean market price')

    # Create the label (mean price) over the error bar
    rects = ax.patches
    labels = ['%.3f' % elem for elem in all_means]
    distances = all_stds

    label_ticks_pos = []
    for rect, label, distance in zip(rects, labels, distances):
        height = rect.get_height() + distance
        ax.text(rect.get_x() + rect.get_width() / 2, height, label,
                ha='center', va='bottom', fontsize=8)

        # Position for x labels
        label_ticks_pos.append(rect.get_x() + rect.get_width() / 2)

    labels_bars = [
        '2H0A \n (SG 1)',
        '3H0A \n (SG 1)',
        '2H0A \n (SG 2)',
        '3H0A \n (SG 2)',
        '2H0A \n (SG 3)',
        '3H0A \n (SG 3)',
        '0H2A',
        '0H3A']

    ax.set_xticks(label_ticks_pos)
    ax.set_xticklabels(labels_bars)

    # Adding top labels with matplotlib magic numbers
    ax.text(-0.12, 4.7, 'Two firm markets', fontsize=12)
    ax.text(1.56, 4.7, 'Three firm markets', fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=8)

    hatches = ['..', '..','..','..','..','..', '/', '/']

    # Loop over the bars to add hatches
    for i, thisbar in enumerate(rects):
        # Set a different hatch for each bar
        thisbar.set_hatch(hatches[i])

    # Create legend & Show graphic
    ax.legend(loc='lower center', bbox_to_anchor=(0.52, -0.25), ncol=2)
    
    # Turn off xaxis grid
    plt.gca().xaxis.grid(False)
    
    # Save the figure
    fig.savefig(ppj("OUT_FIGURES", "bar_plot_human_v_algos.pdf"),
                bbox_inches='tight', pad_inches = 0)


if __name__ == '__main__':
    # Set some general global plotting parameter
    plt.style.use('seaborn-whitegrid')
    mpl.rc('font', family='serif') 
    mpl.rc('font', serif='Century') 
    plt.rcParams.update({'font.size': 12,
                         'axes.titlesize': 12})    

    # Load the data
    # Two firm algorithm markets
    with open(ppj("OUT_DATA", "super_star_avg_prices_2_agents.pickle"), "rb") as f:
        super_star_avg_prices_2_agents_in = pickle.load(f)

    # Three firm algorithm markets
    with open(ppj("OUT_DATA", "super_star_avg_prices_3_agents.pickle"), "rb") as f:
        super_star_avg_prices_3_agents_in = pickle.load(f)

    # Load the data from the humans
    with open(ppj("OUT_DATA", "data_group_level.pickle"), "rb") as f:
        data_group_level = pickle.load(f)

    # Subset the human data to the last super game and the relevant treatments
    # for this plot.
    data_relevant_treatments= data_group_level.loc[
        (data_group_level['treatment'].isin(['3H0A', '2H0A']))
    ].copy()

    # Aggregate the human data by super_group_id_general which gives us the mean
    # for each independent observation in the last super game
    data_agg_in = data_relevant_treatments.groupby(
        ['super_group_id_general', 'treatment', 'super_game'], as_index=False)[['winning_price']].mean()

    # Create plotting dict
    PLOTTING_DICT = create_value_dict(
        data_agg=data_agg_in,
        super_star_avg_prices_2_agents=super_star_avg_prices_2_agents_in,
        super_star_avg_prices_3_agents=super_star_avg_prices_3_agents_in)
    # Make the plot
    make_human_v_algo_plot(plotting_dict_in=PLOTTING_DICT)
