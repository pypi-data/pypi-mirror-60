#!/usr/bin/env python3
# coding: utf-8

import numpy as np
import pandas as pd


def normalizeWeightsVector(w_vec, assets_selected, lower_bound, upper_bound):
    above_the_upper_bound = w_vec > upper_bound
    w_vec[above_the_upper_bound] = upper_bound
    below_the_lower_bound = w_vec < lower_bound
    w_vec[below_the_lower_bound] = lower_bound
    to_redispatch_quantity = 1 - w_vec.sum()
    if to_redispatch_quantity > 0:
        match = np.logical_and(assets_selected.reshape(len(assets_selected), -1), np.logical_not(above_the_upper_bound))
        w_vec[match] += to_redispatch_quantity / match.sum()
    else:
        match = np.logical_and(assets_selected.reshape(len(assets_selected), -1), np.logical_not(below_the_lower_bound))
        w_vec[match] += to_redispatch_quantity / match.sum()
    return w_vec

def process_weights(w=None, df=None, s=None, n=None, low_bound=None, up_bound=None, weight_cutting_rate = 0.7, display=False):
    """ Process weight to respect constraints.
    Parameters
    ----------
    w : array_like
        Matrix of weights.
    df : pd.DataFrame
        Data of returns or prices.
    n, s : int
        Training and testing periods.
    Returns
    -------
    pd.DataFrame
        Dataframe of weight s.t. sum(w) = 1 and 0 <= w_i <= 1.
    """
    T, N = w.shape
    weight_mat = pd.DataFrame(index=df.index, columns=df.columns)

    def cut_process(series):
        # True if less than 50% of obs. are constant
        return series.value_counts(dropna=False).max() < weight_cutting_rate * s

    previousValidWeights = None
    for t in range(n, T, s):
        t_s = min(T, t + s)
        weight_vect = np.zeros([N, 1])
        above_vect = np.zeros([N, 1])
        below_vect = np.zeros([N, 1])

        # check if the past data are constant
        # if asset i is constant set w_i = 0
        test_slice = slice(t,t_s)
        len_test_slice = test_slice.stop - test_slice.start
        sub_X = df.iloc[test_slice, :].copy()
        assets = sub_X.apply(cut_process).values

        weight_vect[assets, 0] = w[test_slice.start][assets]

        # this case might happen if the last activation
        if weight_vect.min()<0:
            weight_vect=weight_vect - weight_vect.min()

        weight_vect = normalizeWeightsVector(weight_vect, assets, low_bound, up_bound)

        counter=0
        while not(weight_vect.max() <= up_bound and weight_vect.min() >= low_bound):
            if counter>50:
                print('renormalizing '+str(counter))
                break
            weight_vect = normalizeWeightsVector(weight_vect,assets,low_bound,up_bound)
            counter=counter+1

        newValidWeights = None

        if abs(weight_vect.sum())  <= 1e-6:
            if previousValidWeights is None:
                newValidWeights = np.ones([len_test_slice, N]) / N
            else :
                newValidWeights = previousValidWeights[:len_test_slice]
        else:
            newValidWeights = np.ones([len_test_slice, 1]) @ weight_vect.T
            previousValidWeights =  newValidWeights

        weight_mat.iloc[test_slice] = newValidWeights

        if display:
            if w[test_slice.start].max() > up_bound or w[test_slice.start].min() < low_bound:
                print('Invalid incoming weights')
            if newValidWeights[0].max()> up_bound or newValidWeights[0].min() < low_bound:
                print('Invalid outgoing weights')
                print(newValidWeights[0].max())
                print(newValidWeights[0].min())
            if abs(newValidWeights[0].sum()-1.) > 1e-6:
                print('Invalid outgoing weights')

            if abs(weight_mat.iloc[t:t_s].sum().sum()) <= 1e-6:
                print('null prediction, investigate')

    return weight_mat


