"""
Statistics

Routines in this module:

mad(a)
"""

import numpy as np

def mad(a: np.ndarray) -> np.ndarray:
    """
    Compute the mean absolute deviation of an array or matrix.

    Parameters
    ----------
    a : array_like
        Input array

    Returns
    -------
    out : float
        The mean absolute deviation.

    References
    ----------
    https://en.wikipedia.org/wiki/Average_absolute_deviation

    """

    a = np.asarray(a)
    out = np.mean(np.absolute(a - np.mean(a)))
    return out

def gaussian(a: np.ndarray, mu: float=0, sigma: float=1) -> np.ndarray:
    """
    Construct a Gaussian for a given range of values with a specified mean and
    standard deviation.

    Parameters
    ----------
    a : array_like
        Input array
    mu : float, optional
        Mean value of Gaussian
    sigma : float, optional
        Standard deviation of Gaussian

    Returns
    -------
    out : array_like
        Gaussian array corresponding to input array

    References
    ----------
    https://en.wikipedia.org/wiki/Normal_distribution

    https://www.maa.org/sites/default/files/pdf/upload_library/22/
    Allendoerfer/stahl96.pdf

    """

    a = np.asarray(a)
    out = np.exp(-1*(a - mu)**2 / (2*sigma**2)) / np.sqrt(2*np.pi*sigma**2)
    return out

def cdf(a: np.ndarray, normalize: bool=True) -> np.ndarray:
    """
    Construct a Cumulative Distribution Function from a given distribution.
    Normalizing the CDF will put it on a range from [0, 1].

    Parameters
    ----------
    a : array_like
        Input distribution
    normalize : boolean, optional
        If True, the CDF will be normalized.

    Return
    ------
    out : array_like
        Cumulative distribution function

    Notes
    -----
    The Cumulative Distribution Function is the integral of the Probability
    Distribution Function. The area under the curve in a PDF should sum to 1.
    By default this function will re-normalize, to verify that the maximum
    value in the CDF is 1.

    References
    ----------
    https://en.wikipedia.org/wiki/Cumulative_distribution_function

    """

    a = np.asarray(a)
    out = np.cumsum(a)
    if normalize == True:
        out = np.divide(out, out[-1])
    return out

def nearest_index(a: np.ndarray, value: float) -> int:
    """
    Find the index with the closest value to the specified value.

    Parameters
    ----------
    a : array_like
        Input array
    value : float
        Specified value

    Returns
    -------
    out : int
        The index of the input array with the closest value to value

    References
    ----------
    https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array

    """

    a = np.asarray(a)
    out = (np.absolute(a - value)).argmin()
    return out

def probability(a: np.ndarray, b: np.ndarray, lower: float=None, upper: float=None, inclusive: bool=True, normalized: bool=False) -> float:
    """
    Calculate the probability of an area within a distribution given by the
    lower and upper limits. By default, the area is inclusive of the given
    limits and will check that the distribution is a PDF, meaning that the
    total area sums to 1.

    Parameters
    ----------
    a : array_like
        Input positional values of distribution
    b : array_like
        Input distribution
    lower : float, optional
        The lower limit of the probability range in the distribution. If it is
        not provided, then the lowermost value in `a` will be used.
    upper : float, optional
        The upper limit of the probability range in the distribution. If it is
        not provided, then the uppermost value in `a` will be used.
    inclusive : boolean, optional
        If True, then the lower and upper limits are inclusive; if False, then
        they are exclusive. True by default.
    normalized : boolean, optional
        If True, then the provided distribution is a PDF. If False, then the
        distribution will be normalized to a PDF. False by default.

    Returns
    -------
    out : float
        The probability of the region within the lower and upper bounds in a
        distribution.

    References
    ----------
    https://en.wikipedia.org/wiki/Probability_density_function#Absolutely_continuous_univariate_distributions

    """

    # Sort a
    a = np.asarray(a)
    a = np.sort(a)
    
    # Find lower and upper indices
    lower_ind = int(np.argwhere(a == a[nearest_ind(a, lower)]))
    upper_ind = int(np.argwhere(a == a[nearest_ind(a, upper)]))

    if inclusize == False:
        # If not inclusive and the current value at lower_ind or upper_ind is
        # the inclusive value, then shift the index to the left or right.
        if a[lower_ind] == lower:
            lower_ind += 1
        if a[upper_ind] == upper:
            upper_ind -= 1

    # Normalize the distribution
    if normalized == False:
        b /= np.sum(b)

    # Calculate the probability
    out = np.absolute(b[upper_ind] - b[lower_ind])
    return out

def covariance(a: np.ndarray) -> np.ndarray:
    """
    Returns the covariance matrix of a matrix or list of vectors. Contains the
    variances and covariances of the given vectors. The main diagonal is the
    variances and the upper- and lower-triangles are the covariances.
    
    Parameters
    ----------
    a : array_like
        If np.ndarray.shape == 2, then each column is treated as a separate
        vector. If list or tuple of vectors, then each item is a vector.
    
    Returns
    -------
    out : array_like
        A square matrix of shape [N, N], where N is the length of the list or
        tuple input or the number of columns in if the input is a 2D NumPy
        array. Contains the variances and covariances of the given
        vectors. The main diagonal is the variances and the upper- and lower-
        triangles are the covariances.
    
    References
    ----------
    http://stattrek.com/matrix-algebra/covariance-matrix.aspx
    
    https://en.wikipedia.org/wiki/Covariance_matrix
    
    """
    
    a = np.asarray(a).T
    N = a.shape[0]
    A = a - np.mean(a, axis=0)
    return A.T@A/N

def correlation(a: np.ndarray) -> np.ndarray:
    """
    Returns the correlation matrix of a matrix or list of vectors. The main
    diagonal is the correlation of a vector with itself and should be 1. The
    upper- and lower- triangles are the Pearson correlation coefficients.
    
    Parameters
    ----------
    a : array_like
        If np.ndarray.shape == 2, then each column is treated as a separate
        vector. If list or tuple of vectors, then each item is a vector.
    
    Returns
    -------
    out : array_like
        A square matrix of shape [N, N], where N is the length of the list or
        tuple input or the number of columns in if the input is a 2D NumPy
        array. The main diagonal is the correlation of a vector with itself and
        should be 1. The upper- and lower- triangles are the Pearson
        correlation coefficients.
        
    """
    # Source:
    # https://en.wikipedia.org/wiki/Covariance_matrix#Correlation_matrix
    cov = covariance(a)
    diag = np.diag(np.diag(cov)**-0.5, 0)
    return diag@cov@diag

