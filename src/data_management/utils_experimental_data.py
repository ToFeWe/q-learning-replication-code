"""

A collection of function that are used for data cleaning.
"""

import numpy as np
import pandas as pd

def split_column(x):
    """
    Splits the long name column in
    
    App, round, otree_object, variable
    """
    name_parts = x.split('.')
    
    # Session and participant parts in the otree database are not
    # app or round specific-
    if name_parts[0] == 'session' or name_parts[0] == 'participant':
        return [np.nan, np.nan, name_parts[0], name_parts[1]]
    else:
        return name_parts
    
def app_to_sg(x):
    """
    A helper function to transform an app name to a super game indicator.
    """
    
    if x == 'bertrand':
        return 1
    elif x == 'bertrand_SG_2':
        return 2
    elif x == 'bertrand_SG_3':
        return 3
    else:
        return np.nan
    
def make_data_column_long(data_in, var_name):
    """
    
    Takes a specfic variable from the raw oTree data
    and takes the subset of this data for each participant
    round and super game.
    """
    data_out = data_in.loc[data_in['variable'] == var_name][['participant.code', 'round', 'super_game', 'value']].copy()
    data_out.rename({'value': var_name}, inplace=True, axis=1)
    return data_out

def merge_new_column(data_merge_on, data_merge_from, var_name):
    """
    
    A function that looks for the variable *var_name* in the raw otree dataframe 
    *data_merge_from* and merges it to the dataframe *data_merge_on* in the long format.
    
    This function is used for variables that are repeated across rounds and super games.
    """

    # Create the new dataframe from the split-up but raw otree data
    # Note that this dataframe includes the columns
    # participant.code, round, super_game and var_name.
    data_new_column = make_data_column_long(data_in = data_merge_from,
                                            var_name = var_name)
    
    # Merge the new column to the clean data frame
    data_out = data_merge_on.merge(data_new_column, how= 'left', on=['participant.code', 'round', 'super_game'])
    return data_out.copy()


def add_super_group_id(individual_group_id, super_group_ids, treatment):
    """
    
    Add the super group id based on the *super_group_ids* dict and the
    treatment.
    """
    
    # If there was no direct interaction with a human participant
    # the super group id is simply the group id.
    # Note that this group id does not change by player for different super
    # games if there is only 'idividual' choice.
    if treatment in ['1H1A', '1H2A']:
        return individual_group_id
    else:
        for sg_id, group_ids in super_group_ids.items():
            if individual_group_id in group_ids:
                return sg_id
        
def merge_new_column_non_repeating(data_merge_on, data_merge_from, var_name):
    """
    
    Create a new column with a measure that is not repeating accross rounds.
    For instance, the treatment or survey measures.
    """
    data_new_column = data_merge_from[['participant.code', var_name]].copy()
    data_out = data_merge_on.merge(data_new_column, how='left', on=['participant.code'])
    return data_out.copy()

def check_if_collusive(data_merge_on):
    """
    
    Returns true if the market was collusive.
    """
    # Check if we have an algorithm in the group
    # if so we have to take it into account.
    # TODO: Not it assumes that there is one treatment per session
    # Change this if it is not like this anymore.
    treatment = data_merge_on['treatment'].unique()
    if treatment in ['1H1A', '1H2A', '2H1A']:
        # In algorithm treatments, we also have to check if the price of the algorithm
        # is equal to the price of the human.
        series_collusion = np.where((data_merge_on['unique_prices_humans'] == 1) &
                                              (data_merge_on['price'] == data_merge_on['price_algorithm']) &
                                              (data_merge_on['winning_price'] > 1),
                                              1, 0)
    else:    
        series_collusion = np.where((data_merge_on['unique_prices_humans'] == 1) &
                                              (data_merge_on['winning_price'] > 1),
                                              1, 0)
    return series_collusion