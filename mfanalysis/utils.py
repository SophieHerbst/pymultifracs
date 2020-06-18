from __future__ import print_function
from __future__ import unicode_literals

import numpy as np


def smart_power(array, exponent):

    # import warnings
    # warnings.filterwarnings("error")

    if exponent == 1:
        return array

    elif exponent == 2:
        return array * array
        # return np.square(array)

    elif exponent == 0.5:
        return np.sqrt(array)

    elif exponent in [-1, 0]:
        return array ** exponent

    elif isinstance(exponent, int) and exponent > 0 and exponent <= 10:

        array_out = np.ones(array.shape)

        for _ in range(exponent):
            array_out *= array

        return array_out

    return np.power(array, exponent)


class Utils:
    def __init__(self):
        pass

    # TODO:Replace with sklearn import ?

    def linear_regression(self, x, y, nj, return_variance=False):
        """
        Performs a (weighted or not) linear regression.
        Finds 'a' that minimizes the error:
            sum_j { n[j]*(y[j] - (a*x[j] + b))**2 }

        Args:
            x, y : regression variables
            nj: list containg the weigths
        Returns:
            a, b: angular coefficient and intercept

        (!!!!!!!!!!!!!)
        IMPORTANT:

        return_variance NOT DEBUGGED
        (!!!!!!!!!!!!!)
        """

        bj = np.array(nj, dtype=np.float)
        assert len(bj) == len(x)

        V_0 = np.sum(bj)
        V_1 = np.sum(bj * x)
        V_2 = np.sum(bj * (x**2))

        weights_slope = bj * (V_0*x - V_1)/(V_0*V_2 - V_1*V_1)
        weights_intercept = bj * (V_2 - V_1*x)/(V_0*V_2 - V_1*V_1)

        a = np.sum(weights_slope*y)
        b = np.sum(weights_intercept*y)

        var_a = np.sum((1/bj)*weights_slope*weights_slope)

        if not return_variance:
            return a, b
        else:
            return a, b, var_a
