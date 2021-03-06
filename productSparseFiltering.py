"""
==================
 Sparse filtering
==================

Python port of the sparse filtering matlab code by Jiquan Ngiam.

Requires numpy and scipy installed.
"""
import numpy as np
from scipy.optimize import minimize


def l2row(X):
    """
    L2 normalize X by rows. We also use this to normalize by column with l2row(X.T)
    """
    N = np.sqrt((X**2).sum(axis=1)+1e-8)
    Y = (X.T/N).T
    return Y, N


def l2rowg(X, Y, N, D):
    """
    Backpropagate through Normalization.

    Parameters
    ----------

    X = Raw (possibly centered) data.
    Y = Row normalized data.
    N = Norms of rows.
    D = Deltas of previous layer. Used to compute gradient.

    Returns
    -------

    L2 normalized gradient.
    """
    return (D.T/N - Y.T * (D*X).sum(axis=1) / N**2).T


def sparseProductFiltering(N, X, Y):
    "N = # features, X = input data (examples in column)"
    optW = np.random.randn(N, X.shape[0] + Y.shape[0])

    # Objective function!
    def objFun(W):
        # Feed forward
        W = W.reshape((N, X.shape[0] + Y.shape[0]))
        # F1 = (W[:, :X.shape[0]].dot(X))
        # F2 = (W[:, X.shape[0]:].dot(Y))
        F1 = (X.T.dot(W[:, :X.shape[0]].T)).T
        F2 = (Y.T.dot(W[:, X.shape[0]:].T)).T
        F = F1*F2
        Fs = np.sqrt(F**2 + 1e-8)    NFs, L2Fs = l2row(Fs)
        Fhat, L2Fn = l2row(NFs.T)
        # Compute objective function
        # Backprop through each feedforward step
        DeltaW = l2rowg(NFs.T, Fhat, L2Fn, np.ones(Fhat.shape))
        DeltaW = l2rowg(Fs, NFs, L2Fs, DeltaW.T)
        # DeltaW1 = (DeltaW*F2*(F/Fs)).dot(X.T)
        # DeltaW2 = (DeltaW*F1*(F/Fs)).dot(Y.T)
        DeltaW1 = X.dot((DeltaW*F2*(F/Fs)).T).T
        DeltaW2 = Y.dot((DeltaW*F1*(F/Fs)).T).T
        return Fhat.sum(), np.hstack([DeltaW1, DeltaW2]).flatten()

    # Actual optimization
    w, g = objFun(optW)
    res = minimize(objFun, optW, method='L-BFGS-B', jac=True, options={'maxiter':200})
    return res.x.reshape(N, X.shape[0] + Y.shape[0])


def feedForwardPSF(W, X, Y):
    "Feed-forward"
    # F = (W[:, :X.shape[0]].dot(X))*(W[:, Y.shape[0]:].dot(Y))
    F = (X.T.dot(W[:, :X.shape[0]].T))*(Y.T.dot(W[:, Y.shape[0]:].T))
    Fs = np.sqrt(F**2 + 1e-8)
    NFs = l2row(Fs)[0]
    return l2row(NFs.T)[0].T
