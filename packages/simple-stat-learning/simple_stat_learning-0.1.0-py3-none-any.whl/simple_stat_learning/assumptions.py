from typing import Optional, Tuple, Union

import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
import math

from .models import LinearRegression
from .model_inference import _ModelInferenceBuiltIn


class LinearRegressionAssumptions(_ModelInferenceBuiltIn):
    '''
    Check linear regression assumptions.

    :param model: Fitted LinearRegression instance
    :type model: LinearRegression
    '''
    
    def __init__(self, model: LinearRegression) -> None:
        super().__init__(model)

    def plot_predicted_vs_residuals(self) -> plt.figure:
        '''
        Related to assumption 1: Linearity in data
        Creates a predicted vs residuals plot and returns figure.

        :return: Figure
        :rtype: matplotlib.pyplot.figure
        '''
        return LinearRegressionAssumptions._plot_pred_vs_resid(self.model.fitted_values, 
                                                               self.model.residuals, 
                                                               'Residuals')

    def plot_predicted_vs_observed(self) -> plt.figure:
        '''
        Related to assumption 1: Linearity in data
        Creates a predicted vs observed plot and returns figure.

        :return: Figure
        :rtype: matplotlib.pyplot.figure
        '''
        f, ax = plt.subplots()

        sns.scatterplot(x=self.model.fitted_values,
                        y=self.model._y,
                        ax=ax)

        low = min(np.append(self.model.fitted_values, self.model._y))
        high = max(np.append(self.model.fitted_values, self.model._y))

        # drawing horizontal line indcating linear trend
        # this line will also force matplotlib to make x and y axis equal
        ax.plot((low, high), (low, high), ls="--", c=".3")

        ax.set_xlabel("Predicted values")
        ax.set_ylabel("Observed values")
        ax.set_title('Predicted vs observed')

        return f

    def plot_added_variable_plot(self) -> plt.figure:
        '''
        Related to assumption 1: Linearity in data
        Creates an added variable plot and returns figure.

        :return: Figure
        :rtype: matplotlib.pyplot.figure
        '''
        n_cols = 3
        n_rows = math.ceil(self.model._X.shape[1]/n_cols)

        f, ax = plt.subplots(n_rows, n_cols, figsize=(14, 7))

        model = LinearRegression()

        # resid_1 regress X[-i] on y,
        # residuals contain information about Y not explained by other X's
        for i, x_i in enumerate(self.model._X.T):

            # ax_pos can be Tuple or int
            ax_pos: Union[Tuple[int, int], int]

            #(row, col)
            ax_pos = (i//n_cols, i % n_cols)

            # when only 1 row matplotlib references axes positions as int not tuple (row, col)
            if n_rows < 2:
                ax_pos = ax_pos[1]

            # removing column
            new_X = np.delete(self.model._X, i, axis=1)

            model.fit(new_X, self.model._y)
            resp_vs_other = model.residuals

            model.fit(new_X, x_i)
            x_i_vs_other = model.residuals

            sns.regplot(x=x_i_vs_other,
                        y=resp_vs_other,
                        ax=ax[ax_pos])

            ax[ax_pos].set_xlabel(f'col{i} | Other')
            ax[ax_pos].set_ylabel('Response | Other')

        f.suptitle('Added variable plots')

        return f

    def calculate_durbin_watson_test(self) -> float:
        '''
        Related to assumption 2: Random/i.i.d. sample
        Calculates and returns durbin watson test.

        :return: Durbin watson test statistic
        :rtype: float
        '''
        return np.sum(np.square(np.diff(self.model.residuals, n=1))) / \
               np.sum(np.square(self.model.residuals))

    def calculate_variance_inflation_factor(self) -> np.array:
        '''
        Related to assumption 3: No perfect collinearity
        Calculates and returns variance inflation factor for each predictor in X.

        :return: VIF for each predictor in X
        :rtype: np.array
        '''
        model = LinearRegression()

        inflation_factors = np.zeros(self.model._X.shape[1])

        # used to determine what columns to return,
        # if there's an intercept it will ignore and return every column after
        start = 0
        if all(self.model._X[:, 0] == 1):
            start = 1

        for i, x_i in enumerate(self.model._X.T):

            new_x = np.delete(self.model._X, i, axis=1)
            model.fit(X=new_x, y=x_i)

            vif = 1 / (1 - _ModelInferenceBuiltIn(model)._rsquared)

            inflation_factors[i] = vif

        return inflation_factors[start:]

    def plot_predicted_vs_studentised_residuals(self) -> plt.figure:
        '''
        Related to assumption 5: Homoskedasticity
        Creates a predicted vs studentised residuals plot and returns figure.

        :return: Figure
        :rtype: matplotlib.pyplot.figure
        '''
        return LinearRegressionAssumptions._plot_pred_vs_resid(self.model.fitted_values,
                                                               self._studentised_residuals,
                                                               'Studentised residuals')

    def plot_studentised_histogram(self) -> plt.figure:
        '''
        Related to assumption 6: Normality
        Creates a histogram to show distrobution of studentised residuals

        :return: Figure
        :rtype: matplotlib.pyplot.figure
        '''
        f, ax = plt.subplots()

        sns.distplot(self._studentised_residuals,
                     ax=ax)

        return f

    @staticmethod
    def _plot_pred_vs_resid(predicted: np.array,
                            residuals: np.array,
                            res_label: str) -> plt.figure:
        '''
        Predicted vs residuals/standardised/studentised etc is used often so created as resuable method.

       
        :param predicted: y_hat values
        :type predicted: np.array
        :param residuals: residuals/standardised/studentised
        :type residuals: np.array
        :param res_label: label for residual axis
        :type res_label: str

        :return: Figure
        :rtype: matplotlib.pyplot.figure
        '''
        f, ax = plt.subplots()

        sns.scatterplot(x=predicted,
                        y=residuals,
                        ax=ax)

        # draw horizontal line indcating when prediction correct
        ax.axhline(y=0, ls="--", c=".3")

        ax.set_xlabel("Predicted values")
        ax.set_ylabel(res_label)
        ax.set_title(f'Predicted vs {res_label}')

        return f
