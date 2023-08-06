import pytest
import numpy as np

from ..statistics import *

def test_anova_n():
    y = np.linspace(0, 10, 11)
    assert anova_n(y) == anova_one(y)

def test_anova():
    y = np.linspace(0, 10, 11)
    assert anova(y) == anova(y, method='n')
    assert anova(y) == anova_n(y)
