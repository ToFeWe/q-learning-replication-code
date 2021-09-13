"""

A module to make a line plot to compare
the mean market prices for each cluster (type)
in the last super game for the treatments
1H1A and 1H2A.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

from bld.project_paths import project_paths_join as ppj


def make_line_plot(data_1H1A, data_1H2A, all_types):
    """
    A function to create a line plot of the mean market
    prices by cluster type for the last super game.

    Args:
        data_1H1A (DataFrame): Data for the 1H1A treatment with strategy types
        data_1H2A (DataFrame): Data for the 1H2A treatment with strategy types
        all_types (list): List with strategy type indicators
    """

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(7.7,4.6)) #Different from other figures
    plt.subplots_adjust(wspace=0.02)
    
    # Hand picked colors
    all_colors = sns.color_palette('colorblind')
    
    # all treatments of interest 
    all_treatments = ['1H1A', '1H2A']
    
    # Hand picked markers and dashes
    all_markers = ["v", "s", "P"]
    
    # Make line plots
    for ix_data, data in enumerate([data_1H1A, data_1H2A]):
        for ix_type, current_type in enumerate(all_types):

            # Only add labels to the first axis 
            # as it will be the same for the second one.
            if ix_data == 0:
                sns.lineplot(x='round',
                             y='winning_price',
                             data=data.loc[data['strategy_type'] == current_type],
                             ax=axes[ix_data],
                             color=all_colors[ix_type],
                             ci=None,
                             marker=all_markers[ix_type],
                             markersize=4,
                             label=f"Type {current_type}")
            else:
                sns.lineplot(x='round',
                             y='winning_price',
                             data=data.loc[data['strategy_type'] == current_type],
                             ax=axes[ix_data],
                             color=all_colors[ix_type],
                             ci=None,
                             marker=all_markers[ix_type],
                             markersize=4)


        # Last super game has 11 rounds
        axes[ix_data].set_xticks([i for i in range(5, 11 + 1, 5)])
        axes[ix_data].set_xlabel('Round')
        axes[ix_data].set_ylabel('')
        axes[ix_data].set_title(f'{all_treatments[ix_data]}')

        # xtick label size
        axes[ix_data].tick_params(axis='both', which='major', labelsize=8)


    # Scale of axis
    for axis_index in range(2):
        axes[axis_index].set_ylim([0, 5.5])
        axes[axis_index].set_yticks(range(0, 6, 1))

        if axis_index != 0:
            axes[axis_index].set_yticklabels([])

        # Add line for monopoly price and stage game Nash equilibrium
        axes[axis_index].hlines(
            1,
            xmax=11,
            xmin=1,
            label='Nash equilibrium',
            colors='gray')
        axes[axis_index].hlines(
            4,
            xmax=11,
            xmin=1,
            label='Monopoly price',
            colors='black')

        # Turn off grid
        axes[axis_index].xaxis.grid(False)

    # Add ylabel
    axes[0].set_ylabel('Mean market price')
    
    # Add legend
    axes[0].legend(
        loc='lower center', bbox_to_anchor=(
            1, -0.28), ncol=3, fontsize=12)
     
    # Save the figure
    fig.savefig(ppj("OUT_FIGURES", f"line_plot_type_classification.pdf"),
                bbox_inches='tight', pad_inches = 0)

def _check_n_cluster(data):
    """ Check if the number of clusters is indeed three. """
    n_clusters = len(data['strategy_type'].unique())
    assert n_clusters == 3, f'Script is optimized for three clusters, not {n_clusters} as found in the data.'

if __name__ == '__main__':
    # Set some general global plotting parameter
    plt.style.use('seaborn-whitegrid')
    mpl.rc('font', family='serif') 
    mpl.rc('font', serif='Century') 
    plt.rcParams.update({'font.size': 12,
                         'axes.titlesize': 12})    


    # Load the data
    data_cluster_1H1A_in = pd.read_pickle(ppj('OUT_ANALYSIS', 'data_individual_with_types_1H1A.pickle'))
    data_cluster_1H2A_in = pd.read_pickle(ppj('OUT_ANALYSIS', 'data_individual_with_types_1H2A.pickle'))

    # Clustering has given us three types
    _check_n_cluster(data=data_cluster_1H1A_in)
    _check_n_cluster(data=data_cluster_1H2A_in)
    ALL_TYPES = [0, 1, 2]

    # Make the plot
    make_line_plot(data_1H1A=data_cluster_1H1A_in,
                   data_1H2A=data_cluster_1H2A_in,
                   all_types=ALL_TYPES)