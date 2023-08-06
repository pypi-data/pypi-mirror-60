#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
plt.style.use('ggplot')

__all__ = ['Management']


class Management:

    """
    This class provides several functions for manage your dataframes. More preciasly in the case where data are not well
    reported. You can use them through different python dataframes.
    """

    def Import(self, path, head, sep):

        """

        :param path: a string with the path of the dataset
        :param head: a string if the data are already in a classic type with header : "Classic". Otherwise : "Other"
        :param sep: a string with the  type of separator for data
        :return: a pandas dataframe
        """

        if ".csv" in path:

            X = pd.read_csv(path, sep=sep)

            if head != "Classic":
                X.columns = X.iloc[0, :]
                X = X.drop(index=0)
                return X
            else:
                return X

        elif ".xlsx" in path:

            X = pd.read_excel(path, sep=sep)

            if head != "Classic":

                X.columns = X.iloc[0, :]
                X = X.drop(index=0)
                return X

            else:
                return X

        elif ".txt" in path:

            X = pd.read_csv(path, sep=sep)

            if head != "Classic":

                X.columns = X.iloc[0, :]
                X = X.drop(index=0)
                return X

            else:
                return X

    def Split(self, Columns, X, ratio):

        """

        :param Columns: a list of string containing all features to predict
        :param X: a dataframe
        :param ratio: a float between 0 and 1 for splitting train/test
        :return: 4 dataframes with training and test sets
        """

        Train, Test = train_test_split(X, train_size=ratio)

        XTrain = Train.drop(columns=Columns)
        XTest = Test.drop(columns=Columns)
        YTrain = Train[Columns]
        YTest = Test[Columns]

        return XTrain, YTrain, XTest, YTest

    def Oversamplling(self, X, feature):

        """

        :param X: a unbalanced dataframe
        :param feature: a string with the name of the feature where the oversampling has to be done
        :return: a balanced dataframe for the feature corresponding
        """

        liste = list(X[feature].unique())
        over = X[feature].value_counts(normalize=False).index[0]
        label_0 = X[X[feature] == over]
        liste.remove(int(over))

        taille = label_0.shape[0]
        new_0 = label_0.sample(n=taille, replace=False)

        for i in liste:
            label_1_1 = X[X[feature] == i]
            new_1_1 = label_1_1
            new_1_2 = label_1_1.sample(n=(taille - label_1_1.shape[0]), replace=True)
            new_1 = pd.concat([new_1_1, new_1_2], ignore_index=True)
            new_0 = pd.concat([new_0, new_1], ignore_index=True)

        return new_0.sample(n=new_0.shape[0], replace=False)

    def OrderBy(self, X, feature1, feature2):

        """

        :param X: a dataframe
        :param feature1: a string with the name of the future plotted feature
        :param feature2: a string with the name of the feature with which you order
        :return: a dataframe ordered by feature2
        """

        return X.sort_values(by=feature2)