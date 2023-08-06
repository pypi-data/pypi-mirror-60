"""
Regression

Routines in this module:

sst(a)
"""

import numpy as np

def sst(a: np.ndarray) -> np.ndarray:
    """
    Total sum of squares

    Parameters
    ----------
    a : array_like
        N-dimensional matrix

    Returns
    -------
    out : array_like
        Total sum of squares

    Notes
    -----

    SS_total = sum((Y - mean(Y))**2)

    References
    ----------

    https://en.wikipedia.org/wiki/Total_sum_of_squares
    http://statweb.stanford.edu/~susan/courses/s141/exanova.pdf
    http://www.real-statistics.com/two-way-anova/anova-more-than-two-factors/

    """

    a = np.asarray(a)
    out = np.sum((a - np.mean(a))**2)
    return out

def ssb(a: np.ndarray) -> np.ndarray:
    """
    Sum of squares between groups

    Parameters
    ----------
    a : array_like
        N-dimensional matrix

    Returns
    -------
    out : array_like
        Sum of squares between groups

    Notes
    -----

    SS_between = n * sum((mean(Y, axis=1) - mean(Y))**2)

    References
    ----------

    """

    a = np.asarray(a)
    out = a.size * np.sum(np.mean(a, axis=1) - np.mean(a))**2 # should n be a.size or a.shape[1]?
    return out

def ssw(a: np.ndarray) -> np.ndarray:
    return

def ss(a: np.ndarray, method='total': str) -> np.ndarray:
    """
    Sum of squares.

    Parameters
    ----------

    Returns
    -------
    out : float
        The sum of squares

    Notes
    -----
    Sum of squares is the summation of the square of the differences between
    a vector and the mean value.

    SS = sum((Y - mean(Y))**2)

    The objective in a least squares regression is minimizing the sum of
    squares.
    
    There are different types of SS and different naming conventions, such as
    the total SS (shown above), the SS within a group, the SS between groups,
    the SS from interactions of groups, the explained SS, and the residual SS.

    SS_total = sum((Y - mean(Y))**2)

    SS_between = n * sum((mean(Y, axis=1) - mean(Y))**2)

    References
    ----------

    """

    if method.lower() == 'total':
        return sst(a)
    elif method.lower() == 'between':
        return ssb(a)
    elif method.lower() == 'within':
        return ssw(a)
    else:
        raise LookupError(f'Method "{method}" not found')
    return

def anova_one(a: np.ndarray) -> np.ndarray:
    """
    One-way ANOVA test.

    Parameters
    ----------

    Returns
    -------

    Notes
    -----

    References
    ----------

    """

    print("One-way anova")
    a = np.asarray(a)
    n = a.shape[0]
    k = a.shape[1]
    N = n*k

    # Degrees of freedom between
    dfb = k - 1

    # Degrees of freedom within
    dfw = N - k

    # Degrees of freedom total
    dft = N - 1

    # Sum of squares is n*variance
    # Sum of squares between
    #ssb = (np.sum(
    #sum_y_sqrd = 
    #ssw = 
    #sst = 

    return

def anova_two(a: np.ndarray) -> np.ndarray:
    """
    Two-way ANOVA test.

    Parameters
    ----------

    Returns
    -------

    Notes
    -----

    References
    ----------

    """

    print("Two-way anova")
    return

def anova_n(a: np.ndarray) -> np.ndarray:
    """
    N-way ANOVA test.

    Parameters
    ----------

    Returns
    -------

    Notes
    -----

    References
    ----------

    """

    print("N-way anova")
    return

def anova(a: np.ndarray, method='n': str, **kwargs) -> np.ndarray:
    """
    Wrapper function for ANOVA tests. The input is re-directed to a one-way,
    two-way, or n-way ANOVA based on the provided method. By default, a n-way
    ANOVA is performed (since it is the general case).

    Parameters
    ----------

    Returns
    -------

    Notes
    -----

    References
    ----------

    """

    a = np.asarray(a)
    if method.lower() == 'one':
        out = anova_one(a)
        return out
    elif method.lower() == 'two':
        out = anova_two(a)
        return out
    elif method.lower() == 'n':
        out = anova_n(a)
        return out
    else:
        raise LookupError('Method "{}" not found'.format(method))
    return
