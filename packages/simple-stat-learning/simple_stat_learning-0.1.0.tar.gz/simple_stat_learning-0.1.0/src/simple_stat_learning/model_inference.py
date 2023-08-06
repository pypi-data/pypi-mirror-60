from typing import (cast, List, Optional, Union)
from abc import ABC, abstractmethod

import numpy as np
from scipy.stats import t, f

from .models import SupervisedModel

class _ModelInferenceBuiltIn:
    '''
    Model inference functions. 

    :param model: fitted instance
    :type model: LinearRegression
    '''

    def __init__(self, model: SupervisedModel) -> None:
        if not hasattr(model, 'coefficients'):
            raise Exception('Model must be fit() prior to inference')

        self.model = model

    @property
    def _sse(self) -> float:
        '''
        Sum of squares error
        '''
        sse = np.dot(self.model.residuals.T, self.model.residuals)
        return cast(float, sse)

    @property
    def _mse(self) -> float:
        '''
        Mean square error
        '''
        n = len(self.model._X)
        p = self.model._X.shape[1]
        df = n - p

        mse = self._sse / df
        return cast(float, mse)

    @property
    def _ssr(self) -> float:
        '''
        Sum of squares regression
        '''
        y_hat = self.model.predict(self.model._X)
        ssr = np.sum(np.square(y_hat - np.mean(self.model._y)))
        return cast(float, ssr)

    @property
    def _msr(self) -> float:
        '''
        Mean square of the regression
        '''
        p = self.model._X.shape[1]
        df = p - 1

        msr = self._ssr / df
        return cast(float, msr)

    @property
    def _coefficients_variance(self) -> List[float]:
        '''
        Variance of the model coefficients
        '''
        X = self.model._X

        inv_xt_x = np.linalg.inv(np.dot(X.T, X))
        var_coef_matrix = np.dot(self._mse, inv_xt_x)

        # variances of our coefficients are located on the diagonal
        var_coef = np.diagonal(var_coef_matrix)
        return cast(List[float], var_coef)

    @property
    def _rsquared(self) -> float:
        '''
        Rsquared for the fitted model
        '''
        return 1 - (self._sse / (self._ssr + self._sse))

    @property
    def _hat_matrix(self) -> np.array:
        '''
        Hat matrix (H)
        '''
        X = self.model._X

        inv_xt_x = np.linalg.inv(np.dot(X.T, X))
        return np.dot(X, np.dot(inv_xt_x, X.T))

    @property
    def _standardised_residuals(self) -> np.array:
        '''
        Standardised residuals
        '''
        H = self._hat_matrix
        return self.model.residuals / np.sqrt(np.dot(self._mse, (1 - np.diagonal(H))))

    @property
    def _studentised_residuals(self) -> np.array:
        '''
        Studentised residuals
        '''
        n = len(self.model._X)
        p = len(self.model.coefficients)
        r = self._standardised_residuals

        sqrt_calculation = np.sqrt((n-p-1) / (n-p-(r * r)))
        return r * sqrt_calculation


class InferenceTest(ABC):
    '''
    Abstract class for T and F tests to ensure uniform usage
    '''

    @abstractmethod
    def calculate_test_statistic(self) -> Union[float, List[float]]:
        raise NotImplementedError

    @abstractmethod
    def get_table_statistic(self,
                            alpha: float = 0.05) -> float:
        raise NotImplementedError


class T_Test(InferenceTest, _ModelInferenceBuiltIn):

    def calculate_test_statistic(self) -> List[float]:
        '''
        Calculates t statistic for each coeficient in the model

        :return: T statistic for each coefficient in model
        :rtype: List
        '''
        t_statistics = self.model.coefficients / \
            np.sqrt(self._coefficients_variance)

        return cast(List[float], t_statistics)

    def get_table_statistic(self,
                            alpha: float = 0.05,
                            two_tailed: bool = True) -> float:
        '''
        Gets T value from T table

        :param alpha: confidence level (default 0.05)
        :type alpha: float
        :param two_tailed: Whether or not distribution two tailed
        :type two_tailed: bool

        :return: T table statistic
        :rtype: float
        '''
        n = len(self.model._X)
        p = self.model._X.shape[1]
        df = n - p

        alpha = 1 - (alpha / (1 + two_tailed))
        return cast(float, t.ppf(alpha, df))


class F_Test(InferenceTest, _ModelInferenceBuiltIn):

    def calculate_test_statistic(self) -> float:
        '''
        Calculates F statistic 

        :return: F statistic
        :rtype: float
        '''
        return self._msr / self._mse

    def get_table_statistic(self,
                            alpha: float = 0.05,) -> float:
        '''
        Gets F value from F table

        :param alpha: confidence level (default 0.05)
        :type alpha: float
        :param two_tailed: boolean for whether or not distribution two tailed
        :type two_tailed: bool

        :return: F table statistic
        :rtype: float
        '''
        n = len(self.model._X)
        p = self.model._X.shape[1]

        return cast(float, f.ppf(alpha, p-1, n-p))
