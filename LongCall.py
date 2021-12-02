from numba import jit
from MonteCarloNumba import monteCarloNumba
import time
from import_bs import blackscholescall
import numpy as np


@jit(nopython=True, cache=True)
def bsm_debit(sim_price, strikes, rate, time_fraction, sigma):
    P_long_calls = blackscholescall(sim_price, strikes[0], rate, time_fraction, sigma)

    credit = P_long_calls
    debit = -credit

    return debit


def longCall(underlying, sigma, rate, trials, days_to_expiration,
             closing_days_array, percentage_array, long_strike, long_price):

    for closing_days in closing_days_array:
        if closing_days > days_to_expiration:
            raise ValueError("Closing days cannot be beyond Days To Expiration.")

    if len(closing_days_array) != len(percentage_array):
        raise ValueError("closing_days_array and percentage_array sizes must be equal.")

    # SIMULATION
    initial_debit = long_price  # Debit paid from opening trade
    initial_credit = -1 * initial_debit

    min_profit = [initial_debit * x for x in percentage_array]

    strikes = [long_strike]

    # LISTS TO NUMPY ARRAYS CUZ NUMBA HATES LISTS
    strikes = np.array(strikes)
    closing_days_array = np.array(closing_days_array)
    min_profit = np.array(min_profit)

    try:
        pop, pop_error, avg_dtc, avg_dtc_error = monteCarloNumba(underlying, rate, sigma, days_to_expiration,
                                                              closing_days_array, trials,
                                                              initial_credit, min_profit, strikes, bsm_debit)
    except RuntimeError as err:
        print(err.args)

    response = {
        "pop": pop,
        "pop_error": pop_error,
        "avg_dtc": avg_dtc,
        "avg_dtc_error": avg_dtc_error
    }

    return response