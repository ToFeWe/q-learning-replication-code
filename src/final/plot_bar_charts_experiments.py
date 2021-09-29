"""

A module to plot the bar chart that compares
the outcomes in the experimental treatments.
"""

import pickle

import matplotlib as mpl

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from bld.project_paths import project_paths_join as ppj

def make_bar_plot_experiments(agg_level, data_exp_in, super_star_prices_2_firm, super_star_prices_3_firm,  all_treatments):
    """
    A function to create a plot with the mean market price for each
    treatment (super games pooled).

    Args:
        agg_level (string): Either "winning_price" or "collusive"
        data_exp_in (DataFrame): DataFrame with the group level data from the experiment
        # TODO: Add doc
        all_treatments (list): List with all treatment indicators
    """
    # set width of bar
    barWidth = 0.35
    distance = 0

    # Hand picked colors
    all_colors = ['#648FFF', '#785EF0', '#723BFA', '#DC267F', '#FE6100', '#FFB000', '#F58453']

    # Handpick the hatches
    # for each super game
    hatches = ['-', 
                '\\',
                '//',
                '+', 
                '|', 
                'X',
                '--'] 


    fig, ax = plt.subplots(figsize=(5,3.6))


    # Create a plotting dict for ease of use when 
    # acutally plotting.
    plotting_dict = {}

    for treatment in all_treatments:
        plotting_dict[treatment] = {}
        plotting_dict[treatment]['mean'] = list()
        plotting_dict[treatment]['error_bar'] = list()

        if treatment not in ['0H2A', '0H3A']:
            plotting_dict[treatment]['mean'].append(
                    np.mean(data_exp_in.loc[ (data_exp_in['treatment'] == treatment)][agg_level])
            )
            plotting_dict[treatment]['error_bar'].append(
                        data_exp_in.loc[
                            (data_exp_in['treatment'] == treatment)
                        ].groupby(['super_group_id_general']).mean()[agg_level].std()
            )
        elif treatment == '0H2A':
            plotting_dict[treatment]['mean'].append(super_star_prices_2_firm.mean())
            plotting_dict[treatment]['error_bar'].append(super_star_prices_2_firm.std())
        elif treatment == '0H3A':
            plotting_dict[treatment]['mean'].append(super_star_prices_3_firm.mean())
            plotting_dict[treatment]['error_bar'].append(super_star_prices_3_firm.std())

    # Change the position of the bars with some magic
    all_r = []
    for x in range(len(all_treatments)):
        new_r = np.arange(1) + barWidth*x
        
        if x == 3:
            new_r = np.arange(1) + barWidth*x + barWidth /2
        elif x > 3:
            new_r = all_r[x-1] + barWidth
        all_r.append(new_r)

    # Make the plot
    for ix_treatment, treatment in enumerate(all_treatments):
        ax.bar(all_r[ix_treatment], plotting_dict[treatment]['mean'],
                yerr=plotting_dict[treatment]['error_bar'],
                color=all_colors[ix_treatment], width=barWidth, edgecolor='white',
                label=treatment, capsize=1, error_kw={'elinewidth':1})

    # Add xticks on the middle of the group bars
    if agg_level == 'winning_price':
        ax.set_ylim([0,5])
        ax.set_yticks([0,1,2,3,4,5])
        ax.set_yticklabels([0,"$p^{NE}=$1",2,3,"$p^{M}=$4",5])
    elif agg_level == 'collusive':
        ax.set_ylim([0,1])

    ax.set_xticks([])
    ax.set_ylabel('Mean market price')

    # Create the label (VOD rate) over the error bar
    rects = ax.patches
    all_means = list(np.array([plotting_dict[treatment]['mean']  for treatment in all_treatments]).flat)
    all_error = list(np.array([plotting_dict[treatment]['error_bar']  for treatment in all_treatments]).flat)
    labels = ['%.3f' % elem for elem in all_means]
    distances = all_error

    label_ticks_pos = []

    for rect, label, distance in zip(rects, labels, distances):
        height = rect.get_height() + distance
        ax.text(rect.get_x() + rect.get_width() / 2, height, label,
                ha='center', va='bottom', fontsize=8) 
        # Position for x labels
        label_ticks_pos.append(rect.get_x() + rect.get_width() / 2)

    # Loop over the bars to add hatches
    for i,thisbar in enumerate(rects):
        # Set a different hatch for each bar
        thisbar.set_hatch(hatches[i])
    
    # Make labels as xticks
    labels_bars = all_treatments
    ax.set_xticks(label_ticks_pos)
    ax.set_xticklabels(labels_bars)

    # xtick label size
    ax.tick_params(axis='both', which='major', labelsize=8)

    # Adding top labels with matplotlib magic numbers
    ax.text(-0.2, 4.7, 'Two firm markets', fontsize=12)
    ax.text(1.2, 4.7, 'Three firm markets', fontsize=12)

    # Turn off xaxis grid
    plt.gca().xaxis.grid(False)

    # Save the figure
    fig.savefig(ppj("OUT_FIGURES", f"bar_plot_experiments_{agg_level}.pdf"),
                bbox_inches='tight', pad_inches = 0)


if __name__ == '__main__':
    # Set some general global plotting parameter
    plt.style.use('seaborn-whitegrid')
    mpl.rc('font', family='serif') 
    mpl.rc('font', serif='Century') 
    plt.rcParams.update({'font.size': 12,
                         'axes.titlesize': 12})    

    with open(ppj("OUT_DATA", "data_group_level.pickle"), "rb") as f:
        data_group_level_in = pickle.load(f)
    
    # Load super star algorithmic data
    with open(ppj("OUT_DATA", "super_star_avg_prices_2_agents.pickle"), "rb") as f:
        super_star_avg_prices_2_agents = pickle.load(f)
    with open(ppj("OUT_DATA", "super_star_avg_prices_3_agents.pickle"), "rb") as f:
        super_star_avg_prices_3_agents = pickle.load(f)

 
    ALL_TREATMENTS_IN = ['2H0A', '1H1A', '0H2A', '3H0A', '2H1A', '1H2A', '0H3A']

    make_bar_plot_experiments(agg_level='winning_price',
                              data_exp_in = data_group_level_in,
                              super_star_prices_2_firm=super_star_avg_prices_2_agents,
                              super_star_prices_3_firm=super_star_avg_prices_3_agents,
                              all_treatments=ALL_TREATMENTS_IN)