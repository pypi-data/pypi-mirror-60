import numpy as np

'''
Any functions relating to the pre processing of data 
'''

def add_ones_to_X(X: np.ndarray) -> np.ndarray:
    """
    Checks if the first column in X is all ones (needed to calculate the intercept). 
    If not adds all ones as the first column

    :param X: matrix of predictors
    :type X: np.array

    :return: matrix of predictors with 1 extra column if first column didn't contain ones
    :rtype: np.array
    """
    if all(X[:, 0] != 1):
        n = len(X)
        ones = np.ones((n, 1))
        X = np.append(ones, X, axis=1)

    return X
