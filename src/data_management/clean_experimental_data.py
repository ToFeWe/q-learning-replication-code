"""

A module to clean the data from the experiments with humans.
"""

import pandas as pd
import numpy as np
import json

from bld.project_paths import project_paths as pp
from bld.project_paths import project_paths_join as ppj

from src.data_management.utils_experimental_data import app_to_sg
from src.data_management.utils_experimental_data import split_column
from src.data_management.utils_experimental_data import merge_new_column
from src.data_management.utils_experimental_data import merge_new_column_non_repeating
from src.data_management.utils_experimental_data import add_super_group_id
from src.data_management.utils_experimental_data import check_if_collusive


def clean_session(session_data, super_group_ids, data_identifier):
    """

    Main function to clean the data that from the experiments. This function expects one
    experiment session at a time. We merge them together in a later step.
    """

    # Get all variable names for melt command
    # *participant.code* is used as an identifier and thus removed here.
    val_vars = list(session_data)
    val_vars.remove('participant.code')

    # Melt data to get it in long format
    data_long = pd.melt(frame=session_data,
                        id_vars=['participant.code'],
                        value_vars=val_vars,
                        value_name='value',
                        var_name='variable_long')

    # Split the long variable names as they have been saved by otree
    data_long['app'], data_long['round'], data_long['otree_object'], data_long['variable'] = zip(
        *data_long['variable_long'].apply(lambda x: split_column(x)))
    data_long = data_long[['participant.code', 'app',
                           'round', 'variable', 'otree_object', 'value']].copy()

    # Get the super game indicator
    data_long['super_game'] = data_long['app'].transform(
        lambda x: app_to_sg(x))

    # Round is float given it is missing for some due to how otree works
    data_long['round'] = data_long['round'].astype(float)

    # We only need the group and player objects from otree
    data_long = data_long.loc[data_long['otree_object'].isin(
        ['group', 'player'])].copy()

    # Add the super game (App) specific group ID
    group_id_df = data_long.loc[data_long['variable'] == 'id_in_subsession'][[
        'participant.code', 'app', 'value']].copy()
    group_id_df.rename({'value': 'group_id'}, inplace=True, axis=1)
    group_id_df = group_id_df.drop_duplicates().copy()
    data_long = data_long.merge(
        group_id_df, how='left', on=[
            'participant.code', 'app'])

    # Get the round specific data for each super game
    # Note that the maximal round number  for each super game is hardcoded.
    LENGTH_FIRST_SUPER_GAME = 25
    LENGTH_SECOND_SUPER_GAME = 17
    LENGTH_THIRD_SUPER_GAME = 11
    data_round_specific = data_long.loc[((data_long['app'] == 'bertrand') &
                                         (data_long['round'] <= LENGTH_FIRST_SUPER_GAME))
                                        |
                                        ((data_long['app'] == 'bertrand_SG_2') &
                                         (data_long['round'] <= LENGTH_SECOND_SUPER_GAME))
                                        |
                                        ((data_long['app'] == 'bertrand_SG_3') &
                                         (data_long['round'] <= LENGTH_THIRD_SUPER_GAME))
                                        ].copy()

    # Create a DataFrame which we will merge other variables onto
    data_merge_on = data_round_specific[[
        'participant.code', 'round', 'super_game', 'group_id']].drop_duplicates().copy()

    # Add some round specific values as columns
    for var in ['winning_price', 'price', 'price_algorithm', 'id_in_group']:
        data_merge_on = merge_new_column(data_merge_on=data_merge_on,
                                         data_merge_from=data_round_specific,
                                         var_name=var)
        data_merge_on[var] = data_merge_on[var].astype(float)

    # Add the data identifier
    # This will usually be the session date/time as the dict in key in the session data
    # that is being supplied to the function.
    data_merge_on['data_identifier'] = data_identifier

    # Add treatment indicator
    data_merge_on = merge_new_column_non_repeating(
        data_merge_on=data_merge_on, data_merge_from=session_data,
        var_name='introduction.1.group.group_treatment')
    data_merge_on.rename(
        {'introduction.1.group.group_treatment': 'treatment'},
        inplace=True, axis=1)

    # Add the super group id based on the group id
    data_merge_on['super_group_id'] = data_merge_on.apply(
        lambda x: add_super_group_id(
            individual_group_id=x['group_id'],
            super_group_ids=super_group_ids,
            treatment=x['treatment']),
        axis=1)

    # Get the size of the set of unique prices
    data_merge_on['unique_prices_humans'] = data_merge_on.groupby(
        ['group_id', 'super_game', 'round']).transform('nunique')['price']

    # Indicators if the market was collusive
    # We say that a market was collusive in a given round if all prices were the same
    # and above the stage game NE.
    data_merge_on['collusive'] = check_if_collusive(
        data_merge_on=data_merge_on)

    # Add group/super group identifier which is unique across session
    # This will be used for clustering to identify independent observations.
    data_merge_on['super_group_id_general'] = data_merge_on['data_identifier'] + \
        '_' + data_merge_on['super_group_id'].astype('str')
    data_merge_on['group_id_general'] = data_merge_on['data_identifier'] + \
        '_' + data_merge_on['group_id'].astype('str')
    
    # Sort the data
    data_merge_on.sort_values(['super_game','round', 'group_id', 'super_group_id_general'], ascending=True, inplace=True)

    # Create lagged variables
    for ix_lag in range(5):
        data_merge_on['winning_price_lag_{}'.format(ix_lag)] = data_merge_on.groupby(
            ['super_game', 'group_id', 'participant.code'])['winning_price'].shift(ix_lag)
        data_merge_on['price_lag_{}'.format(ix_lag)] = data_merge_on.groupby(
            ['super_game', 'group_id', 'participant.code'])['price'].shift(ix_lag)
        data_merge_on['price_algorithm_{}'.format(ix_lag)] = data_merge_on.groupby(
            ['super_game', 'group_id', 'participant.code'])['price_algorithm'].shift(ix_lag)

    # Round indicator across super games
    # This variable can be used for fixed effects in order to include super game
    # and round effects.
    data_merge_on['r_sg'] = data_merge_on['round'].astype(
        str) + data_merge_on['super_game'].astype(str)
    labels, _ = pd.factorize(data_merge_on['r_sg'])
    data_merge_on['r_sg'] = labels

    return data_merge_on.copy()


if __name__ == '__main__':
    with open(
        ppj("IN_DATA", f"session_info_experiments.json")
    ) as f:
        SESSION_INFO = json.load(f)

    # Super groups indicator mapped into the group IDs in oTree data
    SUPER_GROUP_IDS = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }

    data_list = []
    for session_id, session_info in SESSION_INFO.items():
        current_data = pd.read_csv(ppj("IN_DATA", session_info['path']))
        current_data_clean = clean_session(session_data=current_data,
                                           super_group_ids=SUPER_GROUP_IDS,
                                           data_identifier=session_id)
        data_list.append(current_data_clean)
    data_all = pd.concat(data_list)

    # Reset index 
    data_all.reset_index(inplace=True)

    # Save individual level data
    data_all.to_pickle(ppj("OUT_DATA", "data_individual_level.pickle"))
    data_all.reset_index().to_feather(ppj("OUT_DATA", "data_individual_level.feather"))
    data_all.to_csv(ppj("OUT_DATA", "data_individual_level.csv"))

    # Save group level data
    data_group_level = data_all.drop_duplicates(
        subset=[
            'round',
            'super_game',
            'group_id_general',
            'treatment']).copy()
    data_group_level = data_group_level[['round',
                                         'super_game',
                                         'r_sg',
                                         'group_id_general',
                                         'treatment',
                                         'winning_price',
                                         'collusive',
                                         'super_group_id_general',
                                         'price_algorithm']]

    # Reset index
    data_group_level.reset_index(inplace=True)

    data_group_level.to_pickle(ppj("OUT_DATA", "data_group_level.pickle"))
    data_group_level.reset_index().to_feather(
        ppj("OUT_DATA", "data_group_level.feather"))
    data_group_level.to_csv(ppj("OUT_DATA", "data_group_level.csv"))
