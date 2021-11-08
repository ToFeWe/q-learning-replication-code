"""

A set of strategies that are considered for the cluster
analysis.
"""

def always_cooperate(p, p_other_lag, p_own_lag, rounder_number):
    """

    Return 1 if price corresponds to cooperation at
    the monopoly price and 0 else.
    """
    return 1 if p == 4 else 0

def always_defect(p, p_other_lag, p_own_lag, rounder_number):
    """
    
    Return 1 if price corresponds to defection at
    the stage game Nash equilibrium and 0 else.
    """
    return 1 if p == 1 else 0

def exploit(p, p_other_lag, p_own_lag, rounder_number):
    """

    Return 1 if the prices correspond to the price
    cycle used if a player uses the exploit strategy
    and zero else.
    """
    # p_other_lag always mirrored for algos
    state = (p_other_lag, p_own_lag)
    if p == 3 and state == (1,1):
        return 1
    elif p == 1 and state == (4,3):
        return 1
    elif p == 3 and state == (4,4):
        return 1
    elif rounder_number == 1 and p == 3:
        return 1
    else:
        return 0

def exploit_at_2(p, p_other_lag, p_own_lag, rounder_number):
    """

    Return 1 if the prices correspond to the price
    cycle used if a player uses the exploit2 strategy
    and zero else.
    """
    state = (p_other_lag, p_own_lag)
    if p == 2 and state == (1,1):
        return 1
    elif p == 1 and state == (4,2):
        return 1
    elif p == 2 and state == (4,4):
        return 1
    elif rounder_number == 1 and p == 2:
        return 1
    else:
        return 0