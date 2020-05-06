#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 17:52:15 2020

@author: yifan
"""
# code adapted from : https://scikit-learn.org/stable/auto_examples/model_selection/plot_randomized_search.html

from time import time
import scipy.stats as stats
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score,accuracy_score,precision_score,classification_report
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle


# Utility function to report best scores
def report(results, n_top=3):
    for i in range(1, n_top + 1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model with rank: {0}".format(i))
            print("Mean validation score: {0:.3f} (std: {1:.3f})"
                  .format(results['mean_test_score'][candidate],
                          results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            print("")


# get some data
os.chdir('../data/ML/large/')
X = pd.read_csv('X.csv',index_col=0)
y = pd.read_csv('y.csv',index_col=0)
X = X.to_numpy()
y = y.to_numpy()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=12)
    

# build a classifier
clf = RandomForestClassifier(criterion='gini')


## use a full grid over all parameters
#param_grid = {'min_impurity_decrease': np.linspace(0, 0.001, num=100),
#              'n_estimators': [10,15,20,25,30],
#              'warm_start':[True,False]}
#
## run grid search
#grid_search = GridSearchCV(clf, param_grid=param_grid,cv=10,scoring='f1')
#start = time()
#grid_search.fit(X_train, y_train.ravel())
#
#print("GridSearchCV took %.2f seconds for %d candidate parameter settings."
#      % (time() - start, len(grid_search.cv_results_['params'])))
#report(grid_search.cv_results_)
#


#GridSearchCV took 5359.48 seconds for 1000 candidate parameter settings.
#Model with rank: 1
#Mean validation score: 0.919 (std: 0.040)
#Parameters: {'min_impurity_decrease': 0.0, 'n_estimators': 25, 'warm_start': False}
#
#Model with rank: 2
#Mean validation score: 0.919 (std: 0.035)
#Parameters: {'min_impurity_decrease': 0.0, 'n_estimators': 15, 'warm_start': False}
#
#Model with rank: 3
#Mean validation score: 0.918 (std: 0.047)
#Parameters: {'min_impurity_decrease': 0.0, 'n_estimators': 30, 'warm_start': True}
##
final_clf = RandomForestClassifier(min_impurity_decrease=0.0,criterion='gini',warm_start=False, n_estimators=25)
final_clf.fit(X_train, np.ravel(y_train,order='C'))
y_pred = final_clf.predict(X_test)
y_true = np.ravel(y_test,order='C')
pre_score = precision_score(y_true, y_pred, average='weighted')
acc_score = accuracy_score(y_true, y_pred)
f1_score = f1_score(y_true,y_pred)
print(classification_report(y_true, y_pred))
print(pre_score)
print(acc_score)
print(f1_score)
    
filename = 'myModel.sav'
pickle.dump(final_clf, open(filename, 'wb'))