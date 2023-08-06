from typing import (cast, List, Optional)
from abc import ABC, abstractmethod

import numpy as np

from .preprocessing import add_ones_to_X


class SupervisedModel(ABC):
    '''
    Abstract class for all supervised models to ensure uniform usage
    '''

    @property
    @abstractmethod
    def _X(self) -> np.array:
        # underscore as dont want people setting X outside of fit()
        pass

    @property
    @abstractmethod
    def _y(self) -> np.array:
        # underscore as dont want people setting y outside of fit()
        pass

    @property
    @abstractmethod
    def coefficients(self) -> List[float]:
        '''
        Model coefficients

        :rtype: List
        '''
        pass

    @property
    def fitted_values(self) -> np.array:
        '''
        Y_hat

        :rtype: np.array
        '''
        return self.predict(self._X)

    @property
    def residuals(self) -> np.array:
        '''
        Residuals from fitted values

        :rtype: np.array
        '''
        # residuals are always the difference between y and y_hat
        return self._y - self.fitted_values

    @abstractmethod
    def fit(self,
            X: np.array,
            y: np.array) -> None:
        '''
        Fits model to the X and y data

        :param X: matrix of predictors, columns expected to be predictors and rows observations
        :type X: np.array
        :param y: vector of response variables, 1 column of n rows
        :type y: np.array
        '''
        raise NotImplementedError

    @abstractmethod
    def predict(self, X: np.array) -> np.array:
        '''
        Uses fitted model to predict yhat for new X 

        :param X: new matrix of predictiors
        :type X: np.array 

        :return: predicted y values
        :rtype: np.array
        '''
        raise NotImplementedError


class LinearRegression(SupervisedModel):
    '''
    Class to model Linear Regression
    '''

    @property
    def _X(self) -> np.array:
        return self.__X

    @_X.setter
    def _X(self, value: np.array) -> None:
        # add intercept
        self.__X = add_ones_to_X(value)

    @property
    def _y(self) -> np.array:
        return self.__y

    @_y.setter
    def _y(self, value: np.array) -> None:
        # y can be shape (n, 1) or (n,)
        try:
            assert value.shape[1] == 1
        except IndexError:
            # if error y shape = (n,) which is allowed
            pass
        self.__y = value

    @property
    def coefficients(self) -> List[float]:
        inv_xt_x = np.linalg.inv(np.dot(self._X.T, self._X))
        xt_y = np.dot(self._X.T, self._y)

        coefficients = inv_xt_x.dot(xt_y)

        return cast(List[float], coefficients)

    def fit(self,
            X: np.array,
            y: np.array) -> None:

        assert len(X) == len(y)
        
        self._X = X
        self._y = y

    def predict(self, X: np.array) -> np.array:
        try:
            X = add_ones_to_X(X)

            # must have same number of predictors as fitted X
            assert X.shape[1] == self._X.shape[1]

            return np.dot(X, self.coefficients)

        # thrown when no coefficients 
        except AttributeError:
            raise Exception('Must call fit() before predict()')
