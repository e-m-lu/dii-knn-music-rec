#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import sys
import os
import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans


X_COLS = ['Dancability', 'Energy', 'Valance', 'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness']
Y_COL = 'HR perc'


np.random.seed(19)


def split_train_test(df):
    msk = np.random.rand(len(df)) < 0.5
    train = df[msk]
    test = df[~msk]
    X_train, y_train = train[X_COLS], train[Y_COL]
    X_test, y_test = test[X_COLS], test[Y_COL]
    return X_train, y_train, X_test, y_test


def train_predict(X_train, y_train, X_test, y_test, k=9, weights='uniform'):
    model = KNeighborsClassifier(n_neighbors=k, weights=weights)
    model.fit(X_train, y_train)
    y_hat = model.predict(X_test)
    return y_hat


def run_predict_evaluate(X_train, y_train, X_test, y_test):
    print('Predict and evaluate by KNN')
    accuracy_list = []
    for k in range(1, 41):
        y_hat = train_predict(X_train, y_train, X_test, y_test, k=k)
        accuracy = sum(y_hat == y_test) / float(len(y_hat))
        accuracy_list.append(accuracy)
        print('k=%d accuracy=%.4f' % (k, accuracy))
    print()
    plt.figure()
    plt.plot(range(1, 41), accuracy_list)
    plt.xlabel('k')
    plt.ylabel('Accuracy of prediction')
    plt.title('Evaluation (knn): k from 1 to 40')


def run_elbow(df):
    print('elbow method')
    sse_list = []
    X = df[X_COLS]
    for k in range(1, 41):
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(X)
        sse = kmeans.inertia_
        sse_list.append(sse)
        print('k=%d sse=%.4f' % (k, sse))
    print()
    plt.figure()
    plt.plot(range(2, 41), sse_list[1:])
    plt.xlabel('k')
    plt.ylabel('SSE')
    plt.title('elbow method: k=2 to 40')


def inverse_distance_weighted_vote(distances):
    return [1. / d for d in distances]


def run_inverse_distance_weighted_vote(X_train, y_train, X_test, y_test):
    print('Predict and evaluate by Inverse distance-weighted voting')
    accuracy_list = []
    for k in range(1, 41):
        y_hat = train_predict(X_train, y_train, X_test, y_test, k=k,
                            weights=inverse_distance_weighted_vote)
        accuracy = sum(y_hat == y_test) / float(len(y_hat))
        accuracy_list.append(accuracy)
        print('k=%d accuracy=%.4f' % (k, accuracy))
    """
    print()
    plt.figure()
    plt.plot(range(1, 41), accuracy_list)
    plt.xlabel('k')
    plt.ylabel('Accuracy of prediction')
    plt.title('Evaluation (Inverse distance-weighted voting): k from 1 to 40')
    """


def display_dist_features(df):
    print('Distribution of features of songs liked per HR percentage')
    labels = sorted(df[Y_COL].unique())
    continuous_features = ['Tempo'] + X_COLS
    disrect_features = ['Genre']
    for label in labels:
        df_hrp = df[df[Y_COL]==label]
        for fea in continuous_features:
            print('at %d-%d%%: average %s is %.4f' % (label, label + 10, fea, df_hrp[fea].mean()))
        for fea in disrect_features:
            print('at %d-%d%%: most liked %s is %s' % (label, label + 10, fea, df_hrp[fea].mode()[0]))
    print()


def get_best_k(df):
    accuracy_list = [0] * 40
    N = 100
    for i in range(1, N):
        X_train, y_train, X_test, y_test = split_train_test(df)
        for k in range(1, 41):
            y_hat = train_predict(X_train, y_train, X_test, y_test, k=k,
                                weights=inverse_distance_weighted_vote)
            accuracy = sum(y_hat == y_test) / float(len(y_hat))
            accuracy_list[k-1] += accuracy
    accuracy_list = [acc_sum / N for acc_sum in accuracy_list]
    plt.figure()
    plt.plot(range(1, 41), accuracy_list)
    plt.xlabel('k')
    plt.ylabel('Average accuracy of prediction')
    plt.title('Evaluation (Inverse distance-weighted voting): k from 1 to 40')
    best_k = np.argmax(accuracy_list) + 1
    best_acc = np.max(accuracy_list)
    return best_k, best_acc


def get_best_k_knn(df):
    accuracy_list = [0] * 40
    N = 100
    for i in range(1, N):
        X_train, y_train, X_test, y_test = split_train_test(df)
        for k in range(1, 41):
            y_hat = train_predict(X_train, y_train, X_test, y_test, k=k)
            accuracy = sum(y_hat == y_test) / float(len(y_hat))
            accuracy_list[k-1] += accuracy
    accuracy_list = [acc_sum / N for acc_sum in accuracy_list]
    """
    plt.figure()
    plt.plot(range(1, 41), accuracy_list)
    plt.xlabel('k')
    plt.ylabel('Average accuracy of prediction')
    plt.title('Evaluation (knn): k from 1 to 40')
    best_k = np.argmax(accuracy_list) + 1
    best_acc = np.max(accuracy_list)
    """


def main(data_file):
    """ entry """
    df = pd.read_csv(data_file)
    X_train, y_train, X_test, y_test = split_train_test(df)
    run_predict_evaluate(X_train, y_train, X_test, y_test)
    run_elbow(df)
    run_inverse_distance_weighted_vote(X_train, y_train, X_test, y_test)
    display_dist_features(df)

    #best_k, best_acc = get_best_k_knn(df)
    #print('best accuracy=%.4f when k is %d' % (best_acc, best_k))
    best_k, best_acc = get_best_k(df)
    print('Using Inverse distance-weighted voting, best accuracy=%.4f when k is %d' % (best_acc, best_k))
    plt.show()


if __name__ == '__main__':
    data_file = sys.argv[1]
    main(data_file)
