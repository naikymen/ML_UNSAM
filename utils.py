#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 15:10:29 2021

@author: rodrigo
"""
import numpy as np
import scipy.stats as st
from scipy.linalg import cho_factor, cho_solve

from matplotlib import pyplot as plt


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


def anova(t, y_base, y_model, nparam_base, nparam_models):
    """
    Perform simple ANOVA analysis.

    :param np.array t: label array (dimensions (nsamples, 1) or (nsamples,))
    :param np.array y_base: predictions from base model
    (dimensions (nsamples, 1) or (nsamples,))
    :param np.array y_model: predictions from new (more complex) models
    (dimensions (nmodels, nsamples)
    :param int nparam_base: number of parameters of base model
    :param list nparam_models: list with number of parameters of new models
    """
    y_model = np.atleast_2d(y_model)

    print('Model\tdof \tdiferencia \tdof \tF-stat\t p-value')
    print('-----\t--- \t---------- \t--- \t------\t -------')
    print('Base \tN-{:d}'.format(nparam_base))

    for i, [y, npar] in enumerate(zip(y_model, nparam_models)):
        # Compute squared sums
        screg = np.sum((y - y_base)**2) / (npar - nparam_base)
        scres = np.sum((t - y)**2) / (len(t) - npar)

        fratio = screg/scres

        # Define appropiate F distribution
        my_f = st.f(dfn=(npar - nparam_base), dfd=(len(t) - npar))
        pvalue = 1 - my_f.cdf(fratio)

        printdict = {'model': i+1,
                     'npar': npar,
                     'dpar': npar - nparam_base,
                     'fratio': fratio,
                     'pvalue': pvalue
                     }
        # Print line in table
        print('New_{model:d} \tN-{npar:d} \tNew_{model:d} - Base \t{dpar:d} '
              '\t{fratio:.4f}\t{pvalue:.2e}'.format(**printdict))
    return


def plot_clasi(x, t, ws, labels=None, xp=[-1., 1.], thr=[0, ], spines='zero',
               equal=True, margin=None, **kwargs):
    """
    Plot results of linear classification problems.

    :param np.array x: Data matrix
    :param np.array t: Label vector.
    :param list or tuple ws: list with fitted paramter vector of models
                             (excluding bias), one element per model
    :param tuple xp: start and end x-coordinates of decision boundaries and
                     margins.
    :param list or tuple thr: threshold (-bias) values for each model.
    :param str or None spines: whether the spines go through zero. If None,
                               the default behaviour is used.
    :param bool equal: whether to use equal axis aspect (default=True;
                       recomended to see the parameter vector normal to
                       boundary)
    :param None or tuple margin: tupler of booleans that define whether
                                 to plot margin for each model being plotted.
                                 If None, False for all models.
                                 
    Other params
    ------------
    :param bool join_centers: whether to draw lines between classes centres.
    :param bool legend: whether to show the legend.
    """
    assert labels is None or len(labels) == len(ws)
    assert len(ws) == len(thr)
    
    join_centers = kwargs.pop('join_centers', True)
    legend = kwargs.pop('legend', True)
    
    if margin is None:
        margin = [False] * len(ws)
    else:
        margin = np.atleast_1d(margin)
    assert len(margin) == len(ws)

#     if len(labels) == 0:
#         labels = np.arange(len(ws)).astype('str')

    # Agregemos el vector al plot
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111)

    xc1 = x[t == np.unique(t).max()]
    xc2 = x[t == np.unique(t).min()]

    ax.plot(*xc1.T, 'ob', mfc='None', label='C1')
    ax.plot(*xc2.T, 'or', mfc='None', label='C2')

    for i, w in enumerate(ws):

        # Compute vector norm
        wnorm = np.sqrt(np.sum(w**2))

        # ploteo plano perpendicular
        xp = np.array(xp)
        yp = (thr[i] - w[0]*xp)/w[1]

        plt.plot(xp, yp, '-', color='C{}'.format(i+2), **kwargs)

        # Ploteo vector de pesos
        if labels is None:
            ax.quiver(xp.mean(), yp.mean(), w[0]/wnorm, w[1]/wnorm,
                      color='C{}'.format(i+2), scale=10, zorder=10, **kwargs)
        else:
            ax.quiver(xp.mean(), yp.mean(), w[0]/wnorm, w[1]/wnorm,
                      color='C{}'.format(i+2), scale=10, label=labels[i],
                      zorder=10, **kwargs)

        # Plot margin
        if margin[i]:
            for marg in [-1, 1]:
                ym = yp + marg/w[1]
                plt.plot(xp, ym, ':', color='C{}'.format(i+2))

    if join_centers:
        # Ploteo línea que une centros de los conjuntos
        mu1 = xc1.mean(axis=0)
        mu2 = xc2.mean(axis=0)
        ax.plot([mu1[0], mu2[0]], [mu1[1], mu2[1]], 'o:k', mfc='None', ms=10)

    if legend:
        ax.legend(loc=0, fontsize=12)
    
    if equal:
        ax.set_aspect('equal')

    if spines is not None:
        for a in ['left', 'bottom']:
            ax.spines[a].set_position('zero')
        for a in ['top', 'right']:
            ax.spines[a].set_visible(False)

    return


def makew(fitter, norm=False):
    """
    Prepare parameter vector for an sklearn.liner_model predictor.

    :param sklearn.LinearModel fitter: the model used to classify the data
    :param bool norm: default: False; whether to normalize the parameter vector
    """
    # # Obtengamos los pesos
    w = fitter.coef_.copy()

    # # Incluye intercept
    if fitter.fit_intercept:
        w = np.hstack([fitter.intercept_.reshape(1, 1), w])

    # # Normalizon
    if norm:
        w /= np.linalg.norm(w)
    return w.T


def plot_svm(svc, x, t, colorbar=False, **kwargs):
    
    plt.figure(figsize=(9, 7))

    xx, yy = np.meshgrid(np.linspace(x[:, 0].min()-1, x[:, 0].max()+1, 200), 
                         np.linspace(x[:, 1].min()-1, x[:, 1].max()+1, 200))

    # evaluate decision function
    Z = svc.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # veamos la función de decisión y la frontera de decisión
    pcm = plt.pcolormesh(xx, yy, -Z, cmap=plt.cm.RdBu_r, 
                         shading='auto', **kwargs)

    if colorbar:
        plt.colorbar(label='Decision function')

    plt.contour(xx, yy, -Z, 0, colors='0.25', zorder=1)
    plt.contour(xx, yy, -Z, [-1, 1], colors='0.25', linestyles='dashed', zorder=1)

    xc1 = x[t == np.unique(t.flatten()).max()]
    xc2 = x[t == np.unique(t.flatten()).min()]

    plt.plot(*xc1.T, 'ob', mfc='None', label='C1')
    plt.plot(*xc2.T, 'or', mfc='None', label='C2')

    # Get suppor vector
    xsv = svc.support_vectors_
    plt.plot(xsv[:, 0], xsv[:, 1], 'o', ms=12, mfc='None', mec='k', mew=2)

        
    plt.xticks(())
    plt.yticks(())
    plt.axis('tight')
    
    return