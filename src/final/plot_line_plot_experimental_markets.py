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


def make_line_plot(agg_level, data_in, all_treatments):
    """
    A function to create a line plot with the market price for each
    treatment by super game and round.

    Args:
        agg_level (string): Only *winning_price" implemented at the moment
        data_in (DataFrame): DataFrame with the group level data from the experiment
        all_treatments (list): List with all treatment indicators
    """

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 10))
    plt.subplots_adjust(wspace=0.02)

    # Hand picked colors
    all_colors = ['#648FFF', '#785EF0', '#DC267F', '#FE6100', '#FFB000']

    # Hand picked markers and dashes
    all_markers = ["v", "s", "P", "X", "d"]
    xmax_by_sg = [25, 17, 11]

    # Make line plots
    for sg in [1, 2, 3]:
        for ix_treatment, treatment in enumerate(all_treatments):
            # For the second super game, add the label and else not
            if sg == 2:
                sns.lineplot(x='round',
                             y=agg_level,
                             data=data_in.loc[(data_in['super_game'] == sg) & (data_in['treatment'] == treatment)],
                             ax=axes[sg - 1],
                             color=all_colors[ix_treatment],
                             ci=None,
                             marker=all_markers[ix_treatment],
                             markersize=9,
                             label=treatment)
            else:
                sns.lineplot(x='round',
                             y=agg_level,
                             data=data_in.loc[(data_in['super_game'] == sg) & (data_in['treatment'] == treatment)],
                             marker=all_markers[ix_treatment],
                             markersize=9,
                             ax=axes[sg - 1],
                             color=all_colors[ix_treatment],
                             ci=None)

        axes[sg - 1].set_xticks([i for i in range(5,
                                xmax_by_sg[sg - 1] + 1, 5)])
        axes[sg - 1].set_xlabel('Round')
        axes[sg - 1].set_ylabel('')
        axes[sg - 1].set_title('Super game {}'.format(sg))

        # Increase xtick label size
        axes[sg - 1].tick_params(axis='both', which='major', labelsize=20)

    # Scale of axis
    for axis_index in range(3):

        axes[axis_index].set_ylim([0, 5.5])
        axes[axis_index].set_yticks(range(0, 6, 1))

        if axis_index != 0:
            axes[axis_index].set_yticklabels([])

        # Add line for monopoly price and stage game nash equilibrium
        axes[axis_index].hlines(
            1,
            xmax=xmax_by_sg[axis_index],
            xmin=1,
            label='Nash equilibrium',
            colors='gray')
        axes[axis_index].hlines(
            4,
            xmax=xmax_by_sg[axis_index],
            xmin=1,
            label='Monopoly price',
            colors='black')

    # Add ylabel
    axes[0].set_ylabel('Mean market price')


    # Add legend
    axes[1].legend(
        loc='lower center', bbox_to_anchor=(
            0.5, -0.36), ncol=3, fontsize=20)


    # Save the figure
    fig.savefig(ppj("OUT_FIGURES", f"line_plot_experiments_{agg_level}.pdf"),
                bbox_inches='tight')


if __name__ == '__main__':
    # Setup for matplotlib

    plt.style.use('seaborn-whitegrid')
    plt.rcParams.update({'font.size': 20})
    rc('text', usetex=True)

    # Load the data
    with open(ppj("OUT_DATA", "data_group_level.pickle"), "rb") as f:
        data_group_level_in = pickle.load(f)

    ALL_TREATMENTS_IN = ['2H0A', '1H1A', '3H0A', '2H1A', '1H2A']

    # TODO: Do the same for agg_level=collusive?
    make_line_plot(agg_level='winning_price',
                   data_in=data_group_level_in,
                   all_treatments=ALL_TREATMENTS_IN)
