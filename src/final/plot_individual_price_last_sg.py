"""
A module to make a plot with individual prices in the last supergame.
"""
import json
import sys

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

from bld.project_paths import project_paths_join as ppj


def make_plot_two_humans_one_algo(data_for_plot):
    g = sns.FacetGrid(data_for_plot, col="ID", hue="id_in_group", col_wrap=5, height=1.2, aspect=1.1, legend_out=True)
    g.map(sns.lineplot, "round", "price", linestyle='--')
    g.map(sns.lineplot, "round", "price_algorithm", color='grey')

    g.set(ylim=(0, 5), yticks=[0, 1, 2, 3,4,5], xticks=[5, 10])
    g.set_yticklabels(["", "$p^{NE}=1$", "", "", "$p^{M}=4$", ""])
    g.set_xlabels('Round')
    g.set_ylabels('')


    for i_ax, ax in enumerate(g.axes.flatten()):
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.xaxis.grid(False)
        ax.yaxis.grid(False)
        ax.hlines(
            1,
            xmax=11,
            xmin=1,
            linestyle='dotted',
            colors='black')
        ax.hlines(
            4,
            xmax=11,
            xmin=1,
            linestyle='dotted',
            colors='black')
        # Add legend with matplotlib magic
        if i_ax == 0:
            ax.legend(labels=['Human 1', 'Human 2', 'Algorithm'], bbox_to_anchor=(2.65, -7))

    return g

def make_plot_individual_choice(data_for_plot, treatment):

    """
    Make a plot for the last supergame
    with prices on an individual level.

    Returns:
        Facetgrid: Return Facetgrid plot
    """
    g = sns.FacetGrid(data_for_plot, col="ID", col_wrap=5, height=1.2, aspect=1)
    g.map(sns.lineplot, "round", "price", color=sns.color_palette('colorblind')[7], label='Human')
    g.map(sns.lineplot, "round", "price_algorithm", color='#648FFF', label='Algorithm')
    g.set(ylim=(0, 5), yticks=[0, 1, 2, 3,4,5], xticks=[5, 10])
    g.set_yticklabels(["", "$p^{NE}=1$", "", "", "$p^{M}=4$", ""])
    g.set_xlabels('Round')
    g.set_ylabels('')
    for ax in g.axes.flatten():
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.xaxis.grid(False)
        ax.yaxis.grid(False)
        ax.hlines(
            1,
            xmax=11,
            xmin=1,
            linestyle='dotted',
            colors='black')
        ax.hlines(
            4,
            xmax=11,
            xmin=1,
            linestyle='dotted',
            colors='black')
    # Add a legend with some matplotlib magic
    bbox_values = (0.45, 0.14)
    if treatment == '1H1A':
        bbox_values = (0.6, 0.1)
    g.add_legend(bbox_to_anchor=bbox_values)
    return g


if __name__ == '__main__':
    TREATMENT = sys.argv[1]
    LAST_SUPER_GAME = 3

    # Some default styling for the plot
    plt.style.use('seaborn-whitegrid')
    mpl.rc('font', family='serif') 
    mpl.rc('font', serif='Century') 
    plt.rcParams.update({'font.size': 12,
                        'axes.titlesize': 12})    

    # Read the data
    data = pd.read_pickle(ppj("OUT_DATA", "data_individual_level.pickle"))


    ### Make plot for 1H1A and 1H2A ###
    # Factorize participant.code to ID for the plot

    if TREATMENT != "2H1A":
        data_last_sg = data.loc[(data['super_game'] == LAST_SUPER_GAME) &
                                    (data['treatment'] == TREATMENT) ].copy()
        data_last_sg['ID'], _ = pd.factorize(data_last_sg['participant.code'])



        g = make_plot_individual_choice(data_for_plot=data_last_sg, treatment=TREATMENT)
        g.savefig(ppj("OUT_FIGURES", f"individual_prices_last_sg_{TREATMENT}.pdf"),
                    bbox_inches='tight', pad_inches = 0)
    else:
        ### Make plot for 2H1A ###
        data_2H1A = data.loc[
                    (data['super_game']==LAST_SUPER_GAME) &
                    (data['treatment']=='2H1A')
                    ].copy()
        # Factorize group id
        data_2H1A['ID'], _ = pd.factorize(data_2H1A['group_id_general'])
        g = make_plot_two_humans_one_algo(data_for_plot=data_2H1A)
        g.savefig(ppj("OUT_FIGURES", f"individual_prices_last_sg_{TREATMENT}.pdf"),
                    bbox_inches='tight', pad_inches = 0)
