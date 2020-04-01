#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 11:02:26 2020

@author: yifan
"""

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import precision_score
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import bootstrap


def stratified_k_fold(clf,X,y,k=10):
    # set parameter
    skf = StratifiedKFold(n_splits=k)
    # declare the split dictionaries
    X_train = {}
    X_test = {} 
    y_train = {}
    y_test = {}
    # split the training set into k pairs of training/testing sets for validation
    index = 0
    for train_index, test_index in skf.split(X,y):
        X_train[index], X_test[index] = X[train_index], X[test_index]
        y_train[index], y_test[index] = y[train_index], y[test_index]
        index += 1

    #calculating scores
    scores = []
    for j in range(k):
        clf.fit(X_train[j],y_train[j])
        y_pred = clf.predict(X_test[j])
        y_true = y_test[j]
        score = precision_score(y_true, y_pred, average='weighted')
        scores.append(score)
    print(scores)
    sum = 0
    for single in scores:
        sum += single
    average = sum/k
    return average


def test_logistic(X,y,hyper = 'C'):
    if hyper == 'C':
        Cs = np.linspace(start=0.1,stop=0.8,num=10)
        scores = []
        for c in Cs:
            clf = LogisticRegression(C=c, solver='lbfgs', max_iter=10000)
            scores.append(stratified_k_fold(clf,X,y,k=5))
        plt.plot(Cs,scores)
        plt.grid(True)
        plt.xlabel('Inverse of Regularization Strength')
        plt.ylabel('Average Precision')
        plt.title('Precision of Logistic Regression w.r.t Inverse of Regularization Strength using Stratified 5-fold Cross Validaton')
        plt.show()
    elif hyper == 'tol':
        tols = np.linspace(start=1e-5,stop=1e-2,num=10)
        scores = []
        for t in tols:
            clf = LogisticRegression(tol=t, solver='lbfgs', max_iter=10000)
            scores.append(stratified_k_fold(clf,X,y,k=5))
        plt.plot(tols,scores)
        plt.grid(True)
        plt.xlabel('Tolerance')
        plt.ylabel('Average Precision')
        plt.title('Precision of Logistic Regression w.r.t Tolerance using Stratified 5-fold Cross Validaton')
        plt.show()

def test_decision_tree(X,y,hyper = 'gini'):
    
    decreases = np.linspace(start=1e-4,stop=1e-3,num=10)
    scores = []
    for decrease in decreases:
        clf = DecisionTreeClassifier(criterion=hyper,min_impurity_decrease=decrease)
        scores.append(stratified_k_fold(clf,X,y,k=5))
    plt.plot(decreases,scores)
    plt.grid(True)
    plt.xlabel('Minimum Impurity Decrease')
    plt.ylabel('Average Precision')
    plt.title('Precision of Decision Tree w.r.t Minimum Impurity Decrease under Criterion ' + hyper + ' using Stratified 5-fold Cross Validaton')
    plt.show()

def test_svm(X,y,hyper = 'C'):
    if hyper == 'C':
        Cs = np.linspace(start=0.01,stop=0.05,num=10)
        scores = []
        for c in Cs:
            clf = LinearSVC(C=c, max_iter=100000)
            scores.append(stratified_k_fold(clf,X,y,k=5))
        plt.plot(Cs,scores)
        plt.grid(True)
        plt.xlabel('Inverse of Regularization Strength')
        plt.ylabel('Average Precision')
        plt.title('Precision of Support Vector Machine w.r.t Inverse of Regularization Strength using Stratified 5-fold Cross Validaton')
        plt.show()
    elif hyper == 'tol':
        tols = np.linspace(start=1,stop=1.25,num=10)
        scores = []
        for t in tols:
            clf = LinearSVC(tol=t, max_iter=100000)
            scores.append(stratified_k_fold(clf,X,y,k=5))
        plt.plot(tols,scores)
        plt.grid(True)
        plt.xlabel('Tolerance')
        plt.ylabel('Average Precision')
        plt.title('Precision of Support Vector Machine w.r.t Tolerance using Stratified 5-fold Cross Validaton')
        plt.show()

def test_ada_boost(X,y):
    
    rates = np.linspace(start=0.1,stop=1,num=10)
    scores = []
    for rate in rates:
        clf = AdaBoostClassifier(learning_rate=rate)
        scores.append(stratified_k_fold(clf,X,y,k=5))
    plt.plot(rates,scores)
    plt.grid(True)
    plt.xlabel('Learning Rates')
    plt.ylabel('Average Precision')
    plt.title('Precision of Ada Boost Classifier w.r.t Learning Rates using Stratified 5-fold Cross Validaton')
    plt.show()       
    
def test_random_forest(X,y,hyper = 'gini',warm = True):
    
    decreases = np.linspace(start=0,stop=1e-6,num=10)
    scores = []
    for min_decrease in decreases:
        clf = RandomForestClassifier(min_impurity_decrease=min_decrease,criterion=hyper,warm_start=warm, n_estimators=10)
        scores.append(stratified_k_fold(clf,X,y,k=5))
    plt.plot(decreases,scores)
    plt.grid(True)
    plt.xlabel('Minimum Impurity Decrease')
    plt.ylabel('Average Precision')
    if warm:
        plt.title('Precision of Random Forest Classifier w.r.t Minimum Impurity Decrease under Criterion ' + hyper + 
                  ' with Warm Start using Stratified 5-fold Cross Validaton')
    elif not warm:
        plt.title('Precision of Random Forest Classifier w.r.t Minimum Impurity Decrease under Criterion ' + hyper + 
                  ' without Warm Start using Stratified 5-fold Cross Validaton')
    plt.show()

def test_SGD_classifier(X,y,hyper='optimal'):
    
    tols = np.linspace(start=1e-5,stop=1e-4,num=10)
    scores = []
    for t in tols:
        clf = SGDClassifier(tol=t,learning_rate=hyper,eta0=0.1)
        scores.append(stratified_k_fold(clf,X,y,k=5))
    plt.plot(tols,scores)
    plt.grid(True)
    plt.xlabel('Tolerances')
    plt.ylabel('Average Precision')
    plt.title('Precision of SGD Classifier w.r.t Tolerance with '+hyper+' learning rate using Stratified 5-fold Cross Validaton')
    plt.show()       

if __name__== "__main__":
    

    os.chdir('../data/ML/')
    
    # concatenate datasets
    df1 = pd.read_csv('0116_features.csv', usecols = range(12))
    df2 = pd.read_csv('0117_features.csv', usecols = range(12))
    df3 = pd.read_csv('1028_15_features.csv', usecols = range(12))
    
    frames = [df1, df2, df3]
    
    X_df = pd.concat(frames, ignore_index= True)
    X = X_df.to_numpy()
    X_df.to_csv('X.csv')
    
    df1 = pd.read_csv('0116_label.csv', index_col = None, usecols = [0])
    df2 = pd.read_csv('0117_label.csv', index_col = None, usecols = [0])
    df3 = pd.read_csv('1028_15_label.csv', index_col = None, usecols = [0])
    
    frames = [df1, df2, df3]
    y_df = pd.concat(frames, ignore_index= True)
    y = y_df.to_numpy()
    y_df.to_csv('y.csv')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=50)
    
    ### Hyperparameter tuning
#    test_ada_boost(X_train,np.ravel(y_train,order='C'))
#    test_logistic(X_train,np.ravel(y_train,order='C'),hyper = 'C')
#    test_logistic(X_train,np.ravel(y_train,order='C'),hyper = 'tol')
#    test_decision_tree(X_train,np.ravel(y_train,order='C'))
#    test_svm(X_train,np.ravel(y_train,order='C'),hyper = 'C')
#    test_svm(X_train,np.ravel(y_train,order='C'),hyper = 'tol')
    test_random_forest(X_train,np.ravel(y_train,order='C'))
#    test_SGD_classifier(X_train,np.ravel(y_train,order='C'))
    #
