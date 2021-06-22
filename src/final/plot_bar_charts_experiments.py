"""

A module to plot the bar chart that compares
the outcomes in the experimental treatments.
"""

import pickle

from matplotlib import rc

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from bld.project_paths import project_paths_join as ppj

def make_bar_plot_experiments(agg_level, data_in, all_treatments):
    """
    A function to create a plot with the mean market price for each
    treatment (super games pooled).

    Args:
        agg_level (string): Either "winning_price" or "collusive"
        data_in (DataFrame): DataFrame with the group level data from the experiment
        all_treatments (list): List with all treatment indicators
    """
    # set width of bar
    barWidth = 0.05
    distance = 0

    # Hand picked colors
    all_colors = ['#648FFF', '#785EF0', '#DC267F', '#FE6100', '#FFB000']

    # Handpick the hatches
    # for each super game
    hatches = ['-', 
                '\\', 
                '+', 
                '|', 
                'X',] 


    fig, ax = plt.subplots(1)
    fig.set_size_inches(12.5, 10.5)


    # Create a plotting dict for ease of use when 
    # acutally plotting.
    plotting_dict = {}

    for treatment in all_treatments:
        plotting_dict[treatment] = {}
        plotting_dict[treatment]['mean'] = list()
        plotting_dict[treatment]['error_bar'] = list()
        plotting_dict[treatment]['mean'].append(
                np.mean(data_in.loc[ (data_in['treatment'] == treatment)][agg_level])
        )
        plotting_dict[treatment]['error_bar'].append(
                    data_in.loc[
                        (data_in['treatment'] == treatment)
                    ].groupby(['super_group_id_general']).mean()[agg_level].sem()
        )


        
    all_r = [np.arange(1) + barWidth*x for x in range(len(all_treatments))] 

    # Make the plot
    for ix_treatment, treatment in enumerate(all_treatments):
        ax.bar(all_r[ix_treatment], plotting_dict[treatment]['mean'],
                yerr=plotting_dict[treatment]['error_bar'],
                color=all_colors[ix_treatment], width=barWidth, edgecolor='white',
                label=treatment, capsize=4)

    # Add xticks on the middle of the group bars
    # plt.xlabel('group', fontweight='bold')
    if agg_level == 'winning_price':
        ax.set_ylim([0,5])
    elif agg_level == 'collusive':
        ax.set_ylim([0,1])

    ax.set_xticks([])
    #     ax.set_xticklabels(['Super game 1', 'Super game 2', 'Super game 3'])

    # Create the label (VOD rate) over the error bar
    rects = ax.patches
    all_means = list(np.array([plotting_dict[treatment]['mean']  for treatment in all_treatments]).flat)
    all_error = list(np.array([plotting_dict[treatment]['error_bar']  for treatment in all_treatments]).flat)
    labels = ['%.3f' % elem for elem in all_means]
    distances = all_error

    for rect, label, distance in zip(rects, labels, distances):
        height = rect.get_height() + distance
        ax.text(rect.get_x() + rect.get_width() / 2, height, label,
                ha='center', va='bottom') #, fontweight='bold'

    # Loop over the bars to add hatches
    for i,thisbar in enumerate(rects):
        # Set a different hatch for each bar
        thisbar.set_hatch(hatches[i])

    # Increase xtick label size
    ax.tick_params(axis='both', which='major', labelsize=20)

    # Create legend & Show graphic
    ax.legend(loc='lower center', bbox_to_anchor =(0.5,-0.2), ncol=3, fontsize=20)
    
    # Save the figure
    fig.savefig(ppj("OUT_FIGURES", f"bar_plot_experiments_{agg_level}.pdf"),
                bbox_inches='tight')


if __name__ == '__main__':
    # Setup for matplotlib
    plt.style.use('seaborn-whitegrid')
    plt.rcParams.update({'font.size': 20})
    rc('text', usetex=True)

    with open(ppj("OUT_DATA", "data_group_level.pickle"), "rb") as f:
        data_group_level_in = pickle.load(f)
    
    ALL_TREATMENTS_IN = ['2H0A', '1H1A', '3H0A', '2H1A', '1H2A' ]

    # TODO: Do the same for agg_level=collusive?
    make_bar_plot_experiments(agg_level='winning_price',
                data_in = data_group_level_in,
                all_treatments=ALL_TREATMENTS_IN)