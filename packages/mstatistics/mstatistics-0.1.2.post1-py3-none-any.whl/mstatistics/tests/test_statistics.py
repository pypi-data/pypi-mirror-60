import pytest
import numpy as np

from ..statistics import *

def test_mad():
    assert mad(np.arange(1, 6)) - 6/5 <= 1e-5
    assert mad(np.arange(1, 6)) == 6/5
    assert mad([1, 2, 3, 4, 5]) == 6/5

def test_gaussian():
    assert np.argmax(gaussian(np.linspace(-100, 100, 101))) == 50

def test_cdf():
    assert cdf(np.arange(1, 11), normalize=False)[-1] == 10/2*(10 + 1)
    assert cdf(np.arange(1, 11), normalize=True)[-1] == 1

def test_nearest_index():
    assert nearest_index(np.arange(0, 5), -1) == 0
    assert nearest_index(np.arange(0, 5), 0) == 0
    assert nearest_index(np.arange(0, 5), 5) == 4
    assert nearest_index(np.arange(0, 5), 4) == 4

def test_covariance():
    assert np.all(covariance([np.arange(0, 5),
                              np.arange(0, 5)]) == 2*np.ones([2, 2]))
    assert np.all(covariance(np.array([np.arange(0, 5),
                                       np.arange(0, 5)])) == 2*np.ones([2, 2]))
    assert np.all(covariance([np.arange(0, 5),
                              -1*np.arange(0, 5)]) == np.array([[2, -2],
                                                                [-2, 2]]))

def test_correlation():
    assert np.allclose(correlation([np.arange(0, 5),
                                    np.arange(0, 5)]), np.ones([2, 2]))
    assert np.allclose(correlation(np.array([np.arange(0, 5),
                                             np.arange(0, 5)])), \
                       np.ones([2, 2]))
    assert np.allclose(correlation([np.arange(0, 5),
                                    -1*np.arange(0, 5)]), \
                       np.array([[1, -1], [-1, 1]]))

