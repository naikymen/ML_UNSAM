#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 15:10:29 2021

@author: rodrigo
"""
import numpy as np
from scipy.linalg import cho_factor, cho_solve


def hat_matrix(X, include_bias=True):
    """
    Compute hat matrix for design matrix X.
    
    :param np.array X: design matrix of dimensions (n x d), 
    where n is the number of observations and d is the number of
    features.
    :param bool include_bias: if True (default), then include a bias column, 
    in design matrix X (i.e. a column of ones - acts as an
    intercept term in a linear model).
    """
    if include_bias:
        X = np.hstack([np.ones([len(X), 1]), X])
    
    A = np.matmul(X.T, X)
    
    LL = cho_factor(A)
    return np.matmul(X, cho_solve(LL, X.T))
