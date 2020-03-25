#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 15:58:11 2020

@author: yifan
"""
import numpy as np
import os
import pandas as pd
from train import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics, preprocessing
import pickle

if __name__== "__main__":
    

    os.chdir('../data/ML/')
    
    # concatenate datasets
    features = ['center_stdev','dist_center_to_border',
                'normal_stdev','sl_f', 'sl_i','sl_max', 'sl_min','t_cong','t_overlap']
    df1 = pd.read_csv('0116_features.csv', usecols = range(9))
    df2 = pd.read_csv('0117_features.csv', usecols = range(9))
    df3 = pd.read_csv('0716_features.csv', usecols = range(9))
    
    frames = [df1, df2, df3]
    
    X_df = pd.concat(frames, ignore_index= True)
    X = X_df.to_numpy()
    X_df.to_csv('X.csv')
    
    df1 = pd.read_csv('0116_label.csv', index_col = None, usecols = [0])
    df2 = pd.read_csv('0117_label.csv', index_col = None, usecols = [0])
    df3 = pd.read_csv('0716_label.csv', index_col = None, usecols = [0])
    
    frames = [df1, df2, df3]
    y_df = pd.concat(frames, ignore_index= True)
    y = y_df.to_numpy()
    y_df.to_csv('y.csv')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=50)
    
    
    rf_clf = RandomForestClassifier(min_impurity_decrease=0.00001,criterion='gini',warm_start=True, n_estimators=10)
    rf_clf.fit(X_train, np.ravel(y_train,order='C'))
    y_pred = rf_clf.predict(X_test)
    y_true = np.ravel(y_test,order='C')
    pre_score = metrics.precision_score(y_true, y_pred, average='weighted')
    acc_score = metrics.accuracy_score(y_true, y_pred)
    print(metrics.classification_report(y_true, y_pred))
    print(pre_score)
    print(acc_score)
    
    filename = 'myModel.sav'
    pickle.dump(rf_clf, open(filename, 'wb'))
     
    
       
        