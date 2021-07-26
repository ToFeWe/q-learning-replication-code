"""

This script is used to create a csv file with the payment information
for the players that used an algorithm during the experiment. The payment
was conduct ex-post as those players did not have to be present during the 
actual online experiments.
"""

from bld.project_paths import project_paths_join as ppj
import numpy as np
import pandas as pd
import pickle
import json



def load_raw_data():
    """
    
    Loads entire data from the experiments.

    Returns:
        DataFrame: Raw data from the experiments
    """
    
    # Load the session info for all experimental sessions
    with open(
        ppj("IN_DATA", f"session_info_experiments.json")
    ) as f:
        SESSION_INFO = json.load(f)

    # Load all sessions data and add them together
    data_list = []
    for session_id, session_info in SESSION_INFO.items():
        current_data = pd.read_csv(ppj("IN_DATA", session_info['path']))
        current_data['session_id'] = session_id
        data_list.append(current_data)
    data_all = pd.concat(data_list)
    return data_all

def get_number_of_participants(data):
    """
    Creates a dictionary of the number of participants per treatment without
    the algorithmic players.

    Args:
        data (DataFrame): DataFrame with the cleaned experimental data

    Returns:
        Dict: Dict with N per treatment
    """
    n_per_treatment = data.loc[(data['super_game'] == 1) &
                               (data['round'] == 1)].groupby(['treatment'])['participant.code'].count().to_dict()

    return n_per_treatment



def get_payment_info_for_algorithms(data, info_dict, conversion_rate, show_up):
    """
    
    Note that for each algorithm within a certain treatment
    the same super game is payoff relevant.

    Args:
        data (DataFrame): DataFrame with the raw experimental data
        info_dict (dict): Dictionary with information how to structure the payoff
                          of the algorithms.
        conversion_rate(int): One Euro in ECU/Taler
        show_up(int): Show up fee in Euro

    Returns:
        DataFrame: Payment data from the experimental treatments with
                   algorithmic involvement.

    """ 
    # Randomly draw the super game that is paid for the three
    # experimental treatments with algorithmic involvement

    SG_PAID = np.random.randint(1,4,3)
        
    # List of all experimental treatments with algorithmic involvement
    TREATMENT_LIST = ['1H1A', '1H2A', '2H1A']

    all_payoffs =  []

    for treatment, paid_sg in zip(TREATMENT_LIST, SG_PAID):
        # Select the payoff information for a given treatment and super game 
        relevant_subset = data.loc[data['bertrand.1.group.group_treatment'] == treatment].copy()

        # Groupby session_id and group id in case we are in the 2H1A treatment
        relevant_payment_data = relevant_subset.groupby(
                                    ['session_id', info_dict['grouping_field_by_sg'][paid_sg]]
                                )[info_dict['relevant_payoff_field_by_sg'][paid_sg]].first().values.flatten()

        if treatment == '1H1A':
            assert len(relevant_subset) == info_dict['algos_to_draw'][treatment]
            all_payoffs.append(relevant_payment_data)
        elif treatment == '1H2A':
            assert len(relevant_subset) == info_dict['algos_to_draw'][treatment] / 2
            # In the 1H2A treatment, each values has to be repeated twice as there are two 
            # identical algos in each market 
            all_payoffs.append(np.repeat(relevant_payment_data, 2))

        elif treatment == '2H1A':
            assert len(relevant_subset) == info_dict['algos_to_draw'][treatment] * 2
            # Here for each group there exists only on algorithm
            # Note that the way how we create the *relevant_payment_data* object
            # already accounts for that.
            all_payoffs.append(relevant_payment_data)

    # Convert ECU/Taler to Euro, add the show up fee and round to second decimal
    all_payoffs_with_show_up_euro = (np.concatenate(all_payoffs) / conversion_rate + show_up).round(2)

    assert all_payoffs_with_show_up_euro.shape[0] == 95, "The number of algorithmic players is not correct."

    return pd.DataFrame(all_payoffs_with_show_up_euro, columns=['payments'])

if __name__ == '__main__':
    # TODO: Maybe refactor this main part here. 
    # Its a little long maybe.
    
    # Todays day as a random seed
    np.random.seed(267)

    CONVERSION_RATE = 130
    SHOW_UP_FEE = 4

    # Define dict with payoff info for the algorithm
    INFO_DICT = {
        'algos_to_draw':
            {
                '1H1A': 32,
                '1H2A': 42,
                '2H1A': 21,
            },
        'relevant_payoff_field_by_sg':
            {
                1: 'bertrand.25.group.accumulated_profit_algorithm',
                2: 'bertrand_SG_2.17.group.accumulated_profit_algorithm',
                3: 'bertrand_SG_3.11.group.accumulated_profit_algorithm'
            },
        'grouping_field_by_sg':
        {
            1: 'bertrand.1.group.id_in_subsession',
            2: 'bertrand_SG_2.1.group.id_in_subsession',
            3: 'bertrand_SG_3.1.group.id_in_subsession',

        }
    }

    # Create and save the dataframe with the payments for the participants 
    # that used an algorithm.
    DATA_RAW = load_raw_data()
    payment_df = get_payment_info_for_algorithms(data = DATA_RAW,
                                                 info_dict = INFO_DICT,
                                                 conversion_rate = CONVERSION_RATE,
                                                 show_up = SHOW_UP_FEE)
    payment_df.to_csv(ppj("OUT_DATA", "data_payment_algorithms.csv"))

    # Also load cleaned individual level data and 
    # create dictionary with other relevant information for the paper
    with open(ppj("OUT_DATA", "data_individual_level.pickle"), "rb") as f:
        data_individual_level = pickle.load(f)
    participants_per_treatment = get_number_of_participants(data_individual_level)

    # Calculate average pays
    average_pay_algos = payment_df['payments'].mean()
    average_pay_humans = (DATA_RAW['participant.payoff'] / CONVERSION_RATE + SHOW_UP_FEE).mean()
    average_pay_total = (average_pay_algos + average_pay_humans) / 2
    
    # Add everything to a dict
    additional_info_results = {
        'participants_per_treatment': participants_per_treatment,
        'average_pay_algos': average_pay_algos,
        'average_pay_humans': average_pay_humans,
        'average_pay_total': average_pay_total
    }

    # Write it to JSON file
    with open(ppj("OUT_DATA", "payment_and_N_info.json"), 'w') as fp:
        json.dump(additional_info_results, fp, indent=4)
