#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from tensorflow import keras
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputRegressor
plt.style.use('ggplot')

__all__ = ['PrintDot', 'EnsembleTrees']


class PrintDot(keras.callbacks.Callback):

    """
    Do not take care about this class
    """

    def on_epoch_end(self, epoch):

        """
        do what it has to do
        """

        if epoch % 100 == 0:
            print('')
        print('.', end='')


class EnsembleTrees:

    """
    This module provides all possibilities for using ensemble methods for Machine Learning
    """

    def Regression_Trees(self, XTrain, YTrain, XTest, model, param_grid):

        """

        :param XTrain: a dataframe with the training set
        :param YTrain: a dataframe with the training list of outputs
        :param XTest: a dataframe with the test set
        :param model: a function with the desired model
        :param param_grid: a dictionnary with all the hyperparameters of the model
        :return: a list with the best estimator found and a dataframe with predictions
        """

        if YTrain.shape[1] > 1:

            estimator = GridSearchCV(MultiOutputRegressor(model), param_grid=param_grid)
            estimator = estimator.fit(XTrain, YTrain)
            print("Score = " + str(estimator.score(XTrain, YTrain)))
            best_estimator = estimator.best_estimator_

            predictions = best_estimator.predict(XTest)

        else:
            estimator = GridSearchCV(model, param_grid=param_grid, refit=True, )
            estimator = estimator.fit(XTrain, YTrain)
            print("Score = " + str(estimator.score(XTrain, YTrain)))
            print("Oob error = " + str(1 - estimator.best_estimator_.oob_score_))
            best_estimator = estimator.best_estimator_

            predictions = best_estimator.predict(XTest)

        return best_estimator, pd.DataFrame(predictions, columns=YTrain.columns)