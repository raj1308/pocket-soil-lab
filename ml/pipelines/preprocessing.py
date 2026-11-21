"""Spectral preprocessing transformers, scikit-learn Pipeline-compatible.

SNV and Savitzky-Golay are row-wise (per-spectrum) operations with no
parameters to fit from training data, so they're leak-proof by construction.
Only StandardScaler (used after these, where applicable) is fit on training
data alone, as required.
"""
import numpy as np
from scipy.signal import savgol_filter
from sklearn.base import BaseEstimator, TransformerMixin


class SNVTransformer(BaseEstimator, TransformerMixin):
    """Standard Normal Variate: per-spectrum (row-wise) mean-center and scale."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        mean = X.mean(axis=1, keepdims=True)
        std = X.std(axis=1, keepdims=True)
        std[std == 0] = 1.0
        return (X - mean) / std


class SavitzkyGolayTransformer(BaseEstimator, TransformerMixin):
    """Savitzky-Golay smoothing or derivative, applied along the wavelength axis."""

    def __init__(self, window_length: int = 11, polyorder: int = 2, deriv: int = 0):
        self.window_length = window_length
        self.polyorder = polyorder
        self.deriv = deriv

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        return savgol_filter(
            X, window_length=self.window_length, polyorder=self.polyorder, deriv=self.deriv, axis=1
        )


class SNVThenSavitzkyGolay(BaseEstimator, TransformerMixin):
    """SNV followed by an SG derivative, as a single transformer (not a nested
    Pipeline) — a Pipeline-within-Pipeline step breaks scikit-learn's internal
    clone/fit bookkeeping during cross_val_score, so this does both steps in
    one transform() call instead."""

    def __init__(self, window_length: int = 11, polyorder: int = 2, deriv: int = 1):
        self.window_length = window_length
        self.polyorder = polyorder
        self.deriv = deriv

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        snv = SNVTransformer().transform(X)
        return savgol_filter(
            snv, window_length=self.window_length, polyorder=self.polyorder, deriv=self.deriv, axis=1
        )


def build_preprocessor(name: str):
    """Returns a (name, transformer-or-None) for the named preprocessing option."""
    if name == "raw":
        return None
    if name == "snv":
        return SNVTransformer()
    if name == "sg_smooth":
        return SavitzkyGolayTransformer(window_length=11, polyorder=2, deriv=0)
    if name == "sg1_deriv":
        return SavitzkyGolayTransformer(window_length=11, polyorder=2, deriv=1)
    if name == "snv_sg1":
        return SNVThenSavitzkyGolay(window_length=11, polyorder=2, deriv=1)
    raise ValueError(f"Unknown preprocessing option: {name}")
