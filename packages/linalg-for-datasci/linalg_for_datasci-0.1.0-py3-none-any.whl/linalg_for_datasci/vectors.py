import numpy as np

# Experimental Vectors and Sampling Vectors from Functions


def discrete_sample(n, f):
    xs = np.arange(n)
    return xs, f(xs)


def our_sin(xs):
    scaled_xs = 2 * np.pi * (xs / len(xs))  # SOLUTION
    return np.sin(scaled_xs)


def our_sin_with_freq(xs, freq):
    scaled_xs = freq * 2 * np.pi * (xs / len(xs))  # SOLUTION
    return np.sin(scaled_xs)


def exp_scaled(xs, scale):
    scaled_xs = xs / scale
    return np.exp(-xs)


def apply_multiplicative_noise(v, eps=0.05):
    n = len(v)
    noise = 1 + ((np.random.rand(n) - 0.5) * eps)
    return np.multiply(v, noise)


# QR decompositions by hand
def make_sin(f, n=50):
    """
    Returns a vector that contains a length-n sinusoid with frequency f
    """
    xs = np.arange(n)
    xs = f * 2 * np.pi * (xs / n)
    return np.sin(xs)


# PCA of discretized functions

# Let's generate these vectors in code

from math import pi

# Some parameters; leave these alone
d = 20  # number of features
eps = 0.1
xvals = np.linspace(0, 2 * pi, d)
n = 20

sin_funcs = np.array([np.sin(xvals) for _ in range(n)]).T + np.random.randn(d, n) * eps
exp_funcs = (
    np.array([np.exp(-xvals / (2 * pi)) for _ in range(n)]).T
    + np.random.randn(d, n) * eps
)
rand_funcs = np.array([np.random.rand(d) * 2 - 1 for _ in range(n)]).T

n = 3 * n  # number of observations

X = np.hstack((sin_funcs, exp_funcs, rand_funcs))
