"""

A set of strategies that are considered for the cluster
analysis.
"""

def always_cooperate(p, p_other_lag, rounder_number):
    """

    Return 1 if price corresponds to cooperation at
    the monopoly price and 0 else.
    """
    return 1 if p == 4 else 0

def always_defect(p, p_other_lag, rounder_number):
    """
    
    Return 1 if price corresponds to defection at
    the stage game Nash equilibrium and 0 else.
    """
    return 1 if p == 1 else 0

def exploit(p, p_other_lag, rounder_number):
    """

    Return 1 if the prices correspond to the price
    cycle used if a player uses the exploit strategy
    and zero else.
    """
    if p == 3 and p_other_lag == 1:
        return 1
    elif p == 1 and p_other_lag == 4:
        return 1
    elif rounder_number == 1 and p == 3:
        return 1
    else:
        return 0

def exploit_at_2(p, p_other_lag, rounder_number):
    """

    Return 1 if the prices correspond to the price
    cycle used if a player uses the exploit2 strategy
    and zero else.
    """
    if p == 2 and p_other_lag == 1:
        return 1
    elif p == 1 and p_other_lag == 4:
        return 1
    elif rounder_number == 1 and p == 2:
        return 1
    else:
        return 0